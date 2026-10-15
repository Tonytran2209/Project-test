from __future__ import annotations

from collections import OrderedDict

from supabase import Client, create_client

from app.outreach_campaign_identity import (
    campaign_id_for_name, connect_batch_label, connect_batch_name,
)
from app.settings import load_settings


TARGET_TABLE = "outreach_job_targets"
JOB_TABLE = "outreach_jobs"


class OutreachAcceptedPoolStoreError(
    RuntimeError
):
    pass


def get_outreach_supabase_client() -> Client:
    """
    Backend-safe Outreach Supabase client.

    Keep Railway independent from LinkedIn browser/action imports.
    """
    settings = load_settings()

    if not settings.outreach_supabase_url:
        raise OutreachAcceptedPoolStoreError(
            "Missing OUTREACH_SUPABASE_URL."
        )

    if not settings.outreach_supabase_secret_key:
        raise OutreachAcceptedPoolStoreError(
            "Missing OUTREACH_SUPABASE_SECRET_KEY."
        )

    return create_client(
        settings.outreach_supabase_url,
        settings.outreach_supabase_secret_key,
    )


def _safe_text(
    value,
) -> str:
    return str(
        value
        or ""
    ).strip()


def _timestamp_value(
    value,
) -> str:
    """
    ISO timestamps are sortable lexicographically when stored in
    the same ISO-8601 format. Empty values sort last in our logic.
    """
    return _safe_text(
        value
    )


def _message_bucket(
    message_status: str,
) -> str:
    """
    For now we only expose the two business buckets requested:

    - not_sent
    - sent

    Any non-sent status remains in not_sent until the later
    messaging workflow defines more granular states.
    """
    status = _safe_text(
        message_status
    ).lower()

    if status == "sent":
        return "sent"

    return "not_sent"


def _dedupe_key(
    *,
    prospect_id: str,
    normalized_url: str,
    linkedin_url: str,
) -> str:
    """
    Primary identity:
        prospect_id

    Safety fallback:
        normalized_url

    Last-resort fallback:
        linkedin_url

    This prevents the same accepted profile from appearing
    multiple times in the Accepted Pool.
    """
    cleaned_prospect_id = _safe_text(
        prospect_id
    )

    if cleaned_prospect_id:
        return (
            "prospect:"
            + cleaned_prospect_id
        )

    cleaned_normalized_url = _safe_text(
        normalized_url
    ).lower()

    if cleaned_normalized_url:
        return (
            "url:"
            + cleaned_normalized_url
        )

    cleaned_linkedin_url = _safe_text(
        linkedin_url
    ).lower().rstrip("/")

    return (
        "raw:"
        + cleaned_linkedin_url
    )


def _normalize_pool_row(
    row: dict,
) -> dict:
    prospect = (
        row.get(
            "outreach_prospects"
        )
        or {}
    )

    message_status = _safe_text(
        prospect.get(
            "message_status"
        )
    )

    return {
        "target_id": _safe_text(
            row.get(
                "id"
            )
        ),
        "job_id": _safe_text(
            row.get(
                "job_id"
            )
        ),
        "prospect_id": _safe_text(
            row.get(
                "prospect_id"
            )
        ),
        "assigned_account_id": _safe_text(
            row.get(
                "assigned_account_id"
            )
        ),
        "acceptance_status": _safe_text(
            row.get(
                "acceptance_status"
            )
        ),
        "acceptance_checked_at": (
            row.get(
                "acceptance_checked_at"
            )
        ),
        "accepted_at": (
            row.get(
                "accepted_at"
            )
        ),
        "acceptance_check_count": int(
            row.get(
                "acceptance_check_count",
                0,
            )
            or 0
        ),
        "linkedin_url": _safe_text(
            prospect.get(
                "linkedin_url"
            )
        ),
        "normalized_url": _safe_text(
            prospect.get(
                "normalized_url"
            )
        ),
        "connect_status": _safe_text(
            prospect.get(
                "connect_status"
            )
        ),
        "message_status": message_status,
        "message_bucket": (
            _message_bucket(
                message_status
            )
        ),
        "last_messaged_at": (
            prospect.get(
                "last_messaged_at"
            )
        ),
        "prospect_created_at": (
            prospect.get(
                "created_at"
            )
        ),
        "prospect_updated_at": (
            prospect.get(
                "updated_at"
            )
        ),
        # Filled from the parent Connect Job below. This is the only
        # timestamp used to attribute a profile to a reporting week.
        "job_created_at": None,
    }



def _load_job_metadata(
    *,
    client: Client,
    job_ids: list[str],
) -> dict[str, dict[str, str]]:
    """
    Resolve the existing Connect Job metadata for the job_id already stored
    on outreach_job_targets.

    This is the original send/run identity:
        outreach_job_targets.job_id
            -> outreach_jobs.id
            -> outreach_jobs.display_name + outreach_jobs.job_code

    Only the distinct job IDs present in the Accepted Pool are requested.
    """

    cleaned_ids = list(
        dict.fromkeys(
            _safe_text(value)
            for value in job_ids
            if _safe_text(value)
        )
    )

    if not cleaned_ids:
        return {}

    response = (
        client
        .table(
            JOB_TABLE
        )
        .select(
            "*"
        )
        .in_(
            "id",
            cleaned_ids,
        )
        .execute()
    )

    result: dict[str, dict[str, str]] = {}

    for row in list(
        response.data
        or []
    ):
        job_id = _safe_text(
            row.get(
                "id"
            )
        )

        if not job_id:
            continue

        result[job_id] = {
            "job_code": _safe_text(row.get("job_code")),
            "display_name": _safe_text(row.get("display_name")),
            "batch_name": connect_batch_name(row.get("batch_name"), row.get("created_at")),
            "batch_label": connect_batch_label(
                row.get("batch_name"), row.get("display_name"), row.get("created_at")
            ),
            "campaign_id": campaign_id_for_name(
                row.get("display_name"), connect_batch_id=job_id
            ),
            "created_at": _safe_text(row.get("created_at")),
        }

    return result


