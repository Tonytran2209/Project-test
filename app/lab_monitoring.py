"""Read-only monitoring report for AI Agent Lab (protocol app-monitoring-v1, profile-v1).

The Lab calls GET /internal/monitoring?days=N with a bearer token. The report holds
counts, durations and statuses only: no prospect names, profile URLs, message text or
account identifiers leave this service.
"""

from __future__ import annotations

import os
import platform
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterable

APP_ID = "outreach"
ROW_LIMIT = 1000
STARTED_AT = datetime.now(timezone.utc)
_STARTED_MONOTONIC = time.monotonic()


@dataclass(frozen=True)
class JobSource:
    key: str
    table: str
    job: str
    success: str
    failure: str
    start: str
    ends: tuple[str, ...]
    evidence: Callable[[dict], bool]


def _positive(field: str) -> Callable[[dict], bool]:
    return lambda row: _int(row.get(field)) > 0


JOB_SOURCES = (
    JobSource("connect", "outreach_jobs", "Connect batch", "completed", "failed",
              "started_at", ("completed_at",), _positive("processed_count")),
    JobSource("acceptance", "outreach_acceptance_checks", "Acceptance check", "completed", "failed",
              "started_at", ("completed_at",), lambda row: True),
    JobSource("messages", "outreach_message_batches", "Message batch", "completed", "failed",
              "started_at", ("completed_at",), _positive("sent_count")),
    JobSource("reply_send", "outreach_reply_send_jobs", "Reply send", "sent", "failed",
              "started_at", ("sent_at", "failed_at"), lambda row: bool(row.get("sent_at"))),
)

INVENTORY_LABELS = {
    "outreach_jobs": "Connect batches",
    "outreach_acceptance_checks": "Kiểm tra chấp nhận",
    "outreach_message_batches": "Batch tin nhắn",
    "outreach_reply_send_jobs": "Gửi trả lời",
    "outreach_account_sessions": "Phiên đăng nhập LinkedIn",
}

# Failures caused by infrastructure rather than by LinkedIn's answer or the input.
TECHNICAL = re.compile(
    r"timeout|timed out|network|connection|econn|socket|playwright|browser|navigation|"
    r"target closed|crash|traceback|exception|supabase|postgrest|http 5\d\d|internal server",
    re.IGNORECASE,
)


def _int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else None


def _end(row: dict, source: JobSource) -> datetime | None:
    for field in source.ends:
        parsed = _time(row.get(field))
        if parsed:
            return parsed
    return None


def job_history(sources: dict[str, list[dict] | None], since: datetime | None, truncated: set[str]) -> dict:
    """Terminal jobs (all sources) whose end falls on/after `since` (None = all saved history)."""
    executed = failed = technical = unclassified = valid = unverified = 0
    latest = None
    complete = not truncated
    for source in JOB_SOURCES:
        rows = sources.get(source.key)
        if rows is None:
            complete = False
            continue
        for row in rows:
            status = str(row.get("status") or "").lower()
            if status not in (source.success, source.failure):
                continue
            end = _end(row, source) or _time(row.get("updated_at"))
            if since and (not end or end < since):
                continue
            executed += 1
            if status == source.failure:
                failed += 1
                if TECHNICAL.search(str(row.get("last_error") or "")):
                    technical += 1
                else:
                    unclassified += 1
            elif source.evidence(row):
                valid += 1
            else:
                unverified += 1
            start, finished = _time(row.get(source.start)), _end(row, source)
            if start and finished and finished >= start and (latest is None or finished > latest[0]):
                latest = (finished, source.job, (finished - start).total_seconds() * 1000)
    return {
        "executed": executed,
        "failed": failed,
        "technicalErrors": technical,
        "unclassifiedFailures": unclassified,
        "validCompletions": valid,
        "unverifiedCompletions": unverified,
        "complete": complete,
        "latestJob": None if latest is None else {
            "job": latest[1], "durationMs": round(latest[2]), "completedAt": latest[0].isoformat(),
        },
    }


def _status_counts(rows: Iterable[dict]) -> list[dict]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status") or "unknown").lower()
        counts[status] = counts.get(status, 0) + 1
    return [{"status": k, "count": v} for k, v in sorted(counts.items(), key=lambda kv: -kv[1])]


def _in_window(row: dict, since: datetime, *fields: str) -> bool:
    for field in fields:
        parsed = _time(row.get(field))
        if parsed:
            return parsed >= since
    return False


def _sum(rows: Iterable[dict], field: str) -> int:
    return sum(_int(row.get(field)) for row in rows)


