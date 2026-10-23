from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from supabase import Client, create_client

from app.outreach_accepted_pool_store import (
    get_accepted_pool,
)
from app.outreach_campaign_identity import (
    campaign_id_for_name, connect_batch_label, connect_batch_name,
)
from app.settings import load_settings
from app.outreach_message_company import attach_target_companies


MESSAGE_BATCH_TABLE = (
    "outreach_message_batches"
)

MESSAGE_TARGET_TABLE = (
    "outreach_message_targets"
)

CONNECT_TARGET_TABLE = (
    "outreach_job_targets"
)

CONNECT_JOB_TABLE = (
    "outreach_jobs"
)

LOCAL_TIMEZONE = ZoneInfo(
    "Asia/Ho_Chi_Minh"
)


class OutreachMessagePreparationStoreError(
    RuntimeError
):
    pass


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _safe_text(
    value,
) -> str:
    return str(
        value
        or ""
    ).strip()


# =========================================================
# SUPABASE
# =========================================================

def get_outreach_supabase_client() -> Client:
    """
    Backend-safe client.

    This preparation layer only reads/writes Supabase.
    It does NOT import or run LinkedIn browser code.
    """
    settings = load_settings()

    if not settings.outreach_supabase_url:
        raise OutreachMessagePreparationStoreError(
            "Missing OUTREACH_SUPABASE_URL."
        )

    if not settings.outreach_supabase_secret_key:
        raise OutreachMessagePreparationStoreError(
            "Missing OUTREACH_SUPABASE_SECRET_KEY."
        )

    return create_client(
        settings.outreach_supabase_url,
        settings.outreach_supabase_secret_key,
    )


# =========================================================
# BATCH CODE
# =========================================================

def _build_batch_code(
    *,
    client: Client,
) -> str:
    """
    Format:
        MSG-YYYYMMDD-01
        MSG-YYYYMMDD-02
        ...
    """
    now = datetime.now(
        LOCAL_TIMEZONE
    )

    date_code = now.strftime(
        "%Y%m%d"
    )

    prefix = (
        f"MSG-{date_code}"
    )

    response = (
        client.table(
            MESSAGE_BATCH_TABLE
        )
        .select(
            "batch_code"
        )
        .like(
            "batch_code",
            f"{prefix}-%",
        )
        .execute()
    )

    rows = list(
        response.data
        or []
    )

    highest_sequence = 0

    for row in rows:
        batch_code = _safe_text(
            row.get(
                "batch_code"
            )
        )

        if not batch_code:
            continue

        try:
            sequence = int(
                batch_code.rsplit(
                    "-",
                    1,
                )[1]
            )

        except (
            IndexError,
            ValueError,
        ):
            continue

        highest_sequence = max(
            highest_sequence,
            sequence,
        )

    return (
        f"{prefix}-"
        f"{highest_sequence + 1:02d}"
    )


# =========================================================
# ALREADY PREPARED PROSPECTS
# =========================================================

def _load_prepared_prospect_ids(
    *,
    client: Client,
) -> set[str]:
    """
    Profiles already snapshot into a currently prepared message
    batch are excluded from future Prepare All runs.

    This prevents:
        Batch #1 -> Prospect A
        Batch #2 -> Prospect A again

    before the messaging phase has even started.
    """
    response = (
        client.table(
            MESSAGE_TARGET_TABLE
        )
        .select(
            "prospect_id,status"
        )
        .eq(
            "status",
            "prepared",
        )
        .execute()
    )

    rows = list(
        response.data
        or []
    )

    return {
        _safe_text(
            row.get(
                "prospect_id"
            )
        )
        for row in rows
        if _safe_text(
            row.get(
                "prospect_id"
            )
        )
    }


# =========================================================
# ELIGIBLE RECIPIENTS
# =========================================================

