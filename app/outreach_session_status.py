from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from supabase import Client, create_client

from app.outreach_account_pool import (
    OUTREACH_ACCOUNT_DISPLAY_NAMES,
    OutreachAccountPool,
)
from app.settings import load_settings


SESSION_TABLE = "outreach_account_sessions"

SESSION_STATUSES = {
    "never_checked",
    "pending",
    "checking",
    "logged_in",
    "logged_out",
    "checkpoint",
    "busy",
    "unknown",
    "failed",
}


class OutreachSessionStatusError(RuntimeError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def get_outreach_supabase_client() -> Client:
    settings = load_settings()

    if not settings.outreach_supabase_url:
        raise OutreachSessionStatusError(
            "Missing OUTREACH_SUPABASE_URL."
        )

    if not settings.outreach_supabase_secret_key:
        raise OutreachSessionStatusError(
            "Missing OUTREACH_SUPABASE_SECRET_KEY."
        )

    return create_client(
        settings.outreach_supabase_url,
        settings.outreach_supabase_secret_key,
    )


def _account_rows_from_pool() -> list[dict[str, Any]]:
    pool = OutreachAccountPool()

    return [
        {
            "account_id": account.account_id,
            "display_name": account.display_name,
        }
        for account in pool.accounts
    ]


def _normalise_session_row(
    row: dict[str, Any],
    *,
    fallback_display_name: str,
) -> dict[str, Any]:
    status = _safe_text(
        row.get("status")
    ) or "never_checked"

    if status not in SESSION_STATUSES:
        status = "unknown"

    return {
        "account_id": _safe_text(
            row.get("account_id")
        ),
        "display_name": (
            _safe_text(
                row.get("display_name")
            )
            or fallback_display_name
        ),
        "status": status,
        "requested_at": row.get(
            "requested_at"
        ),
        "checking_at": row.get(
            "checking_at"
        ),
        "checked_at": row.get(
            "checked_at"
        ),
        "current_url": row.get(
            "current_url"
        ),
        "last_error": row.get(
            "last_error"
        ),
        "updated_at": row.get(
            "updated_at"
        ),
    }


def ensure_session_rows(
    *,
    client: Client | None = None,
) -> list[dict[str, Any]]:
    """
    Ensure the registered Outreach account rows exist.

    This function is kept for compatibility, but it now performs at most:
      1 SELECT
      1 batch UPSERT only when rows are missing
    """

    active_client = client or get_outreach_supabase_client()
    accounts = _account_rows_from_pool()

    response = (
        active_client
        .table(SESSION_TABLE)
        .select("account_id")
        .execute()
    )

    existing_ids = {
        _safe_text(
            row.get("account_id")
        )
        for row in list(
            response.data
            or []
        )
    }

    missing = [
        {
            "account_id": account[
                "account_id"
            ],
            "display_name": account[
                "display_name"
            ],
            "status": "never_checked",
            "updated_at": _utc_now_iso(),
        }
        for account in accounts
        if account[
            "account_id"
        ] not in existing_ids
    ]

    if missing:
        (
            active_client
            .table(SESSION_TABLE)
            .upsert(
                missing,
                on_conflict="account_id",
            )
            .execute()
        )

    return accounts


def list_outreach_session_statuses(
    *,
    client: Client | None = None,
) -> list[dict[str, Any]]:
    """
    Load the popup state with one normal SELECT.

    Missing rows are rare; if any are missing, they are inserted in one batch
    and merged locally instead of performing a second full-table SELECT.
    """

    active_client = client or get_outreach_supabase_client()
    accounts = _account_rows_from_pool()

    response = (
        active_client
        .table(SESSION_TABLE)
        .select(
            "account_id,display_name,status,requested_at,"
            "checking_at,checked_at,current_url,last_error,updated_at"
        )
        .execute()
    )

    rows_by_id = {
        _safe_text(
            row.get("account_id")
        ): dict(row)
        for row in list(
            response.data
            or []
        )
    }

    missing_payload: list[
        dict[str, Any]
    ] = []

    now = _utc_now_iso()

    for account in accounts:
        account_id = account[
            "account_id"
        ]

        if account_id in rows_by_id:
            continue

        row = {
            "account_id": account_id,
            "display_name": account[
                "display_name"
            ],
            "status": "never_checked",
            "updated_at": now,
        }

        rows_by_id[
            account_id
        ] = row

        missing_payload.append(
            row
        )

    if missing_payload:
        (
            active_client
            .table(SESSION_TABLE)
            .upsert(
                missing_payload,
                on_conflict="account_id",
            )
            .execute()
        )

    result: list[
        dict[str, Any]
    ] = []

    for account in accounts:
        account_id = account[
            "account_id"
        ]

        result.append(
            _normalise_session_row(
                rows_by_id[
                    account_id
                ],
                fallback_display_name=(
                    account[
                        "display_name"
                    ]
                    or OUTREACH_ACCOUNT_DISPLAY_NAMES.get(
                        account_id,
                        account_id,
                    )
                ),
            )
        )

    return result


def queue_outreach_session_checks(
    *,
    account_ids: list[str] | None = None,
    client: Client | None = None,
) -> list[dict[str, Any]]:
    """
    Queue session checks with ONE batch UPSERT.

    No worker polling is required. The UPSERT itself is the event that wakes
    the Mac worker through Supabase Realtime.
    """

    active_client = client or get_outreach_supabase_client()
    accounts = _account_rows_from_pool()

    account_by_id = {
        item[
            "account_id"
        ]: item
        for item in accounts
    }

    allowed_ids = set(
        account_by_id
    )

    requested_ids = (
        [
            _safe_text(
                value
            )
            for value in account_ids
        ]
        if account_ids is not None
        else [
            item[
                "account_id"
            ]
            for item in accounts
        ]
    )

    cleaned_ids: list[
        str
    ] = []

    seen: set[
        str
    ] = set()

    for account_id in requested_ids:
        if (
            not account_id
            or account_id in seen
        ):
            continue

        if account_id not in allowed_ids:
            raise OutreachSessionStatusError(
                f"Unknown Outreach account: {account_id}"
            )

        seen.add(
            account_id
        )

        cleaned_ids.append(
            account_id
        )

    if not cleaned_ids:
        raise OutreachSessionStatusError(
            "No Outreach accounts selected for session check."
        )

    now = _utc_now_iso()

    payload = [
        {
            "account_id": account_id,
            "display_name": account_by_id[
                account_id
            ][
                "display_name"
            ],
            "status": "pending",
            "requested_at": now,
            "checking_at": None,
            "last_error": None,
            "updated_at": now,
        }
        for account_id in cleaned_ids
    ]

    response = (
        active_client
        .table(SESSION_TABLE)
        .upsert(
            payload,
            on_conflict="account_id",
        )
        .execute()
    )

    returned_rows = {
        _safe_text(
            row.get("account_id")
        ): dict(row)
        for row in list(
            response.data
            or []
        )
    }

    # The normal "Check all accounts" path gets all configured rows back from the
    # single UPSERT, so no follow-up GET is necessary.
    if set(cleaned_ids) == allowed_ids and len(returned_rows) == len(accounts):
        return [
            _normalise_session_row(
                returned_rows[
                    account[
                        "account_id"
                    ]
                ],
                fallback_display_name=account[
                    "display_name"
                ],
            )
            for account in accounts
        ]

    # Future single-account checks still return the complete popup state.
    # This fallback is user-triggered only; it is not background polling.
    return list_outreach_session_statuses(
        client=active_client
    )