def _minutes(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return round(ordered[min(len(ordered) - 1, int(0.95 * len(ordered)))] / 60000, 2)


def build_profile(sources: dict[str, list[dict] | None], sessions: list[dict] | None,
                  workers: dict | None, since: datetime, days: int) -> dict:
    def rows(key: str) -> list[dict]:
        return sources.get(key) or []

    def window(key: str, *fields: str) -> list[dict]:
        return [r for r in rows(key) if _in_window(r, since, *fields)]

    connect = window("connect", "completed_at", "created_at")
    messages = window("messages", "completed_at", "created_at")
    replies = window("reply_send", "sent_at", "failed_at", "created_at")
    acceptance = window("acceptance", "completed_at", "created_at")
    period = f"{days} ngày gần nhất (UTC)"

    def unknown(key: str) -> bool:
        return sources.get(key) is None

    def value(key: str, number: int) -> int | None:
        return None if unknown(key) else number

    durations = []
    for source in JOB_SOURCES:
        values = []
        for row in window(source.key, *source.ends, "created_at"):
            start, end = _time(row.get(source.start)), _end(row, source)
            if start and end and end >= start and str(row.get("status") or "").lower() == source.success:
                values.append((end - start).total_seconds() * 1000)
        durations.append([source.job, len(values), _minutes(values)])

    connect_sent = _sum(connect, "success_count")
    connect_processed = _sum(connect, "processed_count")
    sections = [
        {
            "id": "funnel",
            "title": "Phễu outreach",
            "description": "Tổng theo job kết thúc trong " + period + ". Số người, không phải số job.",
            "metrics": [
                {"label": "Lời mời connect đã gửi", "value": value("connect", connect_sent)},
                {"label": "Hồ sơ đã xử lý (connect)", "value": value("connect", connect_processed)},
                {"label": "Tỷ lệ gửi connect thành công", "format": "percent",
                 "value": None if unknown("connect") or not connect_processed
                 else round(100 * connect_sent / connect_processed, 1)},
                {"label": "Tin nhắn đã gửi", "value": value("messages", _sum(messages, "sent_count"))},
                {"label": "Tin nhắn lỗi", "value": value("messages", _sum(messages, "failed_count")),
                 "tone": "warning" if _sum(messages, "failed_count") else None},
                {"label": "Trả lời đã gửi", "value": value(
                    "reply_send", sum(1 for r in replies if str(r.get("status")).lower() == "sent"))},
            ],
        },
        {
            "id": "durations",
            "title": "Thời gian chạy theo loại job",
            "description": "P95 từ started_at đến lúc kết thúc, chỉ job thành công trong " + period + ".",
            "table": {"columns": ["Job", "Số job đo được", "P95 (phút)"], "rows": durations},
        },
    ]
    if sessions is not None:
        statuses = {s["status"]: s["count"] for s in _status_counts(sessions)}
        blocked = statuses.get("logged_out", 0) + statuses.get("checkpoint", 0) + statuses.get("failed", 0)
        sections.append({
            "id": "accounts",
            "title": "Tài khoản LinkedIn",
            "description": "Trạng thái phiên đăng nhập hiện tại của các tài khoản chạy outreach.",
            "metrics": [
                {"label": "Đang đăng nhập", "value": statuses.get("logged_in", 0),
                 "tone": "success" if statuses.get("logged_in") else "warning"},
                {"label": "Cần xử lý (đăng xuất / checkpoint / lỗi)", "value": blocked,
                 "tone": "error" if blocked else "success"},
                {"label": "Đang kiểm tra hoặc chờ", "value": statuses.get("checking", 0) + statuses.get("pending", 0)},
                {"label": "Tổng tài khoản", "value": len(sessions)},
            ],
        })
    if workers is not None:
        sections.append({
            "id": "workers",
            "title": "Worker đang chạy",
            "description": "Tác vụ có tín hiệu trong 30 phút gần nhất (reply check: 2 phút).",
            "table": {
                "columns": ["Tác vụ", "Đang chạy"],
                "rows": [[t.get("label") or t.get("key"), t.get("count")] for t in workers.get("tasks", [])],
            },
        })

    return {
        "version": "profile-v1",
        "jobTargets": _job_targets(),
        "inventoryLabels": INVENTORY_LABELS,
        "mainJob": {
            "title": "Outreach LinkedIn theo campaign",
            "steps": ["Gửi lời mời connect", "Kiểm tra chấp nhận", "Gửi tin nhắn", "Kiểm tra và gửi trả lời"],
            "metrics": [
                {"label": "Connect batch kết thúc", "value": value("connect", len(connect))},
                {"label": "Lượt kiểm tra chấp nhận", "value": value("acceptance", len(acceptance))},
                {"label": "Batch tin nhắn kết thúc", "value": value("messages", len(messages))},
                {"label": "Lượt gửi trả lời", "value": value("reply_send", len(replies))},
            ],
            "note": "Đếm job kết thúc trong " + period + ". Thời gian chạy phụ thuộc giới hạn an toàn của LinkedIn.",
        },
        "sections": sections,
    }


def _job_targets() -> dict:
    """Optional targets in minutes, e.g. LAB_JOB_TARGETS_MINUTES='{"Connect batch": 30}'."""
    import json

    try:
        raw = json.loads(os.getenv("LAB_JOB_TARGETS_MINUTES", "") or "{}")
    except ValueError:
        return {}
    known = {s.job for s in JOB_SOURCES}
    return {k: v for k, v in raw.items() if k in known and isinstance(v, (int, float)) and v > 0} if isinstance(raw, dict) else {}


def _rss_bytes() -> int | None:
    try:
        with open("/proc/self/status", encoding="utf8") as status:
            for line in status:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


_SECRETISH = re.compile(r"(eyJ[\w-]{10,}|sb_[\w-]{10,}|[A-Za-z0-9_\-]{32,}|(?:key|token|secret|password)\s*[:=]\s*\S+)", re.IGNORECASE)


def safe_reason(error: BaseException) -> str:
    """Short, secret-free reason: exception type, PostgREST code and message (names only, no data)."""
    code = getattr(error, "code", None)
    message = getattr(error, "message", None) or str(error)
    text = " ".join(str(part) for part in (type(error).__name__ + ":", code, message) if part)
    return _SECRETISH.sub("[ẩn]", text)[:200]


def _fetch(client, table: str) -> tuple[list[dict] | None, bool, str | None]:
    if client is None:
        return None, False, "Không có Supabase client"
    try:
        response = client.table(table).select("*").order("created_at", desc=True).limit(ROW_LIMIT).execute()
    except Exception as error:
        return None, False, safe_reason(error)
    data = list(response.data or [])
    return data, len(data) >= ROW_LIMIT, None


def build_report(client, days: int, *, worker_activity: Callable[[], dict] | None = None,
                 now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
                 client_error: str | None = None) -> dict:
    current = now()
    since = datetime(current.year, current.month, current.day, tzinfo=timezone.utc) - timedelta(days=days - 1)

    db_start = time.monotonic()
    sources: dict[str, list[dict] | None] = {}
    truncated: set[str] = set()
    errors: dict[str, str] = {}
    for source in JOB_SOURCES:
        rows, cut, error = _fetch(client, source.table)
        sources[source.key] = rows
        if cut:
            truncated.add(source.key)
        if error:
            errors[source.table] = error
    db_ms = round((time.monotonic() - db_start) * 1000 / len(JOB_SOURCES))
    sessions, _, session_error = _fetch(client, "outreach_account_sessions")
    if session_error:
        errors["outreach_account_sessions"] = session_error
    try:
        workers = worker_activity() if worker_activity and client is not None else None
    except Exception as error:
        workers = None
        errors["outreach_worker_activity"] = safe_reason(error)

    reachable = [k for k, v in sources.items() if v is not None]
    inventory = {source.table: (None if sources[source.key] is None else _status_counts(sources[source.key]))
                 for source in JOB_SOURCES}
    inventory["outreach_account_sessions"] = None if sessions is None else _status_counts(sessions)

    return {
        "protocol": "app-monitoring-v1",
        "appId": APP_ID,
        "generatedAt": current.isoformat(),
        "window": {"days": days, "start": since.isoformat(), "end": current.isoformat()},
        "runtime": {
            "cpuPercent": None,
            "rssBytes": _rss_bytes(),
            "heapUsedBytes": None,
            "heapTotalBytes": None,
            "uptimeSeconds": round(time.monotonic() - _STARTED_MONOTONIC),
            "startedAt": STARTED_AT.isoformat(),
            "runtimeVersion": "Python " + platform.python_version(),
            "commit": os.getenv("RAILWAY_GIT_COMMIT_SHA") or None,
        },
        "database": {
            "status": "ready" if len(reachable) == len(JOB_SOURCES) else "degraded",
            "responseMs": db_ms if reachable else None,
            "error": client_error or (next(iter(errors.values())) if errors else None),
        },
        "jobHistory": job_history(sources, since, truncated),
        "jobHistoryAllTime": job_history(sources, None, truncated),
        "inventory": inventory,
        "profile": _with_diagnostics(build_profile(sources, sessions, workers, since, days), client_error, errors),
    }


def _with_diagnostics(profile: dict, client_error: str | None, errors: dict[str, str]) -> dict:
    """Show why data is missing, first, so 'no data' is never mistaken for zero activity."""
    if not client_error and not errors:
        return profile
    rows = [["Supabase client", client_error]] if client_error else []
    rows += [[table, reason] for table, reason in errors.items()]
    profile["sections"].insert(0, {
        "id": "diagnostics",
        "title": "Chưa đọc được dữ liệu",
        "description": "Các nguồn dưới đây lỗi nên số liệu liên quan hiển thị 'Chưa có dữ liệu' thay vì 0.",
        "table": {"columns": ["Nguồn", "Lý do"], "rows": rows[:12]},
    })
    return profile
