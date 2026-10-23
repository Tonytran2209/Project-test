from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from supabase import AsyncClient, acreate_client

from app.linkedin_session_checker import (
    check_outreach_account_session,
)
from app.outreach_account_pool import OutreachAccountPool
from app.outreach_session_status import SESSION_TABLE
from app.settings import load_settings


logger = logging.getLogger("outreach_session_worker")

_work_queue: asyncio.Queue[str] | None = None
_queued_accounts: set[str] = set()

_RECOVER_PENDING = "__recover_pending__"


def _get_work_queue() -> asyncio.Queue[str]:
    """
    Return the queue created inside the currently running asyncio loop.

    Python 3.9 can bind asyncio primitives to the event loop that existed
    when they were created. Creating the queue at module import time can
    therefore produce "Future attached to a different loop" once
    asyncio.run() starts its own loop.
    """

    if _work_queue is None:
        raise RuntimeError(
            "Session worker queue has not been initialized."
        )

    return _work_queue


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _payload_record(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}

    for key in ("new", "record"):
        value = payload.get(key)
        if isinstance(value, dict):
            return dict(value)

    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("record", "new"):
            value = data.get(key)
            if isinstance(value, dict):
                return dict(value)

    return {}


async def get_async_supabase_client() -> AsyncClient:
    settings = load_settings()

    if not settings.outreach_supabase_url:
        raise RuntimeError(
            "Missing OUTREACH_SUPABASE_URL."
        )

    if not settings.outreach_supabase_secret_key:
        raise RuntimeError(
            "Missing OUTREACH_SUPABASE_SECRET_KEY."
        )

    return await acreate_client(
        settings.outreach_supabase_url,
        settings.outreach_supabase_secret_key,
    )


def _enqueue_account(
    account_id: str,
) -> None:
    account_id = _clean(account_id)

    if (
        not account_id
        or account_id in _queued_accounts
    ):
        return

    _queued_accounts.add(
        account_id
    )

    _get_work_queue().put_nowait(
        account_id
    )


def _finish_account(
    account_id: str,
) -> None:
    _queued_accounts.discard(
        account_id
    )


def _enqueue_recovery() -> None:
    _get_work_queue().put_nowait(
        _RECOVER_PENDING
    )


def _handle_realtime_change(
    payload: Any,
) -> None:
    """
    Called by Supabase Realtime whenever the session table changes.

    Only rows moved to pending are queued.
    """

    row = _payload_record(
        payload
    )

    if (
        _clean(
            row.get("status")
        ).lower()
        != "pending"
    ):
        return

    _enqueue_account(
        _clean(
            row.get("account_id")
        )
    )


def _build_subscribe_callback():
    """
    The subscribe callback itself must stay synchronous.

    On SUBSCRIBED / re-SUBSCRIBED, queue one reconciliation read so a request
    created while the Mac was offline is not lost. There is still no timer.
    """

    def on_subscribe(
        status: Any,
        error: Any = None,
    ) -> None:
        status_text = _clean(
            getattr(
                status,
                "value",
                status,
            )
        ).lower()

        if "subscribed" in status_text:
            logger.info(
                "Supabase Realtime connected."
            )

            _enqueue_recovery()
            return

        if error:
            logger.warning(
                "Supabase Realtime status=%s error=%s",
                status,
                error,
            )

    return on_subscribe


async def recover_pending_requests(
    client: AsyncClient,
) -> None:
    """
    One tiny GET at startup/reconnect only.
    No polling loop.
    """

    response = await (
        client
        .table(SESSION_TABLE)
        .select("account_id")
        .eq("status", "pending")
        .order(
            "requested_at",
            desc=False,
        )
        .execute()
    )

    for row in list(
        response.data
        or []
    ):
        _enqueue_account(
            _clean(
                row.get("account_id")
            )
        )


async def claim_session_check(
    client: AsyncClient,
    *,
    account_id: str,
) -> bool:
    now = _utc_now_iso()

    response = await (
        client
        .table(SESSION_TABLE)
        .update(
            {
                "status": "checking",
                "checking_at": now,
                "last_error": None,
                "updated_at": now,
            }
        )
        .eq(
            "account_id",
            account_id,
        )
        .eq(
            "status",
            "pending",
        )
        .execute()
    )

    return bool(
        list(
            response.data
            or []
        )
    )


