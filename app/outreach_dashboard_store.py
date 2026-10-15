from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from supabase import Client, create_client

from app.outreach_campaign_identity import campaign_id_for_name, connect_batch_label, connect_batch_name
from app.settings import (
    Settings,
    load_settings,
)


JOB_TABLE = "outreach_jobs"
TARGET_TABLE = "outreach_job_targets"
PROSPECT_TABLE = "outreach_prospects"
SCHEDULER_TABLE = "outreach_scheduler_state"
ACCOUNT_TABLE = "outreach_accounts"
ACCOUNT_USAGE_TABLE = "outreach_account_usage"
ACCEPTANCE_CHECK_TABLE = "outreach_acceptance_checks"

WEEKLY_SUCCESS_LIMIT = 100

LOCAL_TIMEZONE = timezone(
    timedelta(hours=7)
)

SCHEDULER_NAME = "linkedin_outreach"


class OutreachDashboardStoreError(
    RuntimeError
):
    pass


# =========================================================
# CLIENT
# =========================================================


def get_outreach_client(
    settings: Settings | None = None,
) -> Client:
    active_settings = (
        settings
        if settings is not None
        else load_settings()
    )

    if not (
        active_settings
        .outreach_supabase_url
    ):
        raise OutreachDashboardStoreError(
            "Missing OUTREACH_SUPABASE_URL."
        )

    if not (
        active_settings
        .outreach_supabase_secret_key
    ):
        raise OutreachDashboardStoreError(
            "Missing OUTREACH_SUPABASE_SECRET_KEY."
        )

    return create_client(
        active_settings.outreach_supabase_url,
        active_settings.outreach_supabase_secret_key,
    )


# =========================================================
# BASIC HELPERS
# =========================================================