def get_accepted_pool(
    *,
    client: Client | None = None,
) -> dict:
    """
    Build the Accepted Pool directly from current source data.

    Source of truth:
        outreach_job_targets.acceptance_status == accepted

    Important:
    - no separate accepted-pool table;
    - every Acceptance Check update is visible on the next API read;
    - one profile appears only once;
    - week attribution comes from the parent Connect Job's created_at;
      later Acceptance Checks never move a profile into another week;
    - primary dedupe key is prospect_id;
    - normalized_url is the safety fallback;
    - the accepted target with the latest accepted/check timestamp wins.

    Return:
        {
            "summary": {
                "total": ...,
                "not_sent": ...,
                "sent": ...
            },
            "items": [...]
        }
    """
    active_client = (
        client
        if client is not None
        else get_outreach_supabase_client()
    )

    try:
        response = (
            active_client
            .table(
                TARGET_TABLE
            )
            .select(
                (
                    "id,"
                    "job_id,"
                    "prospect_id,"
                    "assigned_account_id,"
                    "acceptance_status,"
                    "acceptance_checked_at,"
                    "accepted_at,"
                    "acceptance_check_count,"
                    "outreach_prospects("
                    "id,"
                    "linkedin_url,"
                    "normalized_url,"
                    "connect_status,"
                    "message_status,"
                    "last_messaged_at,"
                    "created_at,"
                    "updated_at"
                    ")"
                )
            )
            .eq(
                "acceptance_status",
                "accepted",
            )
            .order(
                "accepted_at",
                desc=True,
            )
            .execute()
        )

    except Exception as exc:
        raise OutreachAcceptedPoolStoreError(
            "Could not load Accepted Pool: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    rows = list(
        response.data
        or []
    )

    # OrderedDict preserves the first row we keep.
    # Because the query is newest-first, latest accepted state wins.
    unique: OrderedDict[
        str,
        dict,
    ] = OrderedDict()

    for raw_row in rows:
        item = _normalize_pool_row(
            raw_row
        )

        # Pool rows must remain actionable for the later messaging step.
        if not item[
            "assigned_account_id"
        ]:
            continue

        if not item[
            "linkedin_url"
        ]:
            continue

        key = _dedupe_key(
            prospect_id=(
                item[
                    "prospect_id"
                ]
            ),
            normalized_url=(
                item[
                    "normalized_url"
                ]
            ),
            linkedin_url=(
                item[
                    "linkedin_url"
                ]
            ),
        )

        existing = unique.get(
            key
        )

        if existing is None:
            unique[
                key
            ] = item
            continue

        # Extra safety if source ordering is ever inconsistent:
        # keep whichever accepted/check timestamp is newer.
        existing_time = max(
            _timestamp_value(
                existing.get(
                    "accepted_at"
                )
            ),
            _timestamp_value(
                existing.get(
                    "acceptance_checked_at"
                )
            ),
        )

        candidate_time = max(
            _timestamp_value(
                item.get(
                    "accepted_at"
                )
            ),
            _timestamp_value(
                item.get(
                    "acceptance_checked_at"
                )
            ),
        )

        if candidate_time > existing_time:
            unique[
                key
            ] = item

    items = list(
        unique.values()
    )

    job_metadata_by_id = (
        _load_job_metadata(
            client=active_client,
            job_ids=[
                _safe_text(
                    item.get(
                        "job_id"
                    )
                )
                for item in items
            ],
        )
    )

    for item in items:
        job_id = _safe_text(
            item.get(
                "job_id"
            )
        )

        job_metadata = job_metadata_by_id.get(job_id, {})
        item["connect_batch_id"] = job_id
        item["campaign_id"] = job_metadata.get("campaign_id") or campaign_id_for_name(
            "", connect_batch_id=job_id
        )
        item["job_code"] = job_metadata.get("job_code", "")
        item["batch_name"] = job_metadata.get("batch_name", "")
        item["batch_label"] = job_metadata.get("batch_label", "")
        item["display_name"] = job_metadata.get("display_name", "")
        item["campaign_name"] = item["display_name"]
        item["job_created_at"] = job_metadata.get("created_at")

    # Stable newest-first output by the week the Connect Job was sent.
    # Acceptance timestamps are deliberately not used for this ordering.
    items.sort(
        key=lambda item: _timestamp_value(item.get("job_created_at")),
        reverse=True,
    )

    sent_count = sum(
        1
        for item in items
        if item[
            "message_bucket"
        ] == "sent"
    )

    not_sent_count = (
        len(items)
        - sent_count
    )

    return {
        "summary": {
            "total": len(
                items
            ),
            "not_sent": (
                not_sent_count
            ),
            "sent": sent_count,
        },
        "items": items,
    }
