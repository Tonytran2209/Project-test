from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from supabase import Client

from app.outreach_account_pool import (
    DEFAULT_OUTREACH_ACCOUNT_IDS,
    OUTREACH_ACCOUNT_DISPLAY_NAMES,
)
from app.outreach_campaign_identity import campaign_id_for_name, connect_batch_label
from app.outreach_dashboard_store import get_outreach_client
from app.outreach_reply_direction import profile_slug_key


REPLY_TABLE = "outreach_reply_messages"
MESSAGE_TARGET_TABLE = "outreach_message_targets"
MESSAGE_BATCH_TABLE = "outreach_message_batches"
CONNECT_TARGET_TABLE = "outreach_job_targets"
CONNECT_JOB_TABLE = "outreach_jobs"


class OutreachReplyStoreError(RuntimeError):
    pass


def _safe_text(value) -> str:
    return str(value or "").strip()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _message_fingerprint(
    *,
    sent_target_id: str,
    assigned_account_id: str,
    linkedin_url: str,
    message_text: str,
    linkedin_message_time: str,
) -> str:
    source = "\n".join(
        (
            _safe_text(sent_target_id),
            _safe_text(assigned_account_id),
            _safe_text(linkedin_url),
            " ".join(_safe_text(message_text).split()),
            _safe_text(linkedin_message_time),
        )
    )
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def prune_stale_outreach_replies(
    scan_started_at: str, *, client: Client | None = None,
) -> int:
    """Atomically remove replies absent from a successful full Unread scan.

    The database function excludes every reply with a linked send job, so a
    concurrent queue operation cannot lose its parent row through CASCADE.
    """
    if not _safe_text(scan_started_at):
        raise OutreachReplyStoreError("scan_started_at is required for pruning.")
    response = (client or get_outreach_client()).rpc(
        "prune_stale_outreach_replies",
        {"p_scan_started_at": scan_started_at},
    ).execute()
    try:
        return int(response.data)
    except (TypeError, ValueError) as exc:
        raise OutreachReplyStoreError("Reply pruning did not return a count.") from exc


def save_outreach_reply(
    *,
    sent_target_id: str,
    prospect_id: str,
    assigned_account_id: str,
    user_name: str,
    linkedin_url: str,
    thread_url: str = "",
    message_text: str,
    linkedin_message_time: str = "",
    conversation_messages: list[dict] | None = None,
    match_reason: str = "",
    match_similarity: float = 0.0,
    client: Client | None = None,
) -> dict:
    """Persist a complete Unread thread, with or without an Outreach target."""

    cleaned_target_id = _safe_text(sent_target_id)
    cleaned_name = _safe_text(user_name)
    cleaned_url = _safe_text(linkedin_url)
    cleaned_thread_url = _safe_text(thread_url).split("?", 1)[0]
    cleaned_message = " ".join(_safe_text(message_text).split())
    cleaned_message_time = _safe_text(linkedin_message_time)

    cleaned_account = _safe_text(assigned_account_id)
    if cleaned_account not in DEFAULT_OUTREACH_ACCOUNT_IDS:
        raise OutreachReplyStoreError("A valid assigned_account_id is required.")
    if not cleaned_name:
        raise OutreachReplyStoreError("user_name is required.")
    if not cleaned_url:
        raise OutreachReplyStoreError("linkedin_url is required.")
    if not list(conversation_messages or []):
        raise OutreachReplyStoreError("A captured conversation is required.")

    active_client = client or get_outreach_client()
    existing_rows: list[dict] = []
    if cleaned_target_id:
        target_response = (
            active_client.table(REPLY_TABLE).select("*")
            .eq("sent_target_id", cleaned_target_id)
            .order("captured_at", desc=True).limit(1).execute()
        )
        existing_rows = list(target_response.data or [])
    if not existing_rows:
        if cleaned_thread_url:
            thread_response = (
                active_client.table(REPLY_TABLE).select("*")
                .eq("assigned_account_id", cleaned_account)
                .eq("thread_url", cleaned_thread_url)
                .order("captured_at", desc=True).limit(1).execute()
            )
            existing_rows = list(thread_response.data or [])
    if not existing_rows:
        url_response = (
            active_client.table(REPLY_TABLE).select("*")
            .eq("assigned_account_id", cleaned_account)
            .eq("linkedin_url", cleaned_url)
            .order("captured_at", desc=True).limit(1).execute()
        )
        existing_rows = list(url_response.data or [])
    existing = dict(existing_rows[0]) if existing_rows else {}
    effective_target = cleaned_target_id or _safe_text(existing.get("sent_target_id"))
    effective_url = cleaned_url
    if (
        existing
        and (not cleaned_target_id or not profile_slug_key(cleaned_url))
        and profile_slug_key(existing.get("linkedin_url"))
    ):
        effective_url = _safe_text(existing.get("linkedin_url"))
    fingerprint = _message_fingerprint(
        sent_target_id=effective_target,
        assigned_account_id=cleaned_account,
        linkedin_url=effective_url,
        message_text=cleaned_message,
        linkedin_message_time=cleaned_message_time,
    )
    if existing_rows:
        updates = {
            "sent_target_id": effective_target or None,
            "prospect_id": _safe_text(prospect_id) or existing.get("prospect_id"),
            "assigned_account_id": cleaned_account,
            "user_name": cleaned_name,
            "linkedin_url": effective_url,
            "thread_url": cleaned_thread_url or existing.get("thread_url"),
            "message_text": cleaned_message,
            "linkedin_message_time": cleaned_message_time or None,
            "conversation_messages": list(conversation_messages or []),
            "match_reason": (
                _safe_text(match_reason)
                if cleaned_target_id else _safe_text(existing.get("match_reason"))
            ) or None,
            "match_similarity": max(
                0.0,
                min(1.0, float(
                    match_similarity if cleaned_target_id
                    else existing.get("match_similarity") or 0.0
                )),
            ),
            "message_fingerprint": fingerprint,
            "captured_at": _utc_now(),
        }
        update_response = (
            active_client.table(REPLY_TABLE)
            .update(updates)
            .eq("id", existing.get("id"))
            .execute()
        )
        updated_rows = list(update_response.data or [])
        if updated_rows:
            return dict(updated_rows[0])
        existing.update(updates)
        return existing

    payload = {
        "sent_target_id": cleaned_target_id or None,
        "prospect_id": _safe_text(prospect_id) or None,
        "assigned_account_id": cleaned_account,
        "user_name": cleaned_name,
        "linkedin_url": cleaned_url,
        "thread_url": cleaned_thread_url or None,
        "message_text": cleaned_message,
        "linkedin_message_time": cleaned_message_time or None,
        "conversation_messages": list(conversation_messages or []),
        "match_reason": _safe_text(match_reason) or None,
        "match_similarity": max(0.0, min(1.0, float(match_similarity or 0.0))),
        "message_fingerprint": fingerprint,
        "captured_at": _utc_now(),
    }

    response = active_client.table(REPLY_TABLE).insert(payload).execute()
    rows = list(response.data or [])
    return dict(rows[0]) if rows else payload