def get_message_preparation_candidates(
    *,
    client: Client | None = None,
) -> dict:
    """
    Build the exact recipient set that would be snapshotted now.

    Eligibility:
    - Acceptance Pool item exists
    - message_bucket == not_sent
    - prospect_id exists
    - assigned_account_id exists
    - linkedin_url exists
    - not already in another prepared message batch

    This function does NOT create a batch.
    """
    active_client = (
        client
        if client is not None
        else get_outreach_supabase_client()
    )

    accepted_pool = (
        get_accepted_pool(
            client=active_client
        )
    )

    pool_items = (
        accepted_pool.get(
            "items"
        )
        or []
    )

    already_prepared = (
        _load_prepared_prospect_ids(
            client=active_client
        )
    )

    candidates: list[dict] = []

    for item in pool_items:
        if (
            _safe_text(
                item.get(
                    "message_bucket"
                )
            ).lower()
            != "not_sent"
        ):
            continue

        prospect_id = _safe_text(
            item.get(
                "prospect_id"
            )
        )

        source_target_id = _safe_text(
            item.get(
                "target_id"
            )
        )

        account_id = _safe_text(
            item.get(
                "assigned_account_id"
            )
        )

        linkedin_url = _safe_text(
            item.get(
                "linkedin_url"
            )
        )

        if (
            not prospect_id
            or not source_target_id
            or not account_id
            or not linkedin_url
        ):
            continue

        if prospect_id in already_prepared:
            continue

        candidates.append(
            {
                "prospect_id": (
                    prospect_id
                ),
                "source_target_id": (
                    source_target_id
                ),
                "connect_batch_id": _safe_text(item.get("connect_batch_id")),
                "campaign_id": _safe_text(item.get("campaign_id")),
                "campaign_name": _safe_text(item.get("display_name")),
                "assigned_account_id": (
                    account_id
                ),
                "linkedin_url": (
                    linkedin_url
                ),
                "normalized_url": _safe_text(
                    item.get(
                        "normalized_url"
                    )
                ),
                "accepted_at": (
                    item.get(
                        "accepted_at"
                    )
                ),
            }
        )

    return {
        "count": len(
            candidates
        ),
        "items": candidates,
    }


# =========================================================
# PREPARE BATCH
# =========================================================

def _create_prepared_batch_from_candidates(
    *,
    candidates: list[dict],
    client: Client,
) -> dict:
    if not candidates:
        return {
            "created": False,
            "reason": "no_eligible_recipients",
            "batch": None,
            "target_count": 0,
        }

    batch_code = _build_batch_code(
        client=client
    )

    now = _utc_now()

    batch_response = (
        client.table(
            MESSAGE_BATCH_TABLE
        )
        .insert(
            {
                "batch_code": batch_code,
                "status": "prepared",
                "target_count": 0,
                "created_at": now,
                "updated_at": now,
            }
        )
        .execute()
    )

    batch_rows = list(
        batch_response.data
        or []
    )

    if not batch_rows:
        raise OutreachMessagePreparationStoreError(
            "Could not create message preparation batch."
        )

    batch = batch_rows[0]
    batch_id = _safe_text(
        batch.get("id")
    )

    if not batch_id:
        raise OutreachMessagePreparationStoreError(
            "Created message batch has no id."
        )

    target_rows = [
        {
            "batch_id": batch_id,
            "prospect_id": item["prospect_id"],
            "source_target_id": item["source_target_id"],
            "assigned_account_id": item["assigned_account_id"],
            "linkedin_url": item["linkedin_url"],
            "normalized_url": (
                item["normalized_url"] or None
            ),
            "status": "prepared",
            "created_at": now,
            "updated_at": now,
        }
        for item in candidates
    ]

    try:
        target_response = (
            client.table(
                MESSAGE_TARGET_TABLE
            )
            .insert(
                target_rows
            )
            .execute()
        )

        inserted_targets = list(
            target_response.data
            or []
        )

        inserted_count = len(
            inserted_targets
        )

        if inserted_count != len(
            target_rows
        ):
            raise OutreachMessagePreparationStoreError(
                "Prepared target insert count mismatch: "
                f"expected {len(target_rows)}, "
                f"got {inserted_count}."
            )

        (
            client.table(
                MESSAGE_BATCH_TABLE
            )
            .update(
                {
                    "target_count": inserted_count,
                    "updated_at": _utc_now(),
                }
            )
            .eq(
                "id",
                batch_id,
            )
            .execute()
        )

    except Exception:
        try:
            (
                client.table(
                    MESSAGE_BATCH_TABLE
                )
                .delete()
                .eq(
                    "id",
                    batch_id,
                )
                .execute()
            )
        except Exception:
            pass

        raise

    batch["target_count"] = inserted_count
    source = candidates[0]
    batch["campaign_id"] = _safe_text(source.get("campaign_id"))
    batch["campaign_name"] = _safe_text(source.get("campaign_name"))
    batch["source_connect_batch_id"] = _safe_text(source.get("connect_batch_id"))

    return {
        "created": True,
        "reason": None,
        "batch": batch,
        "target_count": inserted_count,
    }