async def complete_session_check(
    client: AsyncClient,
    *,
    account_id: str,
    status: str,
    current_url: str | None,
    detail: str | None,
) -> None:
    now = _utc_now_iso()

    await (
        client
        .table(SESSION_TABLE)
        .update(
            {
                "status": status,
                "checked_at": now,
                "current_url": current_url,
                "last_error": (
                    detail
                    if status
                    in {
                        "unknown",
                        "failed",
                        "busy",
                        "checkpoint",
                    }
                    else None
                ),
                "updated_at": now,
            }
        )
        .eq(
            "account_id",
            account_id,
        )
        .execute()
    )


async def fail_session_check(
    client: AsyncClient,
    *,
    account_id: str,
    error: Exception,
) -> None:
    now = _utc_now_iso()

    await (
        client
        .table(SESSION_TABLE)
        .update(
            {
                "status": "failed",
                "checked_at": now,
                "last_error": (
                    str(error)[:2000]
                ),
                "updated_at": now,
            }
        )
        .eq(
            "account_id",
            account_id,
        )
        .execute()
    )


async def process_account(
    client: AsyncClient,
    pool: OutreachAccountPool,
    account_id: str,
) -> None:
    claimed = await claim_session_check(
        client,
        account_id=account_id,
    )

    if not claimed:
        return

    try:
        try:
            account = pool.get_account(account_id)
        except KeyError as exc:
            raise RuntimeError(
                f"{account_id} is not in this worker's configured accounts. "
                "Pull the latest code, check OUTREACH_ACCOUNT_IDS in .env "
                "or the shell environment, then restart the worker."
            ) from exc

        logger.info("Checking LinkedIn session: %s", account_id)
        # Playwright/browser manager in this repo is synchronous.
        # Run it off the asyncio event loop so the Realtime websocket stays
        # alive while Chromium is being checked.
        result = await asyncio.to_thread(
            check_outreach_account_session,
            account,
        )

        await complete_session_check(
            client,
            account_id=account_id,
            status=result.status,
            current_url=result.current_url,
            detail=result.detail,
        )

        logger.info(
            "Session check complete | account=%s | status=%s",
            account_id,
            result.status,
        )

    except Exception as exc:
        logger.exception(
            "Session check failed | account=%s",
            account_id,
        )

        await fail_session_check(
            client,
            account_id=account_id,
            error=exc,
        )


async def worker_loop(
    client: AsyncClient,
    pool: OutreachAccountPool,
) -> None:
    while True:
        queue = _get_work_queue()
        item = await queue.get()

        try:
            if item == _RECOVER_PENDING:
                await recover_pending_requests(
                    client
                )
                continue

            await process_account(
                client,
                pool,
                item,
            )

        except Exception:
            logger.exception("Session worker request failed | account=%s", item)

        finally:
            if item != _RECOVER_PENDING:
                _finish_account(
                    item
                )

            queue.task_done()


async def run_forever() -> None:
    global _work_queue

    # IMPORTANT: create asyncio primitives only after asyncio.run() has
    # created the active loop. This avoids cross-loop Future errors on
    # Python 3.9.
    _work_queue = asyncio.Queue()

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        ),
    )

    logging.getLogger(
        "httpx"
    ).setLevel(
        logging.WARNING
    )

    logging.getLogger(
        "httpcore"
    ).setLevel(
        logging.WARNING
    )

    client = await get_async_supabase_client()
    pool = OutreachAccountPool()

    logger.info(
        "Outreach Session Worker started — "
        "Async Realtime mode, no polling."
    )
    logger.info(
        "Configured Outreach accounts (%s): %s",
        len(pool.accounts),
        ", ".join(account.account_id for account in pool.accounts),
    )

    channel = (
        client
        .channel(
            "outreach-session-worker"
        )
        .on_postgres_changes(
            "*",
            schema="public",
            table=SESSION_TABLE,
            callback=(
                _handle_realtime_change
            ),
        )
    )

    try:
        await channel.subscribe(
            _build_subscribe_callback()
        )

        # Startup safety read. Queue de-duplication makes it harmless if the
        # SUBSCRIBED callback has already queued the same recovery.
        _enqueue_recovery()

        await worker_loop(
            client,
            pool,
        )

    finally:
        try:
            await client.remove_channel(
                channel
            )
        except Exception:
            pass


def main() -> None:
    try:
        asyncio.run(
            run_forever()
        )
    except KeyboardInterrupt:
        logger.info(
            "Outreach Session Worker stopped."
        )


if __name__ == "__main__":
    main()
