from __future__ import annotations

import time
from collections import OrderedDict
from datetime import datetime, timezone

from supabase import Client

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
from app.outreach_message_executor import (
    OutreachMessageExecutorError,
    claim_prepared_message_target,
    get_outreach_supabase_client,
    mark_message_target_failed,
    mark_message_target_sent,
)


MESSAGE_BATCH_TABLE = "outreach_message_batches"
MESSAGE_TARGET_TABLE = "outreach_message_targets"

PROFILE_DELAY_SECONDS = 2.5
ACCOUNT_SWITCH_DELAY_SECONDS = 5.0


class OutreachMessageBatchExecutorError(
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


def load_message_batch(
    batch_id: str,
    *,
    client: Client | None = None,
) -> dict:
    active_client = (
        client
        if client is not None
        else get_outreach_supabase_client()
    )

    cleaned_batch_id = _safe_text(
        batch_id
    )

    if not cleaned_batch_id:
        raise ValueError(
            "batch_id is required."
        )

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
                "message_template,"
                "target_count,"
                "processed_count,"
                "sent_count,"
                "failed_count,"
                "queued_at,"
                "started_at,"
                "completed_at,"
                "last_error,"
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
        raise OutreachMessageBatchExecutorError(
            "Message batch not found: "
            f"{cleaned_batch_id}"
        )

    target_response = (
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
                "last_error,"
                "created_at,"
                "updated_at"
            )
        )
        .eq(
            "batch_id",
            cleaned_batch_id,
        )
        .eq(
            "status",
            "prepared",
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

    batch[
        "prepared_targets"
    ] = list(
        target_response.data
        or []
    )

    return batch


def group_prepared_targets_by_account(
    targets: list[dict],
) -> OrderedDict[str, list[dict]]:
    grouped: OrderedDict[
        str,
        list[dict],
    ] = OrderedDict()

    for target in targets:
        account_id = _safe_text(
            target.get(
                "assigned_account_id"
            )
        )

        if not account_id:
            raise OutreachMessageBatchExecutorError(
                "Prepared target has no assigned_account_id: "
                f"{target.get('id')}"
            )

        grouped.setdefault(
            account_id,
            [],
        ).append(
            target
        )

    return grouped


def claim_queued_batch(
    *,
    batch_id: str,
    client: Client,
) -> None:
    """
    Only queued batches may be claimed by the worker.
    """

    now = _utc_now()

    response = (
        client
        .table(
            MESSAGE_BATCH_TABLE
        )
        .update(
            {
                "status": "processing",
                "started_at": now,
                "completed_at": None,
                "last_error": None,
                "updated_at": now,
            }
        )
        .eq(
            "id",
            batch_id,
        )
        .eq(
            "status",
            "queued",
        )
        .execute()
    )

    rows = list(
        response.data
        or []
    )

    if not rows:
        raise OutreachMessageBatchExecutorError(
            "Could not claim queued message batch."
        )


def refresh_batch_counters(
    *,
    batch_id: str,
    client: Client,
) -> dict:
    response = (
        client
        .table(
            MESSAGE_TARGET_TABLE
        )
        .select(
            "status"
        )
        .eq(
            "batch_id",
            batch_id,
        )
        .execute()
    )

    rows = list(
        response.data
        or []
    )

    sent_count = sum(
        1
        for row in rows
        if _safe_text(
            row.get(
                "status"
            )
        ).lower() == "sent"
    )

    failed_count = sum(
        1
        for row in rows
        if _safe_text(
            row.get(
                "status"
            )
        ).lower() == "failed"
    )

    processed_count = (
        sent_count
        + failed_count
    )

    (
        client
        .table(
            MESSAGE_BATCH_TABLE
        )
        .update(
            {
                "processed_count": processed_count,
                "sent_count": sent_count,
                "failed_count": failed_count,
                "updated_at": _utc_now(),
            }
        )
        .eq(
            "id",
            batch_id,
        )
        .execute()
    )

    return {
        "processed_count": processed_count,
        "sent_count": sent_count,
        "failed_count": failed_count,
    }


def mark_batch_completed(
    *,
    batch_id: str,
    client: Client,
) -> dict:
    counters = refresh_batch_counters(
        batch_id=batch_id,
        client=client,
    )

    (
        client
        .table(
            MESSAGE_BATCH_TABLE
        )
        .update(
            {
                "status": "completed",
                "completed_at": _utc_now(),
                "last_error": None,
                "updated_at": _utc_now(),
            }
        )
        .eq(
            "id",
            batch_id,
        )
        .eq(
            "status",
            "processing",
        )
        .execute()
    )

    return counters


def mark_batch_failed(
    *,
    batch_id: str,
    error_message: str,
    client: Client,
) -> None:
    try:
        refresh_batch_counters(
            batch_id=batch_id,
            client=client,
        )
    except Exception:
        pass

    (
        client
        .table(
            MESSAGE_BATCH_TABLE
        )
        .update(
            {
                "status": "failed",
                "completed_at": _utc_now(),
                "last_error": (
                    _safe_text(
                        error_message
                    )[:4000]
                ),
                "updated_at": _utc_now(),
            }
        )
        .eq(
            "id",
            batch_id,
        )
        .execute()
    )


def execute_target_with_browser(
    *,
    target: dict,
    template: str,
    browser,
    client: Client,
) -> dict:
    target_id = _safe_text(
        target.get(
            "id"
        )
    )

    claimed = claim_prepared_message_target(
        target_id,
        client=client,
    )

    linkedin_url = _safe_text(
        claimed.get(
            "linkedin_url"
        )
    )

    account_id = _safe_text(
        claimed.get(
            "assigned_account_id"
        )
    )

    final_message: str | None = None

    try:
        company = company_for_target(claimed, client=client) if template_uses_company(template) else ""
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
            template=template,
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

        if not bool(
            send_result.get(
                "sent_verified"
            )
        ):
            raise OutreachMessageExecutorError(
                "Message send was not verified."
            )

        mark_message_target_sent(
            target_id=target_id,
            message_text=final_message,
            client=client,
        )

        return {
            "ok": True,
            "target_id": target_id,
            "account_id": account_id,
            "linkedin_url": linkedin_url,
            "status": "sent",
        }

    except Exception as exc:
        try:
            mark_message_target_failed(
                target_id=target_id,
                error_message=(
                    f"{type(exc).__name__}: {exc}"
                ),
                message_text=final_message,
                client=client,
            )
        except Exception:
            pass

        return {
            "ok": False,
            "target_id": target_id,
            "account_id": account_id,
            "linkedin_url": linkedin_url,
            "status": "failed",
            "error": (
                f"{type(exc).__name__}: {exc}"
            ),
        }


def execute_queued_message_batch(
    *,
    batch_id: str,
    client: Client | None = None,
) -> dict:
    """
    Execute exactly one QUEUED batch.

    The exact message template is read from the batch row.
    """

    active_client = (
        client
        if client is not None
        else get_outreach_supabase_client()
    )

    batch = load_message_batch(
        batch_id,
        client=active_client,
    )

    cleaned_batch_id = _safe_text(
        batch.get(
            "id"
        )
    )

    if (
        _safe_text(
            batch.get(
                "status"
            )
        ).lower()
        != "queued"
    ):
        raise OutreachMessageBatchExecutorError(
            "Message batch is not queued: "
            f"{cleaned_batch_id} | "
            f"status={batch.get('status')}"
        )

    template = str(
        batch.get(
            "message_template"
        )
        or ""
    )

    if not template.strip():
        raise OutreachMessageBatchExecutorError(
            "Queued batch has no message_template."
        )

    targets = list(
        batch.get(
            "prepared_targets"
        )
        or []
    )

    if not targets:
        raise OutreachMessageBatchExecutorError(
            "Queued message batch has no prepared targets."
        )

    grouped = group_prepared_targets_by_account(
        targets
    )

    claim_queued_batch(
        batch_id=cleaned_batch_id,
        client=active_client,
    )

    pool = OutreachAccountPool()
    results: list[dict] = []

    try:
        account_items = list(
            grouped.items()
        )

        for account_index, (
            account_id,
            account_targets,
        ) in enumerate(
            account_items
        ):
            account = pool.get_account(
                account_id
            )

            if not account.enabled:
                for target in account_targets:
                    target_id = _safe_text(
                        target.get(
                            "id"
                        )
                    )

                    try:
                        claim_prepared_message_target(
                            target_id,
                            client=active_client,
                        )

                        mark_message_target_failed(
                            target_id=target_id,
                            error_message=(
                                "Assigned Outreach account is disabled."
                            ),
                            message_text=None,
                            client=active_client,
                        )
                    except Exception:
                        pass

                    results.append(
                        {
                            "ok": False,
                            "target_id": target_id,
                            "account_id": account_id,
                            "status": "failed",
                            "error": (
                                "Assigned Outreach account is disabled."
                            ),
                        }
                    )

                refresh_batch_counters(
                    batch_id=cleaned_batch_id,
                    client=active_client,
                )
                continue

            browser = account.create_browser_manager()

            try:
                browser.start()

                for target_index, target in enumerate(
                    account_targets
                ):
                    result = execute_target_with_browser(
                        target=target,
                        template=template,
                        browser=browser,
                        client=active_client,
                    )

                    results.append(
                        result
                    )

                    refresh_batch_counters(
                        batch_id=cleaned_batch_id,
                        client=active_client,
                    )

                    if (
                        target_index
                        < len(
                            account_targets
                        ) - 1
                    ):
                        time.sleep(
                            PROFILE_DELAY_SECONDS
                        )

            finally:
                browser.stop()

            if (
                account_index
                < len(
                    account_items
                ) - 1
            ):
                time.sleep(
                    ACCOUNT_SWITCH_DELAY_SECONDS
                )

        counters = mark_batch_completed(
            batch_id=cleaned_batch_id,
            client=active_client,
        )

        return {
            "ok": True,
            "batch_id": cleaned_batch_id,
            "batch_code": _safe_text(
                batch.get(
                    "batch_code"
                )
            ),
            "target_count": len(
                targets
            ),
            "processed_count": (
                counters[
                    "processed_count"
                ]
            ),
            "sent_count": (
                counters[
                    "sent_count"
                ]
            ),
            "failed_count": (
                counters[
                    "failed_count"
                ]
            ),
            "results": results,
        }

    except Exception as exc:
        try:
            mark_batch_failed(
                batch_id=cleaned_batch_id,
                error_message=(
                    f"{type(exc).__name__}: {exc}"
                ),
                client=active_client,
            )
        except Exception:
            pass

        raise