def _prepare_batches_by_connect_source(*, candidates: list[dict], client: Client) -> dict:
    """Keep each prepared message batch tied to exactly one Connect batch."""
    if not candidates:
        return {"created": False, "reason": "no_eligible_recipients", "batch": None,
                "batches": [], "target_count": 0}

    groups: dict[str, list[dict]] = {}
    for candidate in candidates:
        source_id = _safe_text(candidate.get("connect_batch_id"))
        if not source_id:
            raise OutreachMessagePreparationStoreError(
                "A recipient has no source Connect batch. Refresh the accepted pool before preparing."
            )
        groups.setdefault(source_id, []).append(candidate)

    batches: list[dict] = []
    total = 0
    for group in groups.values():
        try:
            result = _create_prepared_batch_from_candidates(candidates=group, client=client)
        except Exception as exc:
            if batches:
                raise OutreachMessagePreparationStoreError(
                    f"Prepared {len(batches)} source batch(es) before an error. "
                    "Refresh Messages before retrying; already prepared recipients will be skipped."
                ) from exc
            raise
        batches.append(result["batch"])
        total += result["target_count"]

    return {"created": True, "reason": None, "batch": batches[0],
            "batches": batches, "target_count": total}


# =========================================================
# PREPARE ALL
# =========================================================

def prepare_all_unsent_accepted(
    *,
    client: Client | None = None,
) -> dict:
    active_client = (
        client
        if client is not None
        else get_outreach_supabase_client()
    )

    candidate_result = (
        get_message_preparation_candidates(
            client=active_client
        )
    )

    return _prepare_batches_by_connect_source(
        candidates=list(
            candidate_result.get("items")
            or []
        ),
        client=active_client,
    )


# =========================================================
# PREPARE SELECTED
# =========================================================

def prepare_selected_unsent_accepted(
    *,
    prospect_ids: list[str],
    client: Client | None = None,
) -> dict:
    active_client = (
        client
        if client is not None
        else get_outreach_supabase_client()
    )

    cleaned_ids: list[str] = []
    seen: set[str] = set()

    for value in (
        prospect_ids
        or []
    ):
        prospect_id = _safe_text(value)

        if (
            not prospect_id
            or prospect_id in seen
        ):
            continue

        seen.add(prospect_id)
        cleaned_ids.append(prospect_id)

    if not cleaned_ids:
        raise OutreachMessagePreparationStoreError(
            "At least one prospect_id is required."
        )

    candidate_result = (
        get_message_preparation_candidates(
            client=active_client
        )
    )

    candidates = list(
        candidate_result.get("items")
        or []
    )

    candidate_by_id = {
        _safe_text(item.get("prospect_id")): item
        for item in candidates
        if _safe_text(item.get("prospect_id"))
    }

    missing_ids = [
        prospect_id
        for prospect_id in cleaned_ids
        if prospect_id not in candidate_by_id
    ]

    if missing_ids:
        raise OutreachMessagePreparationStoreError(
            "Some selected recipients are no longer eligible. "
            "Refresh Accepted Pool and select again."
        )

    selected_candidates = [
        candidate_by_id[prospect_id]
        for prospect_id in cleaned_ids
    ]

    return _prepare_batches_by_connect_source(
        candidates=selected_candidates,
        client=active_client,
    )