REPLY_SELECT_FIELDS = (
    "id,sent_target_id,prospect_id,assigned_account_id,"
    "user_name,linkedin_url,message_text,linkedin_message_time,"
    "conversation_messages,match_reason,match_similarity,captured_at"
)


def get_outreach_reply_revision(
    *, client: Client | None = None, active_since: str | None = None,
) -> str | None:
    """Return a cheap change marker for the most recently captured conversation."""
    active_client = client or get_outreach_client()
    query = (
        active_client.table(REPLY_TABLE)
        .select("id,captured_at")
    )
    if active_since:
        query = query.gte("captured_at", active_since)
    response = (
        query
        .order("captured_at", desc=True)
        .order("id", desc=True)
        .limit(1)
        .execute()
    )
    rows = list(response.data or [])
    if not rows:
        return None
    row = rows[0]
    return f"{_safe_text(row.get('captured_at'))}:{_safe_text(row.get('id'))}"


def _attach_batch_codes(replies: list[dict], active_client: Client) -> None:
    """Resolve message batch and original Connect campaign for each reply."""
    target_ids = [
        _safe_text(reply.get("sent_target_id"))
        for reply in replies
        if _safe_text(reply.get("sent_target_id"))
    ]
    target_to_batch: dict[str, str] = {}
    target_to_source: dict[str, str] = {}
    batch_codes: dict[str, str] = {}

    if target_ids:
        target_response = (
            active_client.table(MESSAGE_TARGET_TABLE)
            .select("id,batch_id,source_target_id")
            .in_("id", target_ids)
            .execute()
        )
        for target in list(target_response.data or []):
            target_id = _safe_text(target.get("id"))
            batch_id = _safe_text(target.get("batch_id"))
            if target_id and batch_id:
                target_to_batch[target_id] = batch_id
            if target_id:
                target_to_source[target_id] = _safe_text(target.get("source_target_id"))

        unique_batch_ids = list(dict.fromkeys(target_to_batch.values()))
        if unique_batch_ids:
            batch_response = (
                active_client.table(MESSAGE_BATCH_TABLE)
                .select("id,batch_code")
                .in_("id", unique_batch_ids)
                .execute()
            )
            for batch in list(batch_response.data or []):
                batch_id = _safe_text(batch.get("id"))
                batch_code = _safe_text(batch.get("batch_code"))
                if batch_id and batch_code:
                    batch_codes[batch_id] = batch_code

    source_to_connect_batch: dict[str, str] = {}
    source_ids = list(dict.fromkeys(source_id for source_id in target_to_source.values() if source_id))
    if source_ids:
        source_response = (
            active_client.table(CONNECT_TARGET_TABLE)
            .select("id,job_id")
            .in_("id", source_ids)
            .execute()
        )
        for source in list(source_response.data or []):
            source_to_connect_batch[_safe_text(source.get("id"))] = _safe_text(source.get("job_id"))

    connect_batch_ids = list(dict.fromkeys(
        job_id for job_id in source_to_connect_batch.values() if job_id
    ))
    connect_jobs: dict[str, dict] = {}
    if connect_batch_ids:
        job_response = (
            active_client.table(CONNECT_JOB_TABLE)
            .select("id,job_code,display_name,batch_name,created_at")
            .in_("id", connect_batch_ids)
            .execute()
        )
        for job in list(job_response.data or []):
            connect_jobs[_safe_text(job.get("id"))] = job

    for reply in replies:
        sent_target_id = _safe_text(reply.get("sent_target_id"))
        batch_id = target_to_batch.get(sent_target_id, "")
        reply["message_batch_code"] = batch_codes.get(batch_id) or None
        connect_batch_id = source_to_connect_batch.get(target_to_source.get(sent_target_id, ""), "")
        connect_job = connect_jobs.get(connect_batch_id, {})
        campaign_name = _safe_text(connect_job.get("display_name"))
        reply["connect_batch_id"] = connect_batch_id
        reply["connect_batch_code"] = _safe_text(connect_job.get("job_code"))
        reply["connect_batch_label"] = connect_batch_label(
            connect_job.get("batch_name"), campaign_name, connect_job.get("created_at")
        ) if connect_job else ""
        reply["campaign_id"] = campaign_id_for_name(
            campaign_name, connect_batch_id=connect_batch_id
        )
        reply["campaign_name"] = campaign_name