def _to_int(
    value,
) -> int:
    try:
        return int(
            value or 0
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0


def _safe_text(
    value,
) -> str:
    return str(
        value or ""
    ).strip()


def _current_usage_period() -> tuple[str, str]:
    """
    Current local calendar day and Monday week start.

    This helper is read-only and safe during Railway startup.
    """
    today = datetime.now(
        LOCAL_TIMEZONE
    ).date()

    monday = (
        today
        - timedelta(
            days=today.weekday()
        )
    )

    return (
        today.isoformat(),
        monday.isoformat(),
    )


def _timestamp_value(
    value,
) -> float:
    if not value:
        return 0.0

    try:
        return (
            datetime
            .fromisoformat(
                str(value)
                .replace(
                    "Z",
                    "+00:00",
                )
            )
            .timestamp()
        )

    except Exception:
        return 0.0


# =========================================================
# JOB NORMALIZATION
# =========================================================


def _normalize_job(
    row: dict,
) -> dict:
    target_count = _to_int(
        row.get(
            "target_count"
        )
    )

    processed_count = _to_int(
        row.get(
            "processed_count"
        )
    )

    progress_percent = 0

    if target_count > 0:
        progress_percent = min(
            100,
            round(
                processed_count
                / target_count
                * 100
            ),
        )

    elif (
        _safe_text(
            row.get(
                "status"
            )
        ).lower()
        == "completed"
    ):
        progress_percent = 100

    return {
        "id": _safe_text(
            row.get(
                "id"
            )
        ),
        "connect_batch_id": _safe_text(row.get("id")),

        "job_code": _safe_text(
            row.get(
                "job_code"
            )
        ),

        "display_name": _safe_text(row.get("display_name")),
        "batch_name": connect_batch_name(row.get("batch_name"), row.get("created_at")),
        "batch_label": connect_batch_label(
            row.get("batch_name"), row.get("display_name"), row.get("created_at")
        ),
        "campaign_id": campaign_id_for_name(
            row.get("display_name"), connect_batch_id=_safe_text(row.get("id"))
        ),

        "job_type": _safe_text(
            row.get(
                "job_type"
            )
        ),

        "status": _safe_text(
            row.get(
                "status"
            )
        ),

        "input_count": _to_int(
            row.get(
                "input_count"
            )
        ),

        "target_count": (
            target_count
        ),

        "duplicate_count": _to_int(
            row.get(
                "duplicate_count"
            )
        ),

        "invalid_count": _to_int(
            row.get(
                "invalid_count"
            )
        ),

        "processed_count": (
            processed_count
        ),

        "success_count": _to_int(
            row.get(
                "success_count"
            )
        ),

        "failed_count": _to_int(
            row.get(
                "failed_count"
            )
        ),

        "progress_percent": (
            progress_percent
        ),

        "last_error": (
            row.get(
                "last_error"
            )
        ),

        "created_at": (
            row.get(
                "created_at"
            )
        ),

        "started_at": (
            row.get(
                "started_at"
            )
        ),

        "completed_at": (
            row.get(
                "completed_at"
            )
        ),

        "updated_at": (
            row.get(
                "updated_at"
            )
        ),

        "targets": [],
        "acceptance": None,
    }


# =========================================================
# JOB QUERY FIELDS
# =========================================================


# Selecting all job columns keeps older databases readable until the optional
# display_name migration is applied; normalization below exposes only UI fields.
JOB_SELECT_FIELDS = "*"


# =========================================================
# CURRENT JOB
# =========================================================


def get_current_job(
    *,
    client: Client,
) -> dict | None:
    """
    Ưu tiên:

    running
    -> pending
    -> latest
    """

    # RUNNING
    response = (
        client
        .table(
            JOB_TABLE
        )
        .select(
            JOB_SELECT_FIELDS
        )
        .eq(
            "job_type",
            "connect",
        )
        .eq(
            "status",
            "running",
        )
        .order(
            "created_at",
            desc=False,
        )
        .limit(
            1
        )
        .execute()
    )

    rows = list(
        response.data
        or []
    )

    if rows:
        return _normalize_job(
            rows[0]
        )

    # PENDING
    response = (
        client
        .table(
            JOB_TABLE
        )
        .select(
            JOB_SELECT_FIELDS
        )
        .eq(
            "job_type",
            "connect",
        )
        .eq(
            "status",
            "pending",
        )
        .order(
            "created_at",
            desc=False,
        )
        .limit(
            1
        )
        .execute()
    )

    rows = list(
        response.data
        or []
    )

    if rows:
        return _normalize_job(
            rows[0]
        )

    # LATEST
    response = (
        client
        .table(
            JOB_TABLE
        )
        .select(
            JOB_SELECT_FIELDS
        )
        .eq(
            "job_type",
            "connect",
        )
        .order(
            "created_at",
            desc=True,
        )
        .limit(
            1
        )
        .execute()
    )

    rows = list(
        response.data
        or []
    )

    if not rows:
        return None

    return _normalize_job(
        rows[0]
    )


# =========================================================
# RECENT JOBS
# =========================================================


def get_recent_jobs(
    *,
    client: Client,
    limit: int = 10,
) -> list[dict]:
    response = (
        client
        .table(
            JOB_TABLE
        )
        .select(
            JOB_SELECT_FIELDS
        )
        .eq(
            "job_type",
            "connect",
        )
        .order(
            "created_at",
            desc=True,
        )
        .limit(
            limit
        )
        .execute()
    )

    rows = list(
        response.data
        or []
    )

    return [
        _normalize_job(
            row
        )
        for row in rows
    ]


# =========================================================
# TARGET NORMALIZATION
# =========================================================


def _normalize_target(
    row: dict,
) -> dict:
    prospect = (
        row.get(
            "outreach_prospects"
        )
        or {}
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

        "target_status": _safe_text(
            row.get(
                "status"
            )
        ),

        "assigned_account_id": _safe_text(
            row.get(
                "assigned_account_id"
            )
        ),

        "retry_count": _to_int(
            row.get(
                "retry_count"
            )
        ),

        "last_error": (
            row.get(
                "last_error"
            )
        ),

        "target_created_at": (
            row.get(
                "created_at"
            )
        ),

        "target_updated_at": (
            row.get(
                "updated_at"
            )
        ),

        "completed_at": (
            row.get(
                "completed_at"
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

        "acceptance_check_count": _to_int(
            row.get(
                "acceptance_check_count"
            )
        ),

        "acceptance_accepted_at": (
            row.get(
                "accepted_at"
            )
        ),

        # -----------------------------
        # PROSPECT
        # -----------------------------

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

        "message_status": _safe_text(
            prospect.get(
                "message_status"
            )
        ),

        "last_connect_attempt_at": (
            prospect.get(
                "last_connect_attempt_at"
            )
        ),

        "accepted_at": (
            prospect.get(
                "accepted_at"
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
    }


# =========================================================
# LOAD TARGETS FOR JOBS
# =========================================================


def load_targets_for_jobs(
    *,
    client: Client,
    job_ids: list[str],
) -> dict[str, list[dict]]:
    cleaned_job_ids = [
        str(job_id).strip()
        for job_id in job_ids
        if str(job_id).strip()
    ]

    if not cleaned_job_ids:
        return {}

    response = (
        client
        .table(
            TARGET_TABLE
        )
        .select(
            (
                "id,"
                "job_id,"
                "prospect_id,"
                "status,"
                "assigned_account_id,"
                "retry_count,"
                "last_error,"
                "created_at,"
                "updated_at,"
                "completed_at,"
                "acceptance_status,"
                "acceptance_checked_at,"
                "acceptance_check_count,"
                "accepted_at,"
                "outreach_prospects("
                "id,"
                "linkedin_url,"
                "normalized_url,"
                "connect_status,"
                "message_status,"
                "last_connect_attempt_at,"
                "accepted_at,"
                "last_messaged_at,"
                "created_at,"
                "updated_at"
                ")"
            )
        )
        .in_(
            "job_id",
            cleaned_job_ids,
        )
        .order(
            "created_at",
            desc=False,
        )
        .execute()
    )

    rows = list(
        response.data
        or []
    )

    grouped: dict[
        str,
        list[dict],
    ] = defaultdict(
        list
    )

    for row in rows:
        target = (
            _normalize_target(
                row
            )
        )

        grouped[
            target["job_id"]
        ].append(
            target
        )

    return dict(
        grouped
    )


# =========================================================
# ATTACH TARGETS
# =========================================================


def attach_targets_to_jobs(
    *,
    current_job: dict | None,
    recent_jobs: list[dict],
    targets_by_job: dict[
        str,
        list[dict],
    ],
) -> None:
    if current_job:
        current_job["targets"] = (
            targets_by_job.get(
                current_job["id"],
                [],
            )
        )

    for job in recent_jobs:
        job["targets"] = (
            targets_by_job.get(
                job["id"],
                [],
            )
        )



# =========================================================
# ACCEPTANCE CHECKS
# =========================================================


def _normalize_acceptance_check(
    row: dict,
) -> dict:
    return {
        "id": _safe_text(
            row.get(
                "id"
            )
        ),

        "source_job_id": _safe_text(
            row.get(
                "source_job_id"
            )
        ),

        "run_number": _to_int(
            row.get(
                "run_number"
            )
        ),

        "status": _safe_text(
            row.get(
                "status"
            )
        ),

        "total_to_check": _to_int(
            row.get(
                "total_to_check"
            )
        ),

        "checked_count": _to_int(
            row.get(
                "checked_count"
            )
        ),

        "new_accepted_count": _to_int(
            row.get(
                "new_accepted_count"
            )
        ),

        "still_pending_count": _to_int(
            row.get(
                "still_pending_count"
            )
        ),

        "declined_or_unknown_count": _to_int(
            row.get(
                "declined_or_unknown_count"
            )
        ),

        "failed_count": _to_int(
            row.get(
                "failed_count"
            )
        ),

        "created_at": (
            row.get(
                "created_at"
            )
        ),

        "started_at": (
            row.get(
                "started_at"
            )
        ),

        "completed_at": (
            row.get(
                "completed_at"
            )
        ),

        "updated_at": (
            row.get(
                "updated_at"
            )
        ),
    }


def load_latest_acceptance_checks(
    *,
    client: Client,
    job_ids: list[str],
) -> dict[str, dict]:
    """
    Load all Acceptance Check rows for the visible Connect Jobs.

    The dashboard keeps the latest run for the current status columns,
    but also carries the sum of ``new_accepted_count`` across every run
    for each job.  The weekly accepted total must include #1 + #2 + #3
    without exposing the full history in the normal polling payload.
    """
    cleaned_job_ids = [
        str(job_id).strip()
        for job_id in job_ids
        if str(job_id).strip()
    ]

    if not cleaned_job_ids:
        return {}

    response = (
        client
        .table(
            ACCEPTANCE_CHECK_TABLE
        )
        .select(
            (
                "id,"
                "source_job_id,"
                "run_number,"
                "status,"
                "total_to_check,"
                "checked_count,"
                "new_accepted_count,"
                "still_pending_count,"
                "declined_or_unknown_count,"
                "failed_count,"
                "created_at,"
                "started_at,"
                "completed_at,"
                "updated_at"
            )
        )
        .in_(
            "source_job_id",
            cleaned_job_ids,
        )
        .order(
            "run_number",
            desc=True,
        )
        .execute()
    )

    rows = list(
        response.data
        or []
    )

    latest_by_job: dict[
        str,
        dict,
    ] = {}

    accepted_totals_by_job: dict[
        str,
        int,
    ] = {}

    for row in rows:
        source_job_id = _safe_text(
            row.get(
                "source_job_id"
            )
        )

        if not source_job_id:
            continue

        accepted_totals_by_job[source_job_id] = (
            accepted_totals_by_job.get(source_job_id, 0)
            + _to_int(row.get("new_accepted_count"))
        )

        if source_job_id in latest_by_job:
            continue

        latest_by_job[
            source_job_id
        ] = _normalize_acceptance_check(
            row
        )

    for source_job_id, acceptance in latest_by_job.items():
        acceptance["all_runs_new_accepted_count"] = (
            accepted_totals_by_job.get(source_job_id, 0)
        )

    return latest_by_job


def attach_acceptance_to_jobs(
    *,
    current_job: dict | None,
    recent_jobs: list[dict],
    acceptance_by_job: dict[
        str,
        dict,
    ],
) -> None:
    if current_job:
        current_job["acceptance"] = (
            acceptance_by_job.get(
                current_job["id"]
            )
        )

    for job in recent_jobs:
        job["acceptance"] = (
            acceptance_by_job.get(
                job["id"]
            )
        )


# =========================================================
# SCHEDULER
# =========================================================


def get_scheduler_state(
    *,
    client: Client,
) -> dict | None:
    response = (
        client
        .table(
            SCHEDULER_TABLE
        )
        .select(
            (
                "scheduler_name,"
                "current_account_id,"
                "used_in_current_turn,"
                "turn_limit,"
                "updated_at"
            )
        )
        .eq(
            "scheduler_name",
            SCHEDULER_NAME,
        )
        .limit(
            1
        )
        .execute()
    )

    rows = list(
        response.data
        or []
    )

    if not rows:
        return None

    row = rows[0]

    used = _to_int(
        row.get(
            "used_in_current_turn"
        )
    )

    turn_limit = _to_int(
        row.get(
            "turn_limit"
        )
    )

    return {
        "scheduler_name": _safe_text(
            row.get(
                "scheduler_name"
            )
        ),

        "current_account_id": _safe_text(
            row.get(
                "current_account_id"
            )
        ),

        "used_in_current_turn": (
            used
        ),

        "turn_limit": (
            turn_limit
        ),

        "remaining_in_current_turn": max(
            turn_limit - used,
            0,
        ),

        "updated_at": (
            row.get(
                "updated_at"
            )
        ),
    }


# =========================================================
# RAW ACCOUNTS
# =========================================================


def get_raw_accounts(
    *,
    client: Client,
) -> list[dict]:
    response = (
        client
        .table(
            ACCOUNT_TABLE
        )
        .select(
            (
                "account_id,"
                "status,"
                "profile_directory,"
                "created_at,"
                "updated_at"
            )
        )
        .order(
            "account_id",
            desc=False,
        )
        .execute()
    )

    return list(
        response.data
        or []
    )


# =========================================================
# ACCOUNT USAGE
# =========================================================


def get_account_usage(
    *,
    client: Client,
) -> dict[str, dict]:
    """
    Read quota usage with safe weekly reset.

    Important:
    - The dashboard must never fail just because a reset write fails.
    - Stale weekly data is normalized in memory immediately.
    - Supabase reset is best-effort only.
    - Week boundary is Monday -> Sunday, Asia/Ho_Chi_Minh.
    """
    today, current_week_start = (
        _current_usage_period()
    )

    response = (
        client
        .table(
            ACCOUNT_USAGE_TABLE
        )
        .select(
            (
                "account_id,"
                "daily_success_count,"
                "daily_date,"
                "weekly_success_count,"
                "week_start,"
                "updated_at"
            )
        )
        .execute()
    )

    rows = list(
        response.data
        or []
    )

    normalized_rows: list[dict] = []

    for original_row in rows:
        row = dict(
            original_row
            or {}
        )

        account_id = _safe_text(
            row.get(
                "account_id"
            )
        )

        if not account_id:
            continue

        stored_daily_date = _safe_text(
            row.get(
                "daily_date"
            )
        )

        stored_week_start = _safe_text(
            row.get(
                "week_start"
            )
        )

        weekly_is_stale = (
            stored_week_start
            != current_week_start
        )

        daily_is_stale = (
            stored_daily_date
            != today
        )

        # -------------------------------------------------
        # Normalize the values returned to the UI FIRST.
        # Even if the database write fails, Rate Limits
        # immediately shows the correct new-period values.
        # -------------------------------------------------
        if weekly_is_stale:
            row[
                "weekly_success_count"
            ] = 0

            row[
                "week_start"
            ] = current_week_start

        if daily_is_stale:
            row[
                "daily_success_count"
            ] = 0

            row[
                "daily_date"
            ] = today

        normalized_rows.append(
            row
        )

        # -------------------------------------------------
        # Persist the reset as best-effort only.
        #
        # A Supabase/network error here must NEVER break
        # /api/outreach/dashboard or Railway health.
        # -------------------------------------------------
        if (
            weekly_is_stale
            or daily_is_stale
        ):
            update_data: dict = {}

            if weekly_is_stale:
                update_data[
                    "weekly_success_count"
                ] = 0

                update_data[
                    "week_start"
                ] = current_week_start

            if daily_is_stale:
                update_data[
                    "daily_success_count"
                ] = 0

                update_data[
                    "daily_date"
                ] = today

            try:
                (
                    client
                    .table(
                        ACCOUNT_USAGE_TABLE
                    )
                    .update(
                        update_data
                    )
                    .eq(
                        "account_id",
                        account_id,
                    )
                    .execute()
                )

            except Exception as exc:
                # Dashboard read must remain healthy.
                # The next dashboard poll / worker usage read
                # will retry the normalization.
                print(
                    "[outreach_account_usage] "
                    f"best-effort reset failed for "
                    f"{account_id}: {exc}"
                )

    return {
        _safe_text(
            row.get(
                "account_id"
            )
        ): row
        for row in normalized_rows
        if _safe_text(
            row.get(
                "account_id"
            )
        )
    }


# =========================================================
# ACCOUNT STATS
# =========================================================


def build_account_stats(
    *,
    accounts: list[dict],
    recent_jobs: list[dict],
    scheduler: dict | None,
    usage_by_account: dict[str, dict],
) -> list[dict]:
    job_code_by_id = {
        job["id"]: (
            job.get(
                "job_code"
            )
            or ""
        )
        for job in recent_jobs
    }

    targets: list[dict] = []

    for job in recent_jobs:
        targets.extend(
            job.get(
                "targets",
                []
            )
            or []
        )

    targets_by_account: dict[
        str,
        list[dict],
    ] = defaultdict(
        list
    )

    for target in targets:
        account_id = _safe_text(
            target.get(
                "assigned_account_id"
            )
        )

        if not account_id:
            continue

        targets_by_account[
            account_id
        ].append(
            target
        )

    current_account_id = ""

    used_in_current_turn = 0
    turn_limit = 0

    if scheduler:
        current_account_id = (
            _safe_text(
                scheduler.get(
                    "current_account_id"
                )
            )
        )

        used_in_current_turn = (
            _to_int(
                scheduler.get(
                    "used_in_current_turn"
                )
            )
        )

        turn_limit = (
            _to_int(
                scheduler.get(
                    "turn_limit"
                )
            )
        )

    result: list[dict] = []

    for account in accounts:
        account_id = _safe_text(
            account.get(
                "account_id"
            )
        )

        usage_row = (
            usage_by_account.get(
                account_id,
                {},
            )
            or {}
        )

        daily_success_count = _to_int(
            usage_row.get(
                "daily_success_count"
            )
        )

        weekly_success_count = _to_int(
            usage_row.get(
                "weekly_success_count"
            )
        )

        weekly_remaining = max(
            WEEKLY_SUCCESS_LIMIT
            - weekly_success_count,
            0,
        )

        quota_available = (
            weekly_remaining > 0
        )

        account_targets = (
            targets_by_account.get(
                account_id,
                [],
            )
        )

        completed_count = sum(
            1
            for target in account_targets
            if (
                _safe_text(
                    target.get(
                        "target_status"
                    )
                ).lower()
                == "completed"
            )
        )

        failed_count = sum(
            1
            for target in account_targets
            if (
                _safe_text(
                    target.get(
                        "target_status"
                    )
                ).lower()
                == "failed"
            )
        )

        pending_count = sum(
            1
            for target in account_targets
            if (
                _safe_text(
                    target.get(
                        "target_status"
                    )
                ).lower()
                == "pending"
            )
        )

        sorted_targets = sorted(
            account_targets,
            key=lambda target: (
                _timestamp_value(
                    target.get(
                        "completed_at"
                    )
                    or target.get(
                        "target_updated_at"
                    )
                )
            ),
            reverse=True,
        )

        latest_target = (
            sorted_targets[0]
            if sorted_targets
            else None
        )

        last_used_at = None
        last_job_id = ""
        last_job_code = ""
        last_error = None
        last_linkedin_url = ""

        if latest_target:
            last_used_at = (
                latest_target.get(
                    "completed_at"
                )
                or latest_target.get(
                    "target_updated_at"
                )
            )

            last_job_id = (
                latest_target.get(
                    "job_id"
                )
                or ""
            )

            last_job_code = (
                job_code_by_id.get(
                    last_job_id,
                    "",
                )
            )

            last_error = (
                latest_target.get(
                    "last_error"
                )
            )

            last_linkedin_url = (
                latest_target.get(
                    "linkedin_url"
                )
                or ""
            )

        is_current = (
            account_id
            == current_account_id
        )

        if is_current:
            account_used = (
                used_in_current_turn
            )

            account_remaining = max(
                turn_limit
                - used_in_current_turn,
                0,
            )
        else:
            account_used = 0
            account_remaining = (
                turn_limit
            )

        result.append(
            {
                "account_id": (
                    account_id
                ),

                "status": _safe_text(
                    account.get(
                        "status"
                    )
                ),

                "profile_directory": _safe_text(
                    account.get(
                        "profile_directory"
                    )
                ),

                "created_at": (
                    account.get(
                        "created_at"
                    )
                ),

                "updated_at": (
                    account.get(
                        "updated_at"
                    )
                ),

                "is_current_account": (
                    is_current
                ),

                "used_in_current_turn": (
                    account_used
                ),

                "turn_limit": (
                    turn_limit
                ),

                "remaining_in_current_turn": (
                    account_remaining
                ),

                "weekly_success_count": (
                    weekly_success_count
                ),

                "weekly_limit": (
                    WEEKLY_SUCCESS_LIMIT
                ),

                "weekly_remaining": (
                    weekly_remaining
                ),

                "quota_available": (
                    quota_available
                ),

                "usage_updated_at": (
                    usage_row.get(
                        "updated_at"
                    )
                ),

                "total_assigned": len(
                    account_targets
                ),

                "completed_count": (
                    completed_count
                ),

                "failed_count": (
                    failed_count
                ),

                "pending_count": (
                    pending_count
                ),

                "last_used_at": (
                    last_used_at
                ),

                "last_job_id": (
                    last_job_id
                ),

                "last_job_code": (
                    last_job_code
                ),

                "last_linkedin_url": (
                    last_linkedin_url
                ),

                "last_error": (
                    last_error
                ),
            }
        )

    return result



# =========================================================
# ON-DEMAND OUTREACH PROFILES
# =========================================================


def get_outreach_profiles(
    *,
    settings: Settings | None = None,
) -> list[dict]:
    """
    Load sent Outreach profiles only when the Profiles UI asks for them.

    This deliberately stays OUT of /api/outreach/dashboard so the normal
    dashboard poll does not repeatedly transfer all target/prospect rows.
    """
    client = get_outreach_client(
        settings
    )

    response = (
        client
        .table(
            TARGET_TABLE
        )
        .select(
            (
                "id,"
                "job_id,"
                "prospect_id,"
                "status,"
                "assigned_account_id,"
                "created_at,"
                "updated_at,"
                "completed_at,"
                "acceptance_status,"
                "accepted_at,"
                "outreach_prospects("
                "id,"
                "linkedin_url,"
                "normalized_url,"
                "connect_status,"
                "message_status,"
                "last_connect_attempt_at,"
                "accepted_at,"
                "last_messaged_at"
                ")"
            )
        )
        .order(
            "created_at",
            desc=True,
        )
        .limit(
            1000
        )
        .execute()
    )

    rows = list(
        response.data
        or []
    )

    job_ids = list({
        _safe_text(
            row.get(
                "job_id"
            )
        )
        for row in rows
        if _safe_text(
            row.get(
                "job_id"
            )
        )
    })

    job_code_by_id: dict[str, str] = {}

    if job_ids:
        job_response = (
            client
            .table(
                JOB_TABLE
            )
            .select(
                "*"
            )
            .in_(
                "id",
                job_ids,
            )
            .execute()
        )

        job_code_by_id = {
            _safe_text(
                row.get(
                    "id"
                )
            ): {
                "job_code": _safe_text(row.get("job_code")),
                "display_name": _safe_text(row.get("display_name")),
            }
            for row in (
                job_response.data
                or []
            )
        }

    seen_prospect_ids: set[str] = set()
    profiles: list[dict] = []

    for row in rows:
        prospect = (
            row.get(
                "outreach_prospects"
            )
            or {}
        )

        connect_status = _safe_text(
            prospect.get(
                "connect_status"
            )
        ).lower()

        if connect_status != "invitation_sent":
            continue

        prospect_id = _safe_text(
            row.get(
                "prospect_id"
            )
        )

        if (
            not prospect_id
            or prospect_id
            in seen_prospect_ids
        ):
            continue

        seen_prospect_ids.add(
            prospect_id
        )

        job_id = _safe_text(
            row.get(
                "job_id"
            )
        )

        profiles.append(
            {
                "id": prospect_id,
                "prospect_id": prospect_id,
                "target_id": _safe_text(
                    row.get(
                        "id"
                    )
                ),
                "job_id": job_id,
                "job_code": (
                    job_code_by_id.get(job_id, {}).get("job_code", "")
                ),
                "display_name": job_code_by_id.get(job_id, {}).get(
                    "display_name", ""
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
                "assigned_account_id": _safe_text(
                    row.get(
                        "assigned_account_id"
                    )
                ),
                "target_status": _safe_text(
                    row.get(
                        "status"
                    )
                ),
                "connect_status": connect_status,
                "acceptance_status": (
                    _safe_text(
                        row.get(
                            "acceptance_status"
                        )
                    )
                    or "not_checked"
                ),
                "message_status": (
                    _safe_text(
                        prospect.get(
                            "message_status"
                        )
                    )
                    or "not_started"
                ),
                "sent_at": (
                    prospect.get(
                        "last_connect_attempt_at"
                    )
                    or row.get(
                        "completed_at"
                    )
                    or row.get(
                        "updated_at"
                    )
                    or row.get(
                        "created_at"
                    )
                ),
                "accepted_at": (
                    row.get(
                        "accepted_at"
                    )
                    or prospect.get(
                        "accepted_at"
                    )
                ),
                "last_messaged_at": (
                    prospect.get(
                        "last_messaged_at"
                    )
                ),
            }
        )

    return profiles


# =========================================================
# ON-DEMAND RATE LIMIT DETAILS
# =========================================================


def get_outreach_rate_limits(
    *,
    settings: Settings | None = None,
) -> dict:
    """
    Load detailed Rate Limits only when its drawer is opened.

    The normal dashboard poll only needs quota + scheduler summary.
    Historical target detail is intentionally isolated here.
    """
    client = get_outreach_client(
        settings
    )

    scheduler = get_scheduler_state(
        client=client
    )

    raw_accounts = get_raw_accounts(
        client=client
    )

    usage_by_account = get_account_usage(
        client=client
    )

    recent_jobs = get_recent_jobs(
        client=client,
        limit=25,
    )

    job_ids = [
        job["id"]
        for job in recent_jobs
        if job.get(
            "id"
        )
    ]

    targets_by_job = (
        load_targets_for_jobs(
            client=client,
            job_ids=job_ids,
        )
        if job_ids
        else {}
    )

    attach_targets_to_jobs(
        current_job=None,
        recent_jobs=recent_jobs,
        targets_by_job=targets_by_job,
    )

    accounts = build_account_stats(
        accounts=raw_accounts,
        recent_jobs=recent_jobs,
        scheduler=scheduler,
        usage_by_account=usage_by_account,
    )

    return {
        "scheduler": scheduler,
        "accounts": accounts,
    }


# =========================================================
# DASHBOARD
# =========================================================


def get_outreach_dashboard(
    *,
    settings: Settings | None = None,
) -> dict:
    """
    Lightweight polling payload.

    Important:
    - no target/prospect detail on the normal polling path;
    - recent jobs remain available for Connect / Acceptance UI;
    - Rate Limit detail and Outreach Profiles are loaded on demand.
    """
    client = get_outreach_client(
        settings
    )

    current_job = get_current_job(
        client=client
    )

    recent_jobs = get_recent_jobs(
        client=client,
        limit=100,
    )

    scheduler = get_scheduler_state(
        client=client
    )

    raw_accounts = get_raw_accounts(
        client=client
    )

    usage_by_account = get_account_usage(
        client=client
    )

    job_ids = [
        job["id"]
        for job in recent_jobs
        if job.get(
            "id"
        )
    ]

    if (
        current_job
        and current_job.get(
            "id"
        )
        and current_job["id"]
        not in job_ids
    ):
        job_ids.append(
            current_job["id"]
        )

    acceptance_by_job = (
        load_latest_acceptance_checks(
            client=client,
            job_ids=job_ids,
        )
        if job_ids
        else {}
    )

    attach_acceptance_to_jobs(
        current_job=current_job,
        recent_jobs=recent_jobs,
        acceptance_by_job=acceptance_by_job,
    )

    # Normal dashboard polling only needs quota/scheduler account values.
    # Detailed assigned/success/failed/last-target fields are loaded from
    # get_outreach_rate_limits() when the Rate Limits drawer is opened.
    accounts = build_account_stats(
        accounts=raw_accounts,
        recent_jobs=[],
        scheduler=scheduler,
        usage_by_account=usage_by_account,
    )

    return {
        "current_job": current_job,
        "scheduler": scheduler,
        "accounts": accounts,
        "recent_jobs": recent_jobs,
    }