def _chunked_values(
    values: list[str],
    size: int = 200,
):
    for start in range(
        0,
        len(values),
        size,
    ):
        yield values[
            start:start + size
        ]


def _attach_source_connect_ids_to_batches(
    *,
    client: Client,
    batches: list[dict],
) -> list[dict]:
    """
    Attach original Connect Job identity to each Message Batch.

    Existing relations only:
        outreach_message_batches.id
        -> outreach_message_targets.batch_id
        -> outreach_message_targets.source_target_id
        -> outreach_job_targets.id
        -> outreach_job_targets.job_id
        -> outreach_jobs.job_code

    A Message Batch may contain recipients from multiple Connect Jobs,
    therefore source_connect_ids is always returned as a list.
    """

    if not batches:
        return batches

    batch_ids = [
        _safe_text(
            batch.get("id")
        )
        for batch in batches
        if _safe_text(
            batch.get("id")
        )
    ]

    target_rows: list[dict] = []

    for chunk in _chunked_values(
        batch_ids
    ):
        offset = 0
        while True:
            response = (
                client
                .table(MESSAGE_TARGET_TABLE)
                .select("batch_id,source_target_id")
                .in_("batch_id", chunk)
                .order("id")
                .range(offset, offset + 999)
                .execute()
            )
            rows = list(response.data or [])
            target_rows.extend(rows)
            if len(rows) < 1000:
                break
            offset += 1000

    source_target_ids = list(
        dict.fromkeys(
            _safe_text(
                row.get(
                    "source_target_id"
                )
            )
            for row in target_rows
            if _safe_text(
                row.get(
                    "source_target_id"
                )
            )
        )
    )

    connect_target_by_id: dict[
        str,
        dict,
    ] = {}

    for chunk in _chunked_values(
        source_target_ids
    ):
        response = (
            client
            .table(
                CONNECT_TARGET_TABLE
            )
            .select(
                "id,job_id"
            )
            .in_(
                "id",
                chunk,
            )
            .execute()
        )

        for row in list(
            response.data
            or []
        ):
            target_id = _safe_text(
                row.get("id")
            )

            if target_id:
                connect_target_by_id[
                    target_id
                ] = dict(row)

    job_ids = list(
        dict.fromkeys(
            _safe_text(
                row.get("job_id")
            )
            for row in connect_target_by_id.values()
            if _safe_text(
                row.get("job_id")
            )
        )
    )

    job_code_by_id: dict[str, dict[str, str]] = {}

    for chunk in _chunked_values(
        job_ids
    ):
        response = (
            client
            .table(
                CONNECT_JOB_TABLE
            )
            .select(
                "*"
            )
            .in_(
                "id",
                chunk,
            )
            .execute()
        )

        for row in list(
            response.data
            or []
        ):
            job_id = _safe_text(
                row.get("id")
            )

            if job_id:
                job_code_by_id[job_id] = {
                    "code": _safe_text(row.get("job_code")),
                    "display_name": _safe_text(row.get("display_name")),
                    "batch_name": connect_batch_name(row.get("batch_name"), row.get("created_at")),
                    "batch_label": connect_batch_label(
                        row.get("batch_name"), row.get("display_name"), row.get("created_at")
                    ),
                    "campaign_id": campaign_id_for_name(
                        row.get("display_name"), connect_batch_id=job_id
                    ),
                }

    source_target_ids_by_batch: dict[
        str,
        list[str],
    ] = {}

    for row in target_rows:
        batch_id = _safe_text(
            row.get("batch_id")
        )

        source_target_id = _safe_text(
            row.get(
                "source_target_id"
            )
        )

        if (
            not batch_id
            or not source_target_id
        ):
            continue

        source_target_ids_by_batch.setdefault(
            batch_id,
            [],
        ).append(
            source_target_id
        )

    enriched: list[dict] = []

    for raw_batch in batches:
        batch = dict(
            raw_batch
        )

        batch_id = _safe_text(
            batch.get("id")
        )

        source_connect_ids: list[
            dict
        ] = []

        seen_job_ids: set[
            str
        ] = set()

        for source_target_id in (
            source_target_ids_by_batch.get(
                batch_id,
                [],
            )
        ):
            connect_target = (
                connect_target_by_id.get(
                    source_target_id
                )
                or {}
            )

            job_id = _safe_text(
                connect_target.get(
                    "job_id"
                )
            )

            if (
                not job_id
                or job_id in seen_job_ids
            ):
                continue

            seen_job_ids.add(
                job_id
            )

            source_connect_ids.append(
                {
                    "id": job_id,
                    "connect_batch_id": job_id,
                    "code": (
                        job_code_by_id.get(job_id, {}).get("code", "")
                    ),
                    "display_name": job_code_by_id.get(job_id, {}).get(
                        "display_name", ""
                    ),
                    "batch_name": job_code_by_id.get(job_id, {}).get("batch_name", ""),
                    "batch_label": job_code_by_id.get(job_id, {}).get("batch_label", ""),
                    "campaign_id": job_code_by_id.get(job_id, {}).get(
                        "campaign_id", ""
                    ),
                }
            )

        source_connect_ids.sort(
            key=lambda item: (
                _safe_text(
                    item.get("code")
                )
                or _safe_text(
                    item.get("id")
                )
            ),
            reverse=True,
        )

        batch[
            "source_connect_ids"
        ] = source_connect_ids
        campaign_ids = {item["campaign_id"] for item in source_connect_ids}
        batch["campaign_id"] = next(iter(campaign_ids)) if len(campaign_ids) == 1 else None
        batch["campaign_name"] = (
            source_connect_ids[0]["display_name"] if len(campaign_ids) == 1 else None
        )
        batch["source_connect_batch_id"] = (
            source_connect_ids[0]["connect_batch_id"] if len(source_connect_ids) == 1 else None
        )
        batch["source_connect_batch_code"] = (
            source_connect_ids[0]["code"] if len(source_connect_ids) == 1 else None
        )
        batch["mixed_sources"] = len(source_connect_ids) > 1

        enriched.append(
            batch
        )

    return enriched