def list_outreach_reply_page(
    *,
    account_id: str,
    offset: int = 0,
    limit: int = 20,
    client: Client | None = None,
    active_since: str | None = None,
) -> dict:
    """Fetch a stable page of raw reply rows for one account."""
    cleaned_account_id = _safe_text(account_id)
    if cleaned_account_id not in DEFAULT_OUTREACH_ACCOUNT_IDS:
        raise OutreachReplyStoreError("Unknown Outreach account.")
    safe_offset = max(0, int(offset))
    safe_limit = max(1, min(int(limit), 50))
    active_client = client or get_outreach_client()
    query = (
        active_client.table(REPLY_TABLE)
        .select(REPLY_SELECT_FIELDS)
        .eq("assigned_account_id", cleaned_account_id)
    )
    if active_since:
        query = query.gte("captured_at", active_since)
    response = (
        query
        .order("captured_at", desc=True)
        .order("id", desc=True)
        .range(safe_offset, safe_offset + safe_limit)
        .execute()
    )
    fetched = [dict(row) for row in list(response.data or [])]
    replies = fetched[:safe_limit]
    _attach_batch_codes(replies, active_client)
    return {
        "replies": replies,
        "next_offset": safe_offset + len(replies),
        "has_more": len(fetched) > safe_limit,
    }


def list_recent_outreach_replies(
    *,
    limit: int = 50,
    client: Client | None = None,
) -> list[dict]:
    """Return the newest reply for each of up to ``limit`` people."""

    safe_limit = max(1, min(int(limit or 50), 100))
    active_client = client or get_outreach_client()
    response = (
        active_client.table(REPLY_TABLE)
        .select(REPLY_SELECT_FIELDS)
        .order("captured_at", desc=True)
        .limit(max(50, safe_limit * 10))
        .execute()
    )

    replies: list[dict] = []
    seen_people: set[str] = set()

    for raw_row in list(response.data or []):
        row = dict(raw_row)
        account_identity = _safe_text(
            row.get("assigned_account_id")
        ).casefold()
        person_identity = _safe_text(row.get("linkedin_url")).casefold()
        if person_identity:
            identity = "|".join((account_identity, person_identity))
        else:
            identity = "|".join(
                (
                    account_identity,
                    _safe_text(row.get("user_name")).casefold(),
                )
            )

        if identity in seen_people:
            continue

        seen_people.add(identity)
        replies.append(row)

        if len(replies) >= safe_limit:
            break

    _attach_batch_codes(replies, active_client)
    return replies


def list_outreach_reply_accounts(
    *,
    client: Client | None = None,
    include_counts: bool = False,
    active_since: str | None = None,
) -> list[dict]:
    """Return registered Outreach accounts with their display names."""

    accounts = [
        {
            "account_id": account_id,
            "display_name": OUTREACH_ACCOUNT_DISPLAY_NAMES.get(
                account_id,
                account_id,
            ),
        }
        for account_id in DEFAULT_OUTREACH_ACCOUNT_IDS
    ]
    if include_counts:
        active_client = client or get_outreach_client()
        for account in accounts:
            query = (
                active_client.table(REPLY_TABLE)
                .select("id", count="exact", head=True)
                .eq("assigned_account_id", account["account_id"])
            )
            if active_since:
                query = query.gte("captured_at", active_since)
            response = (
                query
                .execute()
            )
            account["reply_count"] = int(response.count or 0)
    return accounts
