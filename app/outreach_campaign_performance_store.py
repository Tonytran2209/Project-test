"""Read-only campaign cohorts across Connect, Messages, and Replies."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from supabase import Client

from app.outreach_campaign_identity import (
    campaign_id_for_name, canonical_campaign_name, connect_batch_label,
    connect_batch_name,
)
from app.outreach_dashboard_store import get_outreach_client
from app.outreach_reply_direction import profile_slug_key


WINDOW_DAYS = {"1d": 1, "7d": 7, "30d": 30, "all": None}
REPLY_COUNT_START = datetime(2026, 10, 12, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
PAGE_SIZE = 500
IN_CHUNK_SIZE = 100


def _text(value) -> str:
    return str(value or "").strip()


def _timestamp(value) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(_text(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else None
    except ValueError:
        return None


def _verified_reply(conversation_messages) -> tuple[bool, set[str]]:
    """Require an incoming bubble after the last verified own bubble."""
    if not isinstance(conversation_messages, list):
        return False, set()
    own_indexes = [index for index, event in enumerate(conversation_messages)
                   if isinstance(event, dict) and event.get("sender_type") == "own"]
    if not own_indexes:
        return False, set()
    last_own = own_indexes[-1]
    own_texts = {" ".join(_text(conversation_messages[last_own].get("text")).split())}
    return any(
        isinstance(event, dict)
        and event.get("sender_type") == "incoming"
        and _text(event.get("text"))
        for event in conversation_messages[last_own + 1:]
    ), own_texts


def _chunks(values: list[str]):
    for index in range(0, len(values), IN_CHUNK_SIZE):
        yield values[index:index + IN_CHUNK_SIZE]


def _fetch_pages(query) -> list[dict]:
    rows: list[dict] = []
    offset = 0
    while True:
        response = query.range(offset, offset + PAGE_SIZE - 1).execute()
        page = list(response.data or [])
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            return rows
        offset += PAGE_SIZE


def _fetch_related(client: Client, table: str, fields: str,
                   foreign_key: str, ids: list[str], status: str = "",
                   created_since: str = "") -> list[dict]:
    rows: list[dict] = []
    for chunk in _chunks(ids):
        query = client.table(table).select(fields).in_(foreign_key, chunk).order("id")
        if status:
            query = query.eq("status", status)
        if created_since:
            query = query.gte("created_at", created_since)
        rows.extend(_fetch_pages(query))
    return rows


def aggregate_campaign_performance(jobs: list[dict], connect_targets: list[dict],
                                   sent_targets: list[dict], replies: list[dict]) -> list[dict]:
    """Count distinct prospects; only first-recorded replies after the reset qualify."""
    campaigns: dict[str, dict] = {}
    batch_by_id: dict[str, dict] = {}
    campaign_by_batch: dict[str, dict] = {}
    for job in sorted(jobs, key=lambda item: _text(item.get("created_at")), reverse=True):
        batch_id = _text(job.get("id"))
        if not batch_id:
            continue
        name = canonical_campaign_name(job.get("display_name"))
        campaign_id = campaign_id_for_name(name, connect_batch_id=batch_id)
        campaign = campaigns.setdefault(campaign_id, {
            "campaign_id": campaign_id,
            "campaign_name": name or "Unnamed campaign",
            "batches": [],
            "accounts": [], "_accounts": {},
            "_added": set(), "_messaged": set(), "_replied": set(),
        })
        batch = {
            "batch_id": batch_id,
            "batch_code": _text(job.get("job_code")) or batch_id,
            "batch_name": connect_batch_name(job.get("batch_name"), job.get("created_at")),
            "batch_label": connect_batch_label(
                job.get("batch_name"), job.get("display_name"), job.get("created_at")
            ),
            "created_at": job.get("created_at"),
            "_added": set(), "_messaged": set(), "_replied": set(),
        }
        campaign["batches"].append(batch)
        batch_by_id[batch_id] = batch
        campaign_by_batch[batch_id] = campaign

    def account_bucket(batch_id: str, account_id: str) -> dict:
        campaign = campaign_by_batch[batch_id]
        account_key = account_id or "unassigned"
        return campaign["_accounts"].setdefault(account_key, {
            "account_id": account_key,
            "_added": set(), "_messaged": set(), "_replied": set(),
        })

    connect_by_target: dict[str, tuple[str, str, str]] = {}
    for target in connect_targets:
        target_id = _text(target.get("id"))
        batch_id = _text(target.get("job_id"))
        batch = batch_by_id.get(batch_id)
        if not target_id or not batch:
            continue
        person_id = _text(target.get("prospect_id")) or target_id
        account_id = _text(target.get("assigned_account_id"))
        connect_by_target[target_id] = (batch_id, person_id, account_id)
        batch["_added"].add(person_id)
        account_bucket(batch_id, account_id)["_added"].add(person_id)

    sent_by_profile: dict[tuple[str, str], list[dict]] = {}
    for target in sent_targets:
        source = connect_by_target.get(_text(target.get("source_target_id")))
        sent_id = _text(target.get("id"))
        if not source or not sent_id:
            continue
        batch_id, person_id, connect_account_id = source
        account_id = _text(target.get("assigned_account_id")) or connect_account_id
        profile_key = profile_slug_key(target.get("linkedin_url"))
        batch_by_id[batch_id]["_messaged"].add(person_id)
        account_bucket(batch_id, account_id)["_messaged"].add(person_id)
        sent_record = {
            "id": sent_id, "batch_id": batch_id, "person_id": person_id,
            "account_id": account_id, "profile_key": profile_key,
            "message_text": " ".join(_text(target.get("message_text")).split()),
            "completed_at": _timestamp(target.get("completed_at")),
        }
        if profile_key and account_id:
            sent_by_profile.setdefault((account_id, profile_key), []).append(sent_record)

    for reply in replies:
        first_recorded = _timestamp(reply.get("created_at"))
        if first_recorded is None or first_recorded < REPLY_COUNT_START:
            continue
        verified, own_texts = _verified_reply(reply.get("conversation_messages"))
        if not verified:
            continue
        profile_key = profile_slug_key(reply.get("linkedin_url"))
        account_id = _text(reply.get("assigned_account_id"))
        if not profile_key or not account_id:
            continue
        candidates = [candidate for candidate in sent_by_profile.get((account_id, profile_key), [])
                      if candidate["completed_at"] is None or candidate["completed_at"] <= first_recorded]
        if not candidates:
            continue
        exact_text = [candidate for candidate in candidates
                      if len(candidate["message_text"]) >= 20 and candidate["message_text"] in own_texts]
        if len(exact_text) == 1:
            resolved = exact_text[0]
        elif len(candidates) == 1:
            resolved = candidates[0]
        elif len({(candidate["batch_id"], candidate["person_id"]) for candidate in candidates}) == 1:
            resolved = candidates[0]
        else:
            # The worker may have linked the newest sent target by URL alone.
            # Without matching the last own message, that ID is not proof of batch.
            continue
        batch_id = resolved["batch_id"]
        person_id = resolved["person_id"]
        batch_by_id[batch_id]["_replied"].add(person_id)
        account_bucket(batch_id, account_id)["_replied"].add(person_id)

    results: list[dict] = []
    for campaign in campaigns.values():
        for batch in campaign["batches"]:
            for metric in ("added", "messaged", "replied"):
                campaign[f"_{metric}"].update(batch[f"_{metric}"])
                batch[metric if metric != "replied" else "replies"] = len(batch.pop(f"_{metric}"))
            batch["reply_rate"] = round(100 * batch["replies"] / batch["messaged"], 1) if batch["messaged"] else 0.0
        for metric in ("added", "messaged", "replied"):
            campaign[metric if metric != "replied" else "replies"] = len(campaign.pop(f"_{metric}"))
        campaign["reply_rate"] = round(100 * campaign["replies"] / campaign["messaged"], 1) if campaign["messaged"] else 0.0
        for account in campaign.pop("_accounts").values():
            for metric in ("added", "messaged", "replied"):
                account[metric if metric != "replied" else "replies"] = len(account.pop(f"_{metric}"))
            account["reply_rate"] = round(100 * account["replies"] / account["messaged"], 1) if account["messaged"] else 0.0
            campaign["accounts"].append(account)
        campaign["accounts"].sort(key=lambda account: (-account["messaged"], account["account_id"]))
        campaign["batches"].sort(key=lambda batch: _text(batch["created_at"]), reverse=True)
        campaign["batch_ids"] = [batch["batch_code"] for batch in campaign["batches"]]
        results.append(campaign)
    return sorted(results, key=lambda campaign: _text(campaign["batches"][0]["created_at"]), reverse=True)


def get_campaign_performance(window: str = "all", *, client: Client | None = None) -> list[dict]:
    if window not in WINDOW_DAYS:
        raise ValueError("Unsupported campaign timeframe.")
    active_client = client or get_outreach_client()
    query = active_client.table("outreach_jobs").select(
        "id,job_code,display_name,batch_name,created_at"
    ).eq("job_type", "connect").order("id")
    days = WINDOW_DAYS[window]
    if days is not None:
        cutoff = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")) - timedelta(days=days)
        query = query.gte("created_at", cutoff.isoformat())
    jobs = _fetch_pages(query)
    job_ids = [_text(job.get("id")) for job in jobs if _text(job.get("id"))]
    if not job_ids:
        return []
    connect_targets = _fetch_related(
        active_client, "outreach_job_targets", "id,job_id,prospect_id,assigned_account_id", "job_id", job_ids
    )
    source_ids = [_text(row.get("id")) for row in connect_targets if _text(row.get("id"))]
    sent_targets = _fetch_related(
        active_client, "outreach_message_targets", "id,source_target_id,assigned_account_id,linkedin_url,message_text,completed_at", "source_target_id", source_ids,
        status="sent",
    )
    sent_account_ids = sorted({_text(row.get("assigned_account_id")) for row in sent_targets
                               if _text(row.get("assigned_account_id"))})
    replies = _fetch_pages(
        active_client.table("outreach_reply_messages")
        .select("id,sent_target_id,assigned_account_id,linkedin_url,conversation_messages,created_at")
        .gte("created_at", REPLY_COUNT_START.isoformat())
        .in_("assigned_account_id", sent_account_ids)
        .order("id")
    ) if sent_account_ids else []
    return aggregate_campaign_performance(jobs, connect_targets, sent_targets, replies)
