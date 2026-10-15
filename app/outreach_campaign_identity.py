"""Stable identity for a Connect campaign without a separate campaign table."""

from __future__ import annotations

import re
from datetime import datetime
from uuid import NAMESPACE_URL, uuid5
from zoneinfo import ZoneInfo


def canonical_campaign_name(name: str | None) -> str:
    """Collapse legacy date/run prefixes while retaining the actual campaign name."""
    cleaned = " ".join(str(name or "").split())
    while cleaned:
        without_date = re.sub(
            r"^(?:\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})\s*[-–—:]\s*",
            "", cleaned, count=1,
        )
        without_run = re.sub(
            r"^(?:lần|lan)\s*\d+\s*[-–—:]\s*",
            "", without_date, count=1, flags=re.IGNORECASE,
        )
        if not without_run or without_run == cleaned:
            break
        cleaned = without_run
    return cleaned


def campaign_id_for_name(name: str | None, *, connect_batch_id: str = "") -> str:
    """Give named campaigns one UUID; identify old unnamed runs separately."""
    normalized = canonical_campaign_name(name).casefold()
    if normalized:
        return str(uuid5(NAMESPACE_URL, f"linkedin-daily-scanner/campaign/{normalized}"))
    batch_id = str(connect_batch_id or "").strip()
    if batch_id:
        return str(uuid5(NAMESPACE_URL, f"linkedin-daily-scanner/legacy-connect-batch/{batch_id}"))
    return ""


def connect_batch_name(batch_name: str | None, created_at: str | None) -> str:
    """Use the run date for every legacy or unnamed Connect batch."""
    name = " ".join(str(batch_name or "").split())
    if name:
        return name
    try:
        created = datetime.fromisoformat(str(created_at or "").replace("Z", "+00:00"))
        if created.tzinfo is not None:
            return created.astimezone(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%d/%m/%Y")
    except ValueError:
        pass
    return "Unnamed batch"


def connect_batch_label(batch_name: str | None, campaign_name: str | None,
                        created_at: str | None) -> str:
    """Present a batch underneath its stable campaign identity."""
    name = connect_batch_name(batch_name, created_at)
    campaign = canonical_campaign_name(campaign_name)
    return f"{name} - {campaign}" if campaign else name
