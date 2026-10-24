"""Conservative sender classification for LinkedIn conversation snapshots."""

from __future__ import annotations

import unicodedata
from urllib.parse import unquote, urlparse


def profile_slug_key(linkedin_url: object) -> str:
    """Compare absolute or relative LinkedIn member links without tracking."""
    try:
        value = str(linkedin_url or "").strip()
        parsed = urlparse(value)
        if parsed.hostname:
            hostname = parsed.hostname.casefold()
            if hostname != "linkedin.com" and not hostname.endswith(".linkedin.com"):
                return ""
        elif not value.startswith("/"):
            return ""
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) != 2 or parts[0].casefold() != "in":
            return ""
        return unquote(parts[1]).casefold()
    except Exception:
        return ""


def sent_target_from_own_messages(
    events: list[dict], sent_profiles: list[dict],
) -> dict | None:
    """Match a thread only to a unique, sufficiently specific sent message."""
    by_text: dict[str, list[dict]] = {}
    for profile in sent_profiles:
        text = " ".join(str(profile.get("message_text") or "").split())
        if len(text) >= 20:
            by_text.setdefault(text, []).append(profile)
    for event in events:
        if not event.get("is_own_message"):
            continue
        text = " ".join(str(event.get("text") or "").split())
        candidates = by_text.get(text, [])
        if not candidates:
            continue
        profile_keys = {
            profile_slug_key(candidate.get("linkedin_url"))
            for candidate in candidates
        }
        if len(profile_keys) == 1 and next(iter(profile_keys), ""):
            return candidates[0]
    return None


def sent_target_from_unverified_message(
    events: list[dict], sent_profiles: list[dict], unread_name: str,
) -> dict | None:
    """Resolve an authorless bubble using a unique recipient and sent text."""
    matches: dict[str, dict] = {}
    for profile in sent_profiles:
        if not same_person_name(profile.get("normalized_name"), unread_name):
            continue
        sent_text = " ".join(str(profile.get("message_text") or "").split())
        if len(sent_text) < 20:
            continue
        if any(
            event.get("sender_type") == "unknown"
            and not str(event.get("author") or "").strip()
            and " ".join(str(event.get("text") or "").split()) == sent_text
            for event in events
        ):
            target_id = str(profile.get("id") or "")
            if target_id:
                matches[target_id] = profile
    return next(iter(matches.values())) if len(matches) == 1 else None


def verify_sent_message_events(events: list[dict], sent_message_text: str) -> None:
    """Mark only authorless, unclassified exact sent-message bubbles as own."""
    sent_text = " ".join(str(sent_message_text or "").split())
    if len(sent_text) < 20:
        return
    for event in events:
        if (event.get("sender_type") == "unknown"
                and not str(event.get("author") or "").strip()
                and " ".join(str(event.get("text") or "").split()) == sent_text):
            event["sender_type"] = "own"
            event["is_own_message"] = True
            event["is_incoming"] = False


# @layer business
# @feature replies
def merge_conversation_snapshots(older: list[dict], newer: list[dict]) -> list[dict]:
    """Join overlapping DOM windows without collapsing repeated real messages."""
    def identity(event: dict) -> tuple[str, str, str]:
        return (
            " ".join(str(event.get("text") or "").split()),
            str(event.get("timestamp") or ""),
            str(event.get("sender_type") or "unknown"),
        )

    old_keys = [identity(event) for event in older]
    new_keys = [identity(event) for event in newer]
    for overlap in range(min(len(older), len(newer)), 0, -1):
        if old_keys[-overlap:] == new_keys[:overlap]:
            return older + newer[overlap:]
    if older and newer:
        raise ValueError("Conversation DOM windows have no verified overlap.")
    return older or newer


def incoming_after_last_own(events: list[dict]) -> list[dict]:
    """Return customer messages after the account's most recent message."""
    last_own = max(
        (index for index, event in enumerate(events) if event.get("sender_type") == "own"),
        default=-1,
    )
    recent = [
        event for index, event in enumerate(events)
        if index > last_own and event.get("sender_type") == "incoming"
    ]
    if recent:
        return recent
    all_incoming = [event for event in events if event.get("sender_type") == "incoming"]
    return all_incoming[-1:]


def _name_tokens(value: str) -> list[str]:
    plain = unicodedata.normalize("NFKD", str(value or ""))
    plain = "".join(char for char in plain if not unicodedata.combining(char))
    return sorted(plain.casefold().split())


def same_person_name(left: str, right: str) -> bool:
    left_tokens = _name_tokens(left)
    right_tokens = _name_tokens(right)
    return bool(left_tokens and right_tokens and left_tokens == right_tokens)


# @layer business
# @feature replies
def classify_message_direction(
    *,
    class_evidence: str,
    author: str,
    account_name: str,
    unread_name: str,
    text_value: str,
    sent_message_text: str,
) -> str:
    """Return own, incoming, or unknown; unknown is never a verified reply."""
    classes = class_evidence.casefold().split()
    own_dom = any(
        token.endswith(("--is-me", "--from-me", "--outgoing", "--is-self"))
        or token == "from-me"
        for token in classes
    )
    incoming_dom = any(token.endswith(("--is-other", "--incoming")) for token in classes)
    # Conflicting DOM evidence is not safe to assign to either participant.
    if own_dom and incoming_dom:
        return "unknown"
    if own_dom:
        return "own"
    if incoming_dom:
        return "incoming"
    own_author = same_person_name(author, account_name)
    incoming_author = same_person_name(author, unread_name)
    if own_author and incoming_author:
        return "unknown"
    if own_author:
        return "own"
    if incoming_author:
        return "incoming"
    return "unknown"