# =========================================================
# PREPARED BATCH READ API
# =========================================================

def list_prepared_message_batches(
    *,
    client: Client | None = None,
    limit: int = 50,
) -> list[dict]:
    """
    List recent message-preparation batches.

    Preparation phase only:
    this does NOT trigger messaging.
    """
    active_client = (
        client
        if client is not None
        else get_outreach_supabase_client()
    )

    safe_limit = max(
        1,
        min(
            int(limit),
            100,
        ),
    )

    response = (
        active_client.table(
            MESSAGE_BATCH_TABLE
        )
        .select(
            (
                "id,"
                "batch_code,"
                "status,"
                "target_count,"
                "created_at,"
                "updated_at"
            )
        )
        .order(
            "created_at",
            desc=True,
        )
        .limit(
            safe_limit
        )
        .execute()
    )

    batches = list(
        response.data
        or []
    )

    return (
        _attach_source_connect_ids_to_batches(
            client=active_client,
            batches=batches,
        )
    )


def _attach_connect_identity_to_targets(*, client: Client, targets: list[dict]) -> None:
    """Follow the persisted source_target_id link back to the Connect run."""
    source_ids = list(dict.fromkeys(
        _safe_text(target.get("source_target_id"))
        for target in targets
        if _safe_text(target.get("source_target_id"))
    ))
    source_to_job: dict[str, str] = {}
    for chunk in _chunked_values(source_ids):
        response = (
            client.table(CONNECT_TARGET_TABLE)
            .select("id,job_id")
            .in_("id", chunk)
            .execute()
        )
        for row in list(response.data or []):
            source_to_job[_safe_text(row.get("id"))] = _safe_text(row.get("job_id"))

    job_ids = list(dict.fromkeys(job_id for job_id in source_to_job.values() if job_id))
    jobs: dict[str, dict] = {}
    for chunk in _chunked_values(job_ids):
        response = (
            client.table(CONNECT_JOB_TABLE)
            .select("id,job_code,display_name")
            .in_("id", chunk)
            .execute()
        )
        for row in list(response.data or []):
            jobs[_safe_text(row.get("id"))] = row

    for target in targets:
        connect_batch_id = source_to_job.get(_safe_text(target.get("source_target_id")), "")
        job = jobs.get(connect_batch_id, {})
        campaign_name = _safe_text(job.get("display_name"))
        target["connect_batch_id"] = connect_batch_id
        target["connect_batch_code"] = _safe_text(job.get("job_code"))
        target["campaign_id"] = campaign_id_for_name(
            campaign_name, connect_batch_id=connect_batch_id
        )
        target["campaign_name"] = campaign_name


