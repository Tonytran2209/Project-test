from __future__ import annotations

from datetime import datetime, timezone

from supabase import Client, create_client

from app.settings import load_settings
from app.linkedin_message_template import build_message, template_uses_company
from app.outreach_message_company import attach_target_companies


MESSAGE_BATCH_TABLE = (
    "outreach_message_batches"
)

MESSAGE_TARGET_TABLE = (
    "outreach_message_targets"
)


class OutreachMessageQueueStoreError(
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
    Railway-safe Outreach Supabase client.

    Important:
    this module does NOT import Playwright, browser managers,
    LinkedIn actions, or Mac-worker code.
    """

    settings = load_settings()

    if not settings.outreach_supabase_url:
        raise OutreachMessageQueueStoreError(
            "Missing OUTREACH_SUPABASE_URL."
        )

    if not settings.outreach_supabase_secret_key:
        raise OutreachMessageQueueStoreError(
            "Missing OUTREACH_SUPABASE_SECRET_KEY."
        )

    return create_client(
        settings.outreach_supabase_url,
        settings.outreach_supabase_secret_key,
    )


def queue_message_batch(
    *,
    batch_id: str,
    message_template: str,
    client: Client | None = None,
) -> dict:
    """
    Queue exactly one PREPARED message batch.

    Flow:
        prepared
        -> write message_template
        -> queued

    This function NEVER sends LinkedIn messages.
    The Mac outreach_message_worker.py is responsible for:
        queued -> processing -> completed
    """

    active_client = (
        client
        if client is not None
        else get_outreach_supabase_client()
    )

    cleaned_batch_id = _safe_text(
        batch_id
    )

    cleaned_template = str(
        message_template
        or ""
    ).strip()

    if not cleaned_batch_id:
        raise OutreachMessageQueueStoreError(
            "batch_id is required."
        )

    if not cleaned_template:
        raise OutreachMessageQueueStoreError(
            "message_template is required."
        )

    # -----------------------------------------------------
    # READ CURRENT BATCH
    # -----------------------------------------------------

    batch_response = (
        active_client
        .table(
            MESSAGE_BATCH_TABLE
        )
        .select(
            (
                "id,"
                "batch_code,"
                "status,"
                "target_count,"
                "message_template,"
                "queued_at"
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
        raise OutreachMessageQueueStoreError(
            "Message batch not found."
        )

    batch = dict(
        batch_rows[0]
    )

    current_status = _safe_text(
        batch.get(
            "status"
        )
    ).lower()

    if current_status != "prepared":
        raise OutreachMessageQueueStoreError(
            (
                "Only a prepared batch can be queued. "
                f"Current status: {current_status or 'unknown'}."
            )
        )

    # -----------------------------------------------------
    # MAKE SURE THERE IS SOMETHING TO SEND
    # -----------------------------------------------------

    target_response = (
        active_client
        .table(
            MESSAGE_TARGET_TABLE
        )
        .select(
            "id,prospect_id,linkedin_url,normalized_url"
        )
        .eq(
            "batch_id",
            cleaned_batch_id,
        )
        .eq(
            "status",
            "prepared",
        )
        .execute()
    )

    prepared_targets = list(
        target_response.data
        or []
    )

    if not prepared_targets:
        raise OutreachMessageQueueStoreError(
            "Message batch has no prepared targets."
        )

    try:
        build_message("Recipient", cleaned_template, company="Company")
        if template_uses_company(cleaned_template):
            attach_target_companies(prepared_targets, client=active_client)
            missing = [target for target in prepared_targets if not target.get("company_name")]
            if missing:
                example = missing[0].get("linkedin_url") or missing[0].get("id")
                raise ValueError(
                    f"{len(missing)} recipients have no saved company name (e.g. {example}). "
                    "Add their company names or remove {company} from the template."
                )
    except ValueError as exc:
        raise OutreachMessageQueueStoreError(str(exc)) from exc

    # -----------------------------------------------------
    # CONDITIONAL QUEUE
    # -----------------------------------------------------

    now = _utc_now()

    update_response = (
        active_client
        .table(
            MESSAGE_BATCH_TABLE
        )
        .update(
            {
                "status": "queued",
                "message_template": (
                    cleaned_template
                ),
                "queued_at": now,
                "last_error": None,
                "updated_at": now,
            }
        )
        .eq(
            "id",
            cleaned_batch_id,
        )
        .eq(
            "status",
            "prepared",
        )
        .execute()
    )

    updated_rows = list(
        update_response.data
        or []
    )

    if not updated_rows:
        raise OutreachMessageQueueStoreError(
            (
                "Could not queue message batch. "
                "Its status may have changed."
            )
        )

    queued = dict(
        updated_rows[0]
    )

    queued[
        "prepared_target_count"
    ] = len(
        prepared_targets
    )

    return queued
