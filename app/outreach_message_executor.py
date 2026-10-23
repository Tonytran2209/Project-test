from __future__ import annotations

from datetime import datetime, timezone

from supabase import Client, create_client

from app.linkedin_message_sender import (
    send_message_once,
)
from app.linkedin_message_template import (
    build_message,
    template_uses_company,
)
from app.outreach_message_company import company_for_target
from app.linkedin_profile_message import (
    get_profile_name,
)
from app.outreach_account_pool import (
    OutreachAccountPool,
)
from app.settings import load_settings


MESSAGE_TARGET_TABLE = (
    "outreach_message_targets"
)

PROSPECT_TABLE = (
    "outreach_prospects"
)


class OutreachMessageExecutorError(
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


def get_outreach_supabase_client() -> Client:
    """
    Supabase client for the Mac-side message executor.
    """

    settings = load_settings()

    if not settings.outreach_supabase_url:
        raise OutreachMessageExecutorError(
            "Missing OUTREACH_SUPABASE_URL."
        )

    if not settings.outreach_supabase_secret_key:
        raise OutreachMessageExecutorError(
            "Missing OUTREACH_SUPABASE_SECRET_KEY."
        )

    return create_client(
        settings.outreach_supabase_url,
        settings.outreach_supabase_secret_key,
    )


# =========================================================
# LOAD + CLAIM ONE TARGET
# =========================================================

def load_message_target(
    target_id: str,
    *,
    client: Client | None = None,
) -> dict:
    """
    Read exactly one prepared message target.
    """

    active_client = (
        client
        if client is not None
        else get_outreach_supabase_client()
    )

    cleaned_target_id = _safe_text(
        target_id
    )

    if not cleaned_target_id:
        raise ValueError(
            "target_id is required."
        )

    response = (
        active_client
        .table(
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
                "message_text,"
                "send_attempt_count,"
                "started_at,"
                "completed_at,"
                "last_error"
            )
        )
        .eq(
            "id",
            cleaned_target_id,
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
        raise OutreachMessageExecutorError(
            "Message target not found: "
            f"{cleaned_target_id}"
        )

    return dict(
        rows[0]
    )


def claim_prepared_message_target(
    target_id: str,
    *,
    client: Client | None = None,
) -> dict:
    """
    Atomically-ish claim one target by requiring:
        id == target_id
        status == prepared

    This prevents accidentally sending the same prepared target
    twice from two executor calls.

    No LinkedIn action happens in this function.
    """

    active_client = (
        client
        if client is not None
        else get_outreach_supabase_client()
    )

    target = load_message_target(
        target_id,
        client=active_client,
    )

    if (
        _safe_text(
            target.get(
                "status"
            )
        ).lower()
        != "prepared"
    ):
        raise OutreachMessageExecutorError(
            "Message target is not prepared: "
            f"{target_id} | "
            f"status={target.get('status')}"
        )

    next_attempt_count = (
        int(
            target.get(
                "send_attempt_count",
                0,
            )
            or 0
        )
        + 1
    )

    now = _utc_now()

    response = (
        active_client
        .table(
            MESSAGE_TARGET_TABLE
        )
        .update(
            {
                "status": "processing",
                "started_at": now,
                "completed_at": None,
                "last_error": None,
                "send_attempt_count": (
                    next_attempt_count
                ),
                "updated_at": now,
            }
        )
        .eq(
            "id",
            _safe_text(
                target_id
            ),
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

    if not rows:
        raise OutreachMessageExecutorError(
            "Could not claim prepared message target. "
            "It may already be processing or processed."
        )

    claimed = dict(
        rows[0]
    )

    # Some Supabase/PostgREST configurations may return only
    # updated fields. Merge with the original read for safety.
    merged = dict(
        target
    )
    merged.update(
        claimed
    )

    return merged


# =========================================================
# RESULT WRITES
# =========================================================

def mark_message_target_sent(
    *,
    target_id: str,
    message_text: str,
    client: Client,
) -> None:
    """
    Persist one strictly verified LinkedIn send.

    Both states are required:

    1. outreach_message_targets.status = sent
       -> execution / batch state.

    2. outreach_prospects.message_status = sent
       -> Accepted Pool state shown by the dashboard.

    Accepted Pool reads message_status from outreach_prospects,
    so updating only the message target would leave the UI as
    "Not sent".
    """

    cleaned_target_id = _safe_text(
        target_id
    )

    if not cleaned_target_id:
        raise OutreachMessageExecutorError(
            "target_id is required."
        )

    # Resolve the prospect BEFORE the target state write.
    target_response = (
        client
        .table(
            MESSAGE_TARGET_TABLE
        )
        .select(
            "id,prospect_id,status"
        )
        .eq(
            "id",
            cleaned_target_id,
        )
        .limit(
            1
        )
        .execute()
    )

    target_rows = list(
        target_response.data
        or []
    )

    if not target_rows:
        raise OutreachMessageExecutorError(
            "Message target not found while marking sent: "
            f"{cleaned_target_id}"
        )

    prospect_id = _safe_text(
        target_rows[0].get(
            "prospect_id"
        )
    )

    if not prospect_id:
        raise OutreachMessageExecutorError(
            "Message target has no prospect_id while marking sent: "
            f"{cleaned_target_id}"
        )

    now = _utc_now()

    target_update = (
        client
        .table(
            MESSAGE_TARGET_TABLE
        )
        .update(
            {
                "status": "sent",
                "message_text": (
                    message_text
                ),
                "completed_at": now,
                "last_error": None,
                "updated_at": now,
            }
        )
        .eq(
            "id",
            cleaned_target_id,
        )
        .eq(
            "status",
            "processing",
        )
        .execute()
    )

    updated_target_rows = list(
        target_update.data
        or []
    )

    if not updated_target_rows:
        raise OutreachMessageExecutorError(
            "Could not change message target processing -> sent: "
            f"{cleaned_target_id}"
        )

    # Accepted Pool source of truth for message state.
    prospect_update = (
        client
        .table(
            PROSPECT_TABLE
        )
        .update(
            {
                "message_status": "sent",
                "last_messaged_at": now,
                "updated_at": now,
            }
        )
        .eq(
            "id",
            prospect_id,
        )
        .execute()
    )

    updated_prospect_rows = list(
        prospect_update.data
        or []
    )

    if not updated_prospect_rows:
        raise OutreachMessageExecutorError(
            "Message target was marked sent, but prospect message "
            "state could not be updated: "
            f"prospect_id={prospect_id}"
        )


def mark_message_target_failed(
    *,
    target_id: str,
    error_message: str,
    message_text: str | None,
    client: Client,
) -> None:
    now = _utc_now()

    (
        client
        .table(
            MESSAGE_TARGET_TABLE
        )
        .update(
            {
                "status": "failed",
                "message_text": (
                    message_text
                ),
                "completed_at": now,
                "last_error": (
                    _safe_text(
                        error_message
                    )[:4000]
                ),
                "updated_at": now,
            }
        )
        .eq(
            "id",
            target_id,
        )
        .eq(
            "status",
            "processing",
        )
        .execute()
    )


# =========================================================
# REAL SINGLE-TARGET EXECUTOR
# =========================================================

def execute_one_prepared_message_target(
    *,
    target_id: str,
    template: str,
    client: Client | None = None,
) -> dict:
    """
    REAL SYSTEM — one target only.

    Flow:
        Supabase prepared target
        -> claim as processing
        -> assigned_account_id
        -> exact Outreach browser profile
        -> open target linkedin_url
        -> read first_name
        -> build message
        -> Send
        -> strict verify
        -> target status = sent

    On exception:
        target status = failed
        last_error = exception

    IMPORTANT:
    This sends ONE real LinkedIn message.
    It does NOT loop through a batch yet.
    """

    active_client = (
        client
        if client is not None
        else get_outreach_supabase_client()
    )

    cleaned_template = str(
        template
        or ""
    )

    if not cleaned_template.strip():
        raise ValueError(
            "template is required."
        )

    target = claim_prepared_message_target(
        target_id,
        client=active_client,
    )

    claimed_target_id = _safe_text(
        target.get(
            "id"
        )
        or target_id
    )

    account_id = _safe_text(
        target.get(
            "assigned_account_id"
        )
    )

    linkedin_url = _safe_text(
        target.get(
            "linkedin_url"
        )
    )

    if not account_id:
        mark_message_target_failed(
            target_id=claimed_target_id,
            error_message=(
                "Missing assigned_account_id."
            ),
            message_text=None,
            client=active_client,
        )

        raise OutreachMessageExecutorError(
            "Message target has no assigned_account_id."
        )

    if not linkedin_url:
        mark_message_target_failed(
            target_id=claimed_target_id,
            error_message=(
                "Missing linkedin_url."
            ),
            message_text=None,
            client=active_client,
        )

        raise OutreachMessageExecutorError(
            "Message target has no linkedin_url."
        )

    pool = OutreachAccountPool()

    account = pool.get_account(
        account_id
    )

    browser = (
        account
        .create_browser_manager()
    )

    final_message: str | None = None

    try:
        company = company_for_target(target, client=active_client) if template_uses_company(cleaned_template) else ""
        browser.start()

        page = browser.open_linkedin_url(
            linkedin_url
        )

        profile_name = get_profile_name(
            page
        )

        final_message = build_message(
            first_name=(
                profile_name[
                    "first_name"
                ]
            ),
            template=(
                cleaned_template
            ),
            company=company,
        )

        send_result = send_message_once(
            page,
            final_message,
            expected_profile_name=(
                profile_name[
                    "full_name"
                ]
            ),
        )

        # Send click is the final success boundary.
        # Composer close is cleanup only and is intentionally non-fatal.
        if not bool(
            send_result.get(
                "send_clicked"
            )
        ):
            raise OutreachMessageExecutorError(
                "Message Send button was not clicked."
            )

        mark_message_target_sent(
            target_id=claimed_target_id,
            message_text=final_message,
            client=active_client,
        )

        return {
            "ok": True,
            "target_id": (
                claimed_target_id
            ),
            "batch_id": _safe_text(
                target.get(
                    "batch_id"
                )
            ),
            "prospect_id": _safe_text(
                target.get(
                    "prospect_id"
                )
            ),
            "account_id": (
                account_id
            ),
            "linkedin_url": (
                linkedin_url
            ),
            "full_name": (
                profile_name[
                    "full_name"
                ]
            ),
            "first_name": (
                profile_name[
                    "first_name"
                ]
            ),
            "message_text": (
                final_message
            ),
            "status": "sent",
            "sent_verified": True,
        }

    except Exception as exc:
        try:
            mark_message_target_failed(
                target_id=claimed_target_id,
                error_message=(
                    f"{type(exc).__name__}: {exc}"
                ),
                message_text=(
                    final_message
                ),
                client=active_client,
            )
        except Exception:
            pass

        raise

    finally:
        browser.stop()


def print_single_target_execution(
    *,
    target_id: str,
    template: str,
) -> None:
    """
    Manual test helper.

    WARNING:
    This sends ONE real message from the account stored in
    outreach_message_targets.assigned_account_id.
    """

    result = (
        execute_one_prepared_message_target(
            target_id=target_id,
            template=template,
        )
    )

    print("")
    print(
        "REAL MESSAGE TARGET RESULT"
    )
    print(
        "=========================="
    )

    for key in (
        "target_id",
        "batch_id",
        "prospect_id",
        "account_id",
        "linkedin_url",
        "full_name",
        "first_name",
        "status",
        "sent_verified",
    ):
        print(
            f"{key}: {result.get(key)}"
        )

    print("")
    print(
        "MESSAGE"
    )
    print(
        "-------"
    )
    print(
        result.get(
            "message_text"
        )
    )