def get_prepared_message_batch(
    batch_id: str,
    *,
    client: Client | None = None,
) -> dict | None:
    """
    Load one prepared batch plus its frozen recipient snapshot.
    """
    active_client = (
        client
        if client is not None
        else get_outreach_supabase_client()
    )

    cleaned_batch_id = _safe_text(
        batch_id
    )

    if not cleaned_batch_id:
        raise OutreachMessagePreparationStoreError(
            "Missing message batch id."
        )

    batch_response = (
        active_client.table(
            MESSAGE_BATCH_TABLE
        )
        .select(
            (
                "id,"
                "batch_code,"
                "status,"
                "target_count,"
                "message_template,"
                "created_at,"
                "updated_at"
            )
        )
        .eq(
            "id",
            cleaned_batch_id,
        )
        .limit(
            1
        )
        .execute()
    )

    batch_rows = list(
        batch_response.data
        or []
    )

    if not batch_rows:
        return None

    target_response = (
        active_client.table(
            MESSAGE_TARGET_TABLE
        )
        .select(
            (
                "id,"
                "batch_id,"
                "prospect_id,"
                "source_target_id,"
                "assigned_account_id,"
                "linkedin_url,"
                "normalized_url,"
                "status,"
                "created_at,"
                "updated_at"
            )
        )
        .eq(
            "batch_id",
            cleaned_batch_id,
        )
        .order(
            "created_at",
            desc=False,
        )
        .execute()
    )

    batch = dict(
        batch_rows[0]
    )

    targets = [dict(row) for row in list(target_response.data or [])]
    attach_target_companies(targets, client=active_client)
    _attach_connect_identity_to_targets(client=active_client, targets=targets)
    batch["targets"] = targets

    sources = {(target["connect_batch_id"], target["connect_batch_code"],
                target["campaign_id"], target["campaign_name"])
               for target in targets if target.get("connect_batch_id")}
    batch["source_connect_ids"] = [
        {"id": source_id, "connect_batch_id": source_id, "code": code,
         "campaign_id": campaign_id, "display_name": name}
        for source_id, code, campaign_id, name in sorted(sources)
    ]
    campaign_ids = {source[2] for source in sources}
    batch["campaign_id"] = next(iter(campaign_ids)) if len(campaign_ids) == 1 else None
    batch["campaign_name"] = next(iter(sources))[3] if len(campaign_ids) == 1 else None
    batch["source_connect_batch_id"] = next(iter(sources))[0] if len(sources) == 1 else None
    batch["source_connect_batch_code"] = next(iter(sources))[1] if len(sources) == 1 else None
    batch["mixed_sources"] = len(sources) > 1

    return batch


def get_campaign_message_template_for_batch(
    batch_id: str,
    *,
    client: Client | None = None,
) -> dict:
    """Find the latest saved template from any batch in this campaign."""
    active_client = client if client is not None else get_outreach_supabase_client()
    batch = get_prepared_message_batch(batch_id, client=active_client)
    if batch is None:
        raise OutreachMessagePreparationStoreError("Message batch not found.")

    campaign_id = _safe_text(batch.get("campaign_id"))
    result = {
        "campaign_id": campaign_id,
        "campaign_name": _safe_text(batch.get("campaign_name")),
        "message_template": "",
        "saved_at": None,
        "can_save": (
            bool(campaign_id)
            and _safe_text(batch.get("status")).lower() == "prepared"
        ),
    }
    if not campaign_id:
        result["message_template"] = _safe_text(batch.get("message_template"))
        return result

    page_size = 50
    offset = 0
    best_saved_at = datetime.min.replace(tzinfo=timezone.utc)

    def parse_timestamp(value) -> datetime:
        try:
            parsed = datetime.fromisoformat(_safe_text(value).replace("Z", "+00:00"))
            return parsed.astimezone(timezone.utc)
        except (TypeError, ValueError):
            return datetime.min.replace(tzinfo=timezone.utc)

    while True:
        response = (
            active_client.table(MESSAGE_BATCH_TABLE)
            .select("id,message_template,status,queued_at,updated_at")
            .neq("message_template", "")
            .order("updated_at", desc=True)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        rows = list(response.data or [])
        if not rows:
            break
        for candidate in _attach_source_connect_ids_to_batches(
            client=active_client, batches=rows
        ):
            if _safe_text(candidate.get("campaign_id")) == campaign_id:
                saved_at = (
                    candidate.get("updated_at")
                    if _safe_text(candidate.get("status")).lower() == "prepared"
                    else candidate.get("queued_at") or candidate.get("updated_at")
                )
                parsed_saved_at = parse_timestamp(saved_at)
                if parsed_saved_at > best_saved_at:
                    best_saved_at = parsed_saved_at
                    result["message_template"] = _safe_text(candidate.get("message_template"))
                    result["saved_at"] = saved_at
        if best_saved_at >= parse_timestamp(rows[-1].get("updated_at")):
            break
        if len(rows) < page_size:
            break
        offset += page_size

    return result


def save_campaign_message_template_for_batch(
    batch_id: str,
    message_template: str,
    *,
    client: Client | None = None,
) -> dict:
    """Save a campaign template on a prepared batch; newer saves win."""
    active_client = client if client is not None else get_outreach_supabase_client()
    batch = get_prepared_message_batch(batch_id, client=active_client)
    if batch is None:
        raise OutreachMessagePreparationStoreError("Message batch not found.")
    if _safe_text(batch.get("status")).lower() != "prepared":
        raise OutreachMessagePreparationStoreError("Only prepared batches can save a template.")
    campaign_id = _safe_text(batch.get("campaign_id"))
    if not campaign_id:
        raise OutreachMessagePreparationStoreError(
            "This batch has no single campaign; its template cannot be shared."
        )
    cleaned_template = _safe_text(message_template)
    if not cleaned_template:
        raise OutreachMessagePreparationStoreError("Message template cannot be empty.")

    saved_at = _utc_now()
    response = (
        active_client.table(MESSAGE_BATCH_TABLE)
        .update({"message_template": cleaned_template, "updated_at": saved_at})
        .eq("id", _safe_text(batch_id))
        .eq("status", "prepared")
        .execute()
    )
    if not response.data:
        raise OutreachMessagePreparationStoreError(
            "Could not save template; this batch may no longer be prepared."
        )
    return {
        "campaign_id": campaign_id,
        "campaign_name": _safe_text(batch.get("campaign_name")),
        "message_template": cleaned_template,
        "saved_at": saved_at,
    }
