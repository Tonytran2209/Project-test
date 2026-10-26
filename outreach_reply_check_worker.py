"""Synchronize Unread conversations matched to this account's sent targets.

Flow:
    1. Open the selected Outreach LinkedIn profile.
    2. Open LinkedIn Messaging and select Unread.
    3. Skip Unread entries outside this account's successfully sent list.
    4. Verify eligible thread identity before saving its full history.
    5. Save messages with explicit own/incoming/unknown roles.
    6. Use the active-thread menu beside Star to restore Mark as unread.

Unread conversations are synchronized to Supabase for the Replies inbox.
Opening a conversation changes LinkedIn UI state, so the worker restores the
unread state before continuing.

Keep other workers from using the same persistent browser profile while this
worker is running.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import time
import unicodedata
from collections.abc import Callable
from datetime import datetime, timezone
from urllib.parse import unquote, urlparse
from urllib.parse import urljoin

from playwright.sync_api import Frame, Locator, Page

from app.outreach_account_pool import (
    OUTREACH_ACCOUNT_DISPLAY_NAMES,
    OutreachAccountPool,
)
from app.outreach_message_executor import get_outreach_supabase_client
from app.outreach_reply_schedule import run_reply_check_schedule
from app.outreach_reply_check_requests import (
    claim_reply_check_request,
    finish_reply_check_request,
    record_scheduled_reply_check,
)
from app.outreach_reply_store import save_outreach_reply
from app.outreach_reply_store import prune_stale_outreach_replies
from app.outreach_reply_direction import (
    classify_message_direction,
    incoming_after_last_own,
    merge_conversation_snapshots,
    profile_slug_key,
    same_person_name,
    sent_target_from_own_messages,
    sent_target_from_unverified_message,
    verify_sent_message_events,
)
from app.outreach_worker_heartbeat import worker_heartbeat


DEFAULT_ACCOUNT_ID = "outreach_account_02"
LINKEDIN_HOME_URL = "https://www.linkedin.com/"
LINKEDIN_MESSAGING_URL = "https://www.linkedin.com/messaging/"

logger = logging.getLogger("outreach_reply_check_worker")

UNREAD_SELECTOR = (
    'button[data-test-messaging-inbox-filters__filter-pill="UNREAD"]'
)
UNREAD_CONTAINER_SELECTOR = (
    "div.msg-conversations-container__title-row"
)
UNREAD_NAME_SELECTORS = (
    ".msg-conversation-listitem__participant-names",
    ".msg-conversation-card__participant-names",
    ".msg-conversation-listitem__participant-name",
    ".msg-conversation-card__participant-name",
    ".msg-conversations-container__conversations-listitem__participant-names",
    (
        ".msg-conversations-container__conversations-list "
        '[data-anonymize="person-name"]'
    ),
    (
        ".msg-conversations-container__convo-list "
        '[data-anonymize="person-name"]'
    ),
    (
        ".msg-conversations-container "
        'a[href*="/messaging/thread/"] [data-anonymize="person-name"]'
    ),
)
UNREAD_LIST_SELECTORS = (
    ".msg-conversations-container__conversations-list",
    ".msg-conversations-container__convo-list",
    ".msg-conversations-container__conversations-list-container",
)
UNREAD_ROW_SELECTORS = (
    ".msg-conversations-container .msg-conversation-listitem",
    ".msg-conversations-container .msg-conversation-card",
    '.msg-conversations-container a[href*="/messaging/thread/"]',
)
CONVERSATION_SETTLE_MS = 2_500
BEFORE_THREAD_MENU_MS = 1_200
THREAD_MENU_SETTLE_MS = 700
MARK_UNREAD_SETTLE_MS = 2_000
BETWEEN_CONVERSATIONS_MS = 1_500
MESSAGE_BODY_SELECTORS = (
    ".msg-s-event-listitem__body",
    ".msg-s-message-group__message-bubble",
    ".msg-s-event-listitem__message-bubble",
)
MESSAGE_AUTHOR_SELECTORS = (
    ".msg-s-message-group__name",
    '[data-anonymize="person-name"]',
)
MESSAGE_SCROLL_CONTAINER_SELECTORS = (
    ".msg-s-message-list-container",
    ".msg-s-message-list",
    ".msg-thread__messages",
    ".msg-s-message-list-content",
)
THREAD_STAR_SELECTORS = (
    'button[aria-label*="Star conversation"]',
    'button[aria-label="Star"]',
    'button:has(svg[data-test-icon*="star"])',
)
THREAD_OVERFLOW_SELECTORS = (
    "button.msg-thread-actions__control.artdeco-dropdown__trigger",
    (
        "button.msg-thread-actions__control:has("
        'span.visually-hidden:has-text("Open the options list in your conversation")'
        ")"
    ),
)


def _is_visible(locator: Locator, *, timeout_ms: int = 500) -> bool:
    """Mirror the proven visibility check used by the old workers."""

    try:
        return locator.is_visible(timeout=timeout_ms)
    except Exception:
        return False


def _click_locator(locator: Locator, *, timeout_ms: int = 3_000) -> bool:
    """Use the old worker's DOM-click-first strategy with a fallback."""

    try:
        locator.evaluate(
            """
            element => {
                element.scrollIntoView({block: 'center', inline: 'center'});
                element.click();
            }
            """
        )
        return True
    except Exception:
        pass

    try:
        locator.click(timeout=timeout_ms, force=True)
        return True
    except Exception:
        return False


def _is_selected(locator: Locator) -> bool:
    try:
        return (
            locator.get_attribute("aria-pressed") == "true"
            or locator.get_attribute("aria-checked") == "true"
        )
    except Exception:
        return False


def _surface_has_unread(surface: Page | Frame) -> bool:
    try:
        return surface.locator(UNREAD_SELECTOR).count() > 0
    except Exception:
        return False


def _messaging_surfaces(page: Page) -> list[Page]:
    """Prefer the page just used, then inspect newer tabs before old tabs."""

    surfaces: list[Page] = []
    if not page.is_closed():
        surfaces.append(page)

    for candidate in reversed(page.context.pages):
        if candidate.is_closed() or candidate in surfaces:
            continue
        surfaces.append(candidate)

    return surfaces


def _find_unread_surface(page: Page) -> Page | Frame | None:
    """Return only a live surface whose DOM actually contains Unread."""

    for candidate_page in _messaging_surfaces(page):
        if _surface_has_unread(candidate_page):
            return candidate_page

        for frame in candidate_page.frames:
            if frame is candidate_page.main_frame:
                continue
            if _surface_has_unread(frame):
                return frame

    return None


def _log_unread_diagnostics(page: Page) -> None:
    """Log non-sensitive DOM diagnostics instead of private message text."""

    for page_index, candidate_page in enumerate(
        _messaging_surfaces(page)
    ):
        try:
            exact_count = candidate_page.locator(
                UNREAD_SELECTOR
            ).count()
            text_count = candidate_page.locator(
                'button:has-text("Unread")'
            ).count()
            logger.error(
                "Unread diagnostics | page=%s | url=%s | exact=%s | text=%s",
                page_index,
                candidate_page.url,
                exact_count,
                text_count,
            )
        except Exception as exc:
            logger.error(
                "Unread diagnostics failed | page=%s | error=%s: %s",
                page_index,
                type(exc).__name__,
                exc,
            )

        for frame_index, frame in enumerate(candidate_page.frames):
            if frame is candidate_page.main_frame:
                continue
            try:
                logger.error(
                    "Unread diagnostics | page=%s | frame=%s | url=%s | exact=%s",
                    page_index,
                    frame_index,
                    frame.url,
                    frame.locator(UNREAD_SELECTOR).count(),
                )
            except Exception:
                continue


def _normalize_name(value: object) -> str:
    """Normalize accents, punctuation and whitespace for exact matching."""

    decomposed = unicodedata.normalize(
        "NFKD",
        str(value or "").strip(),
    )
    ascii_text = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )
    words = re.findall(r"[a-z0-9]+", ascii_text.casefold())
    return " ".join(words)


def _profile_name_from_linkedin_url(linkedin_url: object) -> str:
    """Derive a conservative full-name candidate from a public /in/ slug."""

    cleaned_url = str(linkedin_url or "").strip()
    if not cleaned_url:
        return ""

    try:
        path_parts = [
            part
            for part in urlparse(cleaned_url).path.split("/")
            if part
        ]
    except Exception:
        return ""

    if len(path_parts) < 2 or path_parts[0].casefold() != "in":
        return ""

    slug = unquote(path_parts[1]).strip().strip("-")

    # LinkedIn commonly appends a long numeric/hex identity token to a
    # readable profile slug. Remove only tokens that clearly look generated.
    slug = re.sub(
        r"(?:-[0-9]+)?-(?=[0-9a-z]*[0-9])[0-9a-z]{7,}$",
        "",
        slug,
        flags=re.IGNORECASE,
    )

    return _normalize_name(slug.replace("-", " "))


def load_sent_message_profiles(
    *,
    account_id: str,
    client=None,
) -> list[dict]:
    """Load only successfully sent targets for the active LinkedIn account."""

    active_client = client or get_outreach_supabase_client()
    sent_profiles: list[dict] = []
    derivable_name_count = 0
    page_size = 500
    offset = 0
    while True:
        response = (
            active_client.table("outreach_message_targets")
            .select(
                "id,prospect_id,assigned_account_id,linkedin_url,status,"
                "message_text,completed_at"
            )
            .eq("status", "sent")
            .eq("assigned_account_id", str(account_id).strip())
            .order("completed_at", desc=True)
            .order("id", desc=True)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        rows = list(response.data or [])
        for raw_row in rows:
            row = dict(raw_row)
            normalized_name = _profile_name_from_linkedin_url(
                row.get("linkedin_url")
            )
            row["normalized_name"] = normalized_name
            sent_profiles.append(row)
            if normalized_name:
                derivable_name_count += 1
        if len(rows) < page_size:
            break
        offset += page_size

    logger.info(
        (
            "DB SENT QUERY EVIDENCE | table=outreach_message_targets | "
            "filters=status:sent,assigned_account_id:%s | rows=%s | "
            "names_derived_from_linkedin_url=%s | names_not_derivable=%s"
        ),
        account_id,
        len(sent_profiles),
        derivable_name_count,
        len(sent_profiles) - derivable_name_count,
    )
    return sent_profiles


def _read_visible_unread_names(surface: Page | Frame) -> list[str]:
    """Read name nodes only; never read message previews or open a thread."""

    names: list[str] = []

    for selector in UNREAD_NAME_SELECTORS:
        try:
            candidates = surface.locator(selector)
            for index in range(candidates.count()):
                candidate = candidates.nth(index)
                if not _is_visible(candidate):
                    continue
                name = " ".join(candidate.inner_text().split())
                if name and name not in names:
                    names.append(name)
        except Exception:
            continue

    return names


def _thread_url_for_row(row: Locator) -> str:
    """Find a thread link on a row or inside it; LinkedIn uses both shapes."""
    try:
        href = row.get_attribute("href") or ""
        if "/messaging/thread/" not in href:
            link = row.locator('a[href*="/messaging/thread/"]').first
            href = link.get_attribute("href") if link.count() else ""
        if href and "/messaging/thread/" in href:
            return urljoin(LINKEDIN_HOME_URL, href).split("?", 1)[0]
    except Exception:
        pass
    return ""


def _name_for_unread_row(row: Locator) -> str:
    for selector in UNREAD_NAME_SELECTORS:
        try:
            node = row.locator(selector).first
            if node.count() and _is_visible(node):
                name = " ".join(node.inner_text().split())
                if name:
                    return name
        except Exception:
            continue
    return ""


def _read_visible_unread_threads(surface: Page | Frame) -> list[dict]:
    """Keep row identity so two people with the same name are not collapsed."""
    threads: list[dict] = []
    for row_selector in UNREAD_ROW_SELECTORS:
        for row in surface.locator(row_selector).all():
            if not _is_visible(row):
                continue
            name = _name_for_unread_row(row)
            if not name:
                continue
            member_keys = {
                key for anchor in row.locator('a[href*="/in/"]').all()
                if (key := profile_slug_key(anchor.get_attribute("href")))
            }
            member_url = f"https://www.linkedin.com/in/{next(iter(member_keys))}/" if len(member_keys) == 1 else ""
            threads.append({"name": name, "thread_url": _thread_url_for_row(row), "linkedin_url": member_url})
    if threads:
        return threads
    return [
        {"name": name, "thread_url": ""}
        for name in _read_visible_unread_names(surface)
    ]


def _scroll_unread_list(surface: Page | Frame, *, reset: bool = False) -> dict:
    """Scroll only the conversation list so lazy-loaded unread names appear."""

    return surface.evaluate(
        """
        ({listSelectors, nameSelectors, reset}) => {
            let container = null;
            let overflowed = false;

            for (const selector of listSelectors) {
                const candidate = document.querySelector(selector);
                if (!candidate) continue;
                overflowed ||= candidate.scrollHeight > candidate.clientHeight;
                const style = window.getComputedStyle(candidate);
                if (candidate.scrollHeight > candidate.clientHeight &&
                    (style.overflowY === 'auto' || style.overflowY === 'scroll')) {
                    container = candidate;
                    break;
                }
            }

            if (!container) {
                const nameNode = document.querySelector(nameSelectors.join(','));
                let candidate = nameNode ? nameNode.parentElement : null;

                while (candidate) {
                    const style = window.getComputedStyle(candidate);
                    const canScroll =
                        (style.overflowY === 'auto' || style.overflowY === 'scroll') &&
                        candidate.scrollHeight > candidate.clientHeight;
                    if (canScroll) {
                        container = candidate;
                        break;
                    }
                    candidate = candidate.parentElement;
                }
            }

            if (!container) {
                return {found: false, atBottom: true, top: 0, overflowed};
            }

            const before = container.scrollTop;
            container.scrollTop = reset ? 0 : Math.min(
                container.scrollTop + Math.max(container.clientHeight * 0.8, 240),
                container.scrollHeight
            );
            container.dispatchEvent(new Event('scroll', {bubbles: true}));

            const maximum = Math.max(
                0,
                container.scrollHeight - container.clientHeight
            );

            return {
                found: true,
                atBottom: container.scrollTop >= maximum - 2,
                top: container.scrollTop,
                moved: container.scrollTop !== before,
                overflowed
            };
        }
        """,
        {
            "listSelectors": list(UNREAD_LIST_SELECTORS),
            "nameSelectors": list(UNREAD_NAME_SELECTORS),
            "reset": reset,
        },
    )


def _unread_row_count(surface: Page | Frame) -> int:
    return max(
        (surface.locator(selector).count() for selector in UNREAD_ROW_SELECTORS),
        default=0,
    )


def _unread_empty_state_visible(surface: Page | Frame) -> bool:
    try:
        return bool(surface.evaluate(
            """() => /(?:no|you have no) unread (?:messages|conversations)/i.test(
                document.body.innerText || ''
            )"""
        ))
    except Exception:
        return False


def scan_unread_names(page: Page) -> list[dict]:
    """Collect every Unread row, preserving thread URL where available."""

    surface = _find_unread_surface(page)
    if surface is None:
        _log_unread_diagnostics(page)
        raise RuntimeError("Unread filter surface disappeared before scanning.")

    threads: list[dict] = []
    seen: set[str] = set()
    bottom_passes = 0
    started_at = time.monotonic()
    _scroll_unread_list(surface, reset=True)

    for _ in range(120):
        before_count = len(threads)

        for thread in _read_visible_unread_threads(surface):
            key = thread["thread_url"] or f"name:{_normalize_name(thread['name'])}"
            if key not in seen:
                seen.add(key)
                threads.append(thread)

        scroll_state = _scroll_unread_list(surface)
        if not scroll_state.get("found") and scroll_state.get("overflowed"):
            raise RuntimeError("Unread list overflows, but its scroll container was not found.")
        if scroll_state.get("found") and not scroll_state.get("moved") and not scroll_state.get("atBottom"):
            raise RuntimeError("Unread list stopped scrolling before reaching the bottom.")
        at_bottom = bool(scroll_state.get("atBottom"))

        if at_bottom and len(threads) == before_count:
            bottom_passes += 1
        else:
            bottom_passes = 0

        min_wait = 3.0 if threads else 8.0
        if bottom_passes >= 3 and time.monotonic() - started_at >= min_wait:
            break

        page.wait_for_timeout(500)
    else:
        raise RuntimeError("Unread list did not settle after 120 scroll passes.")

    visible_rows = _unread_row_count(surface)
    if not threads and (visible_rows or not _unread_empty_state_visible(surface)):
        raise RuntimeError(
            "Unread list has no extracted names, and an empty inbox was not confirmed."
        )
    if visible_rows > len(threads):
        raise RuntimeError(
            f"Unread list shows {visible_rows} rows but only {len(threads)} threads were captured."
        )
    by_name: dict[str, list[dict]] = {}
    for thread in threads:
        by_name.setdefault(_normalize_name(thread["name"]), []).append(thread)
    if any(
        len(group) > 1 and any(not item["thread_url"] for item in group)
        for group in by_name.values()
    ):
        raise RuntimeError("Duplicate Unread names lack thread URLs; cannot scan safely.")

    logger.info(
        "Unread names scanned | count=%s | visible_rows=%s | names=%s",
        len(threads),
        visible_rows,
        [thread["name"] for thread in threads],
    )
    return threads


def _active_thread_profile_key(page: Page) -> str:
    """Use only a unique member link inside the opened message thread."""
    surface = _find_unread_surface(page) or page
    for selector in (
        ".msg-thread__content",
        ".msg-thread",
        ".msg-conversation-container",
    ):
        try:
            scopes = surface.locator(selector)
            for index in range(scopes.count()):
                scope = scopes.nth(index)
                if not _is_visible(scope):
                    continue
                anchors = scope.locator('a[href*="/in/"]')
                keys = {
                    key
                    for anchor_index in range(anchors.count())
                    if (key := profile_slug_key(
                        anchors.nth(anchor_index).get_attribute("href")
                    ))
                }
                if len(keys) == 1:
                    return next(iter(keys))
                if len(keys) > 1:
                    return ""
        except Exception:
            continue
    return ""


# @layer business
# @feature replies
def sent_candidates_for_unread_thread(thread: dict, sent_profiles: list[dict], account_id: str) -> list[dict]:
    """Gate before opening: a member URL, or exact normalized name, must match.

    A name only permits inspection; it is not sufficient proof for saving.
    Unknown slugs/display-name differences are skipped rather than guessed.
    """
    profiles = [profile for profile in sent_profiles
                if profile.get("status") == "sent"
                and profile.get("assigned_account_id") == account_id]
    key = profile_slug_key(thread.get("linkedin_url"))
    if key:
        return [profile for profile in profiles if profile_slug_key(profile.get("linkedin_url")) == key]
    name = _normalize_name(thread.get("name") or "")
    return [profile for profile in profiles
            if same_person_name(name, profile.get("normalized_name") or
                                _profile_name_from_linkedin_url(profile.get("linkedin_url")))]


def match_unread_by_profile_url(
    page: Page,
    *,
    unread_names: list[dict],
    sent_profiles: list[dict],
    account_id: str,
) -> list[dict]:
    """Skip outsiders before reading history; save only verified sent targets."""
    matched_profiles: list[dict] = []
    sent_by_slug: dict[str, list[dict]] = {}
    for profile in sent_profiles:
        key = profile_slug_key(profile.get("linkedin_url"))
        if key:
            sent_by_slug.setdefault(key, []).append(profile)

    for unread_thread in unread_names:
        unread_name = unread_thread["name"]
        eligible = sent_candidates_for_unread_thread(unread_thread, sent_profiles, account_id)
        if not eligible:
            logger.info("UNREAD SKIPPED | account=%s | name=%s | reason=not_in_sent_list",
                        account_id, unread_name)
            continue
        normalized_name = _normalize_name(unread_name)
        opened = False
        try:
            thread_url = open_matched_conversation(
                page, unread_name, unread_thread["thread_url"]
            )
            opened = True
            profile_key = _active_thread_profile_key(page)
            profile_url = (
                f"https://www.linkedin.com/in/{profile_key}/" if profile_key else ""
            )
            candidates = sent_by_slug.get(profile_key, []) if profile_key else []
            candidates = [profile for profile in candidates
                          if profile.get("status") == "sent"
                          and profile.get("assigned_account_id") == account_id]
            if profile_key and not candidates:
                logger.info("UNREAD SKIPPED | account=%s | name=%s | reason=profile_not_in_sent_list",
                            account_id, unread_name)
                continue
            match_reason = "exact_thread_profile_url"
            conversation_events = load_full_conversation(
                page, unread_name, account_id=account_id,
                sent_message_text=str(candidates[0].get("message_text") or "")
                if candidates else "",
            )
            if not candidates:
                own_text_match = sent_target_from_own_messages(
                    conversation_events, eligible,
                )
                if own_text_match:
                    candidates = [own_text_match]
                    match_reason = "exact_own_sent_message"
                else:
                    unverified_text_match = sent_target_from_unverified_message(
                        conversation_events, eligible, unread_name,
                    )
                    if unverified_text_match:
                        candidates = [unverified_text_match]
                        match_reason = "unique_recipient_and_exact_sent_message"
            if not candidates:
                logger.info("UNREAD SKIPPED | account=%s | name=%s | reason=sent_identity_unverified",
                            account_id, unread_name)
                continue
            verify_sent_message_events(
                conversation_events, str(candidates[0].get("message_text") or ""),
            )
            matched_profiles.append({
                "unread_name": unread_name,
                "thread_url": thread_url,
                "normalized_unread_name": normalized_name,
                "match_reason": match_reason,
                "similarity": 1.0,
                "sent_profile": candidates[0],
                "linkedin_url": profile_url or thread_url,
                "conversation_events": conversation_events,
            })
            if candidates:
                logger.info(
                    "REPLY MATCH | reason=%s | unread_name=%s | target_id=%s",
                    match_reason,
                    unread_name,
                    candidates[0].get("id"),
                )
        finally:
            if opened:
                mark_active_thread_as_unread(page, unread_name)
                page.wait_for_timeout(BETWEEN_CONVERSATIONS_MS)
    return matched_profiles


def _find_visible_unread_name(
    surface: Page | Frame,
    unread_name: str,
) -> Locator | None:
    expected_name = _normalize_name(unread_name)

    for selector in UNREAD_NAME_SELECTORS:
        try:
            candidates = surface.locator(selector)
            for index in range(candidates.count()):
                candidate = candidates.nth(index)
                if not _is_visible(candidate):
                    continue
                actual_name = _normalize_name(candidate.inner_text())
                if actual_name == expected_name:
                    return candidate
        except Exception:
            continue

    return None


def _find_visible_unread_row(
    surface: Page | Frame, unread_name: str, thread_url: str,
) -> Locator | None:
    """Find the clickable box using the same identity captured during scan."""
    expected_name = _normalize_name(unread_name)
    for selector in UNREAD_ROW_SELECTORS:
        try:
            rows = surface.locator(selector)
            for index in range(rows.count()):
                row = rows.nth(index)
                if not _is_visible(row):
                    continue
                if _normalize_name(_name_for_unread_row(row)) != expected_name:
                    continue
                if thread_url and _thread_url_for_row(row) != thread_url:
                    continue
                return row
        except Exception:
            continue
    return None


def _scroll_unread_list_to_start(surface: Page | Frame) -> None:
    try:
        _scroll_unread_list(surface, reset=True)
    except Exception:
        pass


def open_matched_conversation(
    page: Page, unread_name: str, thread_url: str = "",
) -> str:
    """Click the captured Unread box and verify its conversation opened."""

    surface = _find_unread_surface(page)
    if surface is None:
        raise RuntimeError("Unread surface was not found before row click.")

    _scroll_unread_list_to_start(surface)
    page.wait_for_timeout(400)

    bottom_passes = 0

    for _ in range(45):
        row = _find_visible_unread_row(surface, unread_name, thread_url)
        name_locator = _find_visible_unread_name(surface, unread_name) if not thread_url else None
        if row is not None or name_locator is not None:
            opened_url = thread_url or (_thread_url_for_row(row) if row else "")
            previous_url = page.url
            logger.info(
                "Opening Unread box | unread_name=%s | thread_url=%s | row_found=%s",
                unread_name, opened_url, bool(row),
            )
            click_targets: list[tuple[str, Locator]] = []
            if row is not None:
                if "/messaging/thread/" in str(row.get_attribute("href") or ""):
                    click_targets.append(("row-link", row))
                else:
                    link = row.locator('a[href*="/messaging/thread/"]').first
                    if link.count():
                        click_targets.append(("row-link", link))
                click_targets.append(("conversation-box", row))
            if name_locator is not None:
                click_targets.append(("participant-name", name_locator))

            for strategy, target in click_targets:
                if not _click_locator(target):
                    continue
                logger.info(
                    "CONVERSATION CLICK EVIDENCE | strategy=%s | unread_name=%s",
                    strategy, unread_name,
                )
                for _ in range(25):
                    current_url = page.url.split("?", 1)[0]
                    if opened_url and current_url.rstrip("/") == opened_url.rstrip("/"):
                        page.wait_for_timeout(CONVERSATION_SETTLE_MS)
                        logger.info("Opened Unread conversation | unread_name=%s | url=%s", unread_name, current_url)
                        return opened_url
                    if not opened_url and current_url != previous_url.split("?", 1)[0] and "/messaging/thread/" in current_url:
                        page.wait_for_timeout(CONVERSATION_SETTLE_MS)
                        logger.info("Opened Unread conversation | unread_name=%s | url=%s", unread_name, current_url)
                        return current_url
                    page.wait_for_timeout(160)
            raise RuntimeError(f"Clicked Unread box but could not verify its thread: {unread_name!r}.")

        scroll_state = _scroll_unread_list(surface)
        if bool(scroll_state.get("atBottom")):
            bottom_passes += 1
        else:
            bottom_passes = 0

        if bottom_passes >= 2:
            break

        page.wait_for_timeout(400)

    raise RuntimeError(
        f"Matched conversation row was not found for {unread_name!r}."
    )


def _message_group_for_body(body: Locator) -> Locator | None:
    selectors = (
        (
            'xpath=ancestor::*['
            'contains(concat(" ",normalize-space(@class)," "),'
            '" msg-s-message-group ")][1]'
        ),
        (
            'xpath=ancestor::*['
            'contains(concat(" ",normalize-space(@class)," "),'
            '" msg-s-event-listitem ")][1]'
        ),
        'xpath=ancestor::li[1]',
    )

    for selector in selectors:
        try:
            group = body.locator(selector)
            if group.count() > 0:
                return group.first
        except Exception:
            continue

    return None


def _message_class_evidence(body: Locator, group: Locator | None) -> str:
    """Read direction classes from the message and its actual event ancestors."""
    classes: list[str] = []
    for locator in (body, group):
        if locator is None:
            continue
        try:
            classes.append(str(locator.get_attribute("class") or ""))
        except Exception:
            pass
    try:
        event = body.locator(
            'xpath=ancestor::*['
            'contains(concat(" ",normalize-space(@class)," "),'
            '" msg-s-event-listitem ")][1]'
        )
        if event.count():
            classes.append(str(event.first.get_attribute("class") or ""))
    except Exception:
        pass
    return " ".join(classes).casefold()


def _read_message_author(group: Locator | None) -> str:
    if group is None:
        return ""

    for selector in MESSAGE_AUTHOR_SELECTORS:
        try:
            candidates = group.locator(selector)
            for index in range(candidates.count()):
                candidate = candidates.nth(index)
                if not _is_visible(candidate):
                    continue
                value = " ".join(candidate.inner_text().split())
                if value:
                    return value
        except Exception:
            continue

    return ""


def _read_message_timestamp(group: Locator | None) -> str:
    if group is None:
        return ""

    date_value = ""
    date_xpath = (
        'xpath=preceding::*['
        'contains(@class,"msg-s-message-list__time-heading") or '
        'contains(@class,"msg-s-message-list__date-heading") or '
        'contains(@class,"msg-s-message-list__time-divider")'
        '][1]'
    )
    try:
        date_heading = group.locator(date_xpath)
        if date_heading.count() > 0:
            date_value = " ".join(
                date_heading.first.inner_text().split()
            )
    except Exception:
        date_value = ""

    selectors = (
        "time",
        ".msg-s-message-group__timestamp",
        ".msg-s-event-listitem__timestamp",
    )

    for selector in selectors:
        try:
            candidates = group.locator(selector)
            for index in range(candidates.count()):
                candidate = candidates.nth(index)
                for attribute in ("datetime", "title", "aria-label"):
                    attribute_value = str(
                        candidate.get_attribute(attribute) or ""
                    ).strip()
                    if attribute_value:
                        return attribute_value

                time_value = " ".join(candidate.inner_text().split())
                if time_value:
                    if date_value:
                        return f"{date_value} · {time_value}"
                    return time_value
        except Exception:
            continue

    return date_value


def _message_event_dom_key(body: Locator) -> str:
    """Return one stable key for nested selectors from the same message event."""

    try:
        return str(
            body.evaluate(
                """
                element => {
                    const eventNode =
                        element.closest('.msg-s-event-listitem') || element;
                    window.__outreachReplyEventKeys ||= new WeakMap();
                    window.__outreachReplyEventKeyCounter ||= 0;
                    if (!window.__outreachReplyEventKeys.has(eventNode)) {
                        window.__outreachReplyEventKeyCounter += 1;
                        window.__outreachReplyEventKeys.set(
                            eventNode,
                            `reply-event-${window.__outreachReplyEventKeyCounter}`
                        );
                    }
                    return window.__outreachReplyEventKeys.get(eventNode);
                }
                """
            )
            or ""
        ).strip()
    except Exception:
        return ""


def load_full_conversation(
    page: Page, unread_name: str, *, account_id: str,
    sent_message_text: str = "",
) -> list[dict]:
    """Read overlapping DOM windows while walking from newest to oldest."""

    surface = _find_unread_surface(page) or page
    scroll_container: Locator | None = None
    short_container: Locator | None = None
    overflowed = False

    for selector in MESSAGE_SCROLL_CONTAINER_SELECTORS:
        try:
            candidates = surface.locator(selector)
            for index in range(candidates.count()):
                candidate = candidates.nth(index)
                if _is_visible(candidate):
                    state = candidate.evaluate(
                        """element => ({
                            height: element.scrollHeight,
                            viewport: element.clientHeight,
                            overflow: getComputedStyle(element).overflowY
                        })"""
                    )
                    is_tall = state["height"] > state["viewport"] + 2
                    overflowed = overflowed or is_tall
                    if is_tall and state["overflow"] in {"auto", "scroll"}:
                        scroll_container = candidate
                        logger.info(
                            "CONVERSATION SCROLL EVIDENCE | unread_name=%s | selector=%s",
                            unread_name, selector,
                        )
                        break
                    if not is_tall and short_container is None:
                        short_container = candidate
        except Exception:
            continue
        if scroll_container is not None:
            break

    if scroll_container is None and not overflowed:
        scroll_container = short_container
    if scroll_container is None:
        raise RuntimeError(
            f"Conversation scroll container was not found for {unread_name!r}."
        )

    # Always start from newest, including after a previous identity check that
    # left LinkedIn scrolled to the oldest message.
    scroll_container.evaluate(
        """element => {
            element.scrollTo({top: element.scrollHeight, behavior: 'auto'});
            element.dispatchEvent(new Event('scroll', {bubbles: true}));
        }"""
    )
    page.wait_for_timeout(600)

    stable_passes = 0
    previous_height = -1
    _, collected = read_incoming_reply_messages(
        page, unread_name=unread_name,
        sent_message_text=sent_message_text,
        assigned_account_id=account_id,
    )

    for _ in range(80):
        try:
            state_before = scroll_container.evaluate(
                """
                element => {
                    const result = {
                        height: element.scrollHeight,
                        top: element.scrollTop
                    };
                    element.scrollTo({
                        top: Math.max(0, element.scrollTop - Math.max(element.clientHeight * 0.8, 240)),
                        behavior: 'auto'
                    });
                    element.dispatchEvent(new Event('scroll', {bubbles: true}));
                    return result;
                }
                """
            )
        except Exception as exc:
            raise RuntimeError("Could not scroll the conversation history.") from exc

        page.wait_for_timeout(1_200)
        _, older = read_incoming_reply_messages(
            page, unread_name=unread_name,
            sent_message_text=sent_message_text,
            assigned_account_id=account_id,
        )
        collected = merge_conversation_snapshots(older, collected)

        try:
            current_height = int(
                scroll_container.evaluate("element => element.scrollHeight")
                or 0
            )
        except Exception as exc:
            raise RuntimeError("Could not verify conversation history loading.") from exc

        at_top = int(scroll_container.evaluate("element => element.scrollTop") or 0) == 0
        if current_height == previous_height and at_top:
            stable_passes += 1
        else:
            stable_passes = 0

        logger.info(
            (
                "CONVERSATION SCROLL | unread_name=%s | pass=%s | "
                "height_before=%s | height_after=%s | stable_passes=%s"
            ),
            unread_name,
            len(collected),
            state_before.get("height"),
            current_height,
            stable_passes,
        )

        previous_height = current_height
        if stable_passes >= 2:
            break
    else:
        raise RuntimeError("Conversation history did not settle at its beginning.")

    for index, event in enumerate(collected):
        event["index"] = index
    return collected


def read_incoming_reply_messages(
    page: Page,
    *,
    unread_name: str,
    sent_message_text: str,
    assigned_account_id: str,
) -> tuple[list[dict], list[dict]]:
    """Snapshot every visible bubble with conservative sender evidence."""

    surface = _find_unread_surface(page)
    if surface is None:
        surface = page

    body_locator = surface.locator(", ".join(MESSAGE_BODY_SELECTORS))
    normalized_sent_text = " ".join(str(sent_message_text or "").split())
    account_name = OUTREACH_ACCOUNT_DISPLAY_NAMES.get(assigned_account_id, "")
    events: list[dict] = []
    seen_dom_event_keys: set[str] = set()

    logger.info(
        "MESSAGE DOM EVIDENCE | unread_name=%s | selectors=%s | candidates=%s",
        unread_name,
        MESSAGE_BODY_SELECTORS,
        body_locator.count(),
    )

    for index in range(body_locator.count()):
        body = body_locator.nth(index)

        try:
            if not _is_visible(body):
                continue
            text_value = " ".join(body.inner_text().split())
        except Exception:
            continue

        if not text_value:
            continue

        dom_event_key = _message_event_dom_key(body)
        dom_message_key = (
            f"{dom_event_key}|{' '.join(text_value.casefold().split())}"
            if dom_event_key
            else ""
        )
        if dom_message_key and dom_message_key in seen_dom_event_keys:
            logger.debug(
                "Skipping duplicate nested message selector | dom_event_key=%s",
                dom_event_key,
            )
            continue
        if dom_message_key:
            seen_dom_event_keys.add(dom_message_key)

        group = _message_group_for_body(body)
        author = _read_message_author(group)
        class_evidence = _message_class_evidence(body, group)
        direction = classify_message_direction(
            class_evidence=class_evidence,
            author=author,
            account_name=account_name,
            unread_name=unread_name,
            text_value=text_value,
            sent_message_text=normalized_sent_text,
        )
        if direction == "unknown":
            logger.warning(
                "MESSAGE SENDER UNKNOWN | unread_name=%s | author=%s | classes=%s",
                unread_name,
                author,
                class_evidence,
            )

        events.append(
            {
                "index": len(events),
                "author": author,
                "text": text_value,
                "timestamp": _read_message_timestamp(group),
                "is_own_message": direction == "own",
                "is_incoming": direction == "incoming",
                "sender_type": direction,
            }
        )

    last_sent_index = -1
    for event in events:
        if event["is_own_message"]:
            last_sent_index = max(last_sent_index, int(event["index"]))

    replies = [
        event
        for event in events
        if event["is_incoming"] and int(event["index"]) > last_sent_index
    ]

    if not replies:
        incoming_events = [event for event in events if event["is_incoming"]]
        if incoming_events:
            replies = [incoming_events[-1]]

    logger.info(
        (
            "MESSAGE READ EVIDENCE | unread_name=%s | bubbles=%s | "
            "last_sent_index=%s | incoming_replies=%s"
        ),
        unread_name,
        len(events),
        last_sent_index,
        len(replies),
    )
    return replies, events


def _visible_exact_text(page: Page, text_value: str) -> Locator | None:
    candidates = (
        page.get_by_role("menuitem", name=text_value, exact=True),
        page.get_by_text(text_value, exact=True),
    )

    for locator in candidates:
        try:
            for index in range(locator.count()):
                candidate = locator.nth(index)
                if _is_visible(candidate):
                    return candidate
        except Exception:
            continue

    return None


def _find_overflow_beside_star(
    page: Page,
    unread_name: str,
) -> Locator:
    """Find the thread menu whose accessible label names this profile."""

    normalized_target = _normalize_name(unread_name)

    # Current LinkedIn DOM exposes the active-thread menu directly as:
    # button.msg-thread-actions__control.artdeco-dropdown__trigger
    # Its hidden accessible text starts with "Open the options list in your
    # conversation ...". Prefer that stable semantic evidence over position.
    for selector in THREAD_OVERFLOW_SELECTORS:
        try:
            candidates = page.locator(selector)
            for index in range(candidates.count()):
                candidate = candidates.nth(index)
                if not _is_visible(candidate):
                    continue

                hidden_text = " ".join(candidate.inner_text().split())
                normalized_hidden_text = _normalize_name(hidden_text)
                if normalized_target not in normalized_hidden_text:
                    logger.info(
                        (
                            "THREAD MENU SKIPPED | target=%s | "
                            "reason=accessible_name_does_not_match | "
                            "candidate_text=%s"
                        ),
                        unread_name,
                        hidden_text,
                    )
                    continue

                logger.info(
                    (
                        "THREAD MENU DOM EVIDENCE | strategy=direct-control | "
                        "target=%s | selector=%s | aria_expanded=%s | "
                        "hidden_text=%s"
                    ),
                    unread_name,
                    selector,
                    candidate.get_attribute("aria-expanded"),
                    hidden_text,
                )
                return candidate
        except Exception:
            continue

    for selector in THREAD_STAR_SELECTORS:
        try:
            stars = page.locator(selector)
            for index in range(stars.count()):
                star = stars.nth(index)
                if not _is_visible(star):
                    continue

                previous = star.locator(
                    "xpath=preceding-sibling::button[1]"
                )
                if previous.count() > 0 and _is_visible(previous.first):
                    hidden_text = " ".join(
                        previous.first.inner_text().split()
                    )
                    if normalized_target not in _normalize_name(hidden_text):
                        continue
                    logger.info(
                        (
                            "THREAD MENU DOM EVIDENCE | strategy=button-before-star | "
                            "target=%s | star_selector=%s | overflow_aria=%s | "
                            "overflow_title=%s | hidden_text=%s"
                        ),
                        unread_name,
                        selector,
                        previous.first.get_attribute("aria-label"),
                        previous.first.get_attribute("title"),
                        hidden_text,
                    )
                    return previous.first

                parent_buttons = star.locator("xpath=parent::*").locator(
                    ":scope > button"
                )
                for button_index in range(parent_buttons.count()):
                    button = parent_buttons.nth(button_index)
                    if not _is_visible(button):
                        continue
                    try:
                        icon_count = button.locator(
                            'svg[data-test-icon*="overflow"], '
                            'svg[data-test-icon*="ellipsis"]'
                        ).count()
                        aria_label = str(
                            button.get_attribute("aria-label") or ""
                        ).casefold()
                    except Exception:
                        continue
                    hidden_text = " ".join(button.inner_text().split())
                    target_matches = (
                        normalized_target in _normalize_name(hidden_text)
                    )
                    if target_matches and (
                        icon_count > 0 or "more" in aria_label
                    ):
                        logger.info(
                            (
                                "THREAD MENU DOM EVIDENCE | "
                                "strategy=star-parent-overflow | "
                                "target=%s | star_selector=%s | "
                                "overflow_aria=%s | hidden_text=%s"
                            ),
                            unread_name,
                            selector,
                            aria_label,
                            hidden_text,
                        )
                        return button
        except Exception:
            continue

    raise RuntimeError(
        "Active-thread overflow button was not found for "
        f"{unread_name!r}."
    )


def _open_thread_overflow_menu(page: Page, unread_name: str) -> None:
    overflow = _find_overflow_beside_star(page, unread_name)
    if not _click_locator(overflow):
        raise RuntimeError("Could not click thread overflow beside Star.")

    page.wait_for_timeout(THREAD_MENU_SETTLE_MS)

    for _ in range(30):
        if (
            _visible_exact_text(page, "Mark as unread") is not None
            or _visible_exact_text(page, "Mark as read") is not None
        ):
            return
        page.wait_for_timeout(100)

    raise RuntimeError("Thread overflow menu did not become visible.")


def mark_active_thread_as_unread(page: Page, unread_name: str) -> None:
    """Restore unread state and verify menu changes to Mark as read."""

    page.wait_for_timeout(BEFORE_THREAD_MENU_MS)
    _open_thread_overflow_menu(page, unread_name)

    mark_unread = _visible_exact_text(page, "Mark as unread")
    if mark_unread is not None:
        if not _click_locator(mark_unread):
            raise RuntimeError("Could not click exact Mark as unread item.")
        logger.info(
            "Clicked Mark as unread | unread_name=%s | settle_ms=%s",
            unread_name,
            MARK_UNREAD_SETTLE_MS,
        )
        page.wait_for_timeout(MARK_UNREAD_SETTLE_MS)
    else:
        already_unread = _visible_exact_text(page, "Mark as read")
        if already_unread is not None:
            page.keyboard.press("Escape")
            logger.info(
                "Conversation was already unread | unread_name=%s",
                unread_name,
            )
            return
        raise RuntimeError("Neither Mark as unread nor Mark as read was found.")

    verified = False
    for _ in range(5):
        page.wait_for_timeout(THREAD_MENU_SETTLE_MS)
        _open_thread_overflow_menu(page, unread_name)
        if _visible_exact_text(page, "Mark as read") is not None:
            verified = True
            page.keyboard.press("Escape")
            break
        page.keyboard.press("Escape")

    if not verified:
        raise RuntimeError(
            "Mark as unread click was not verified by Mark as read state."
        )

    logger.info(
        "MARKED AS UNREAD | unread_name=%s | verification=Mark as read visible",
        unread_name,
    )


def process_matched_conversations(
    matched_profiles: list[dict],
    *,
    account_id: str,
    client,
) -> int:
    """Save conversations captured during the single Unread thread visit."""

    processed_count = 0
    failed_count = 0

    for match in matched_profiles:
        unread_name = str(match.get("unread_name") or "").strip()
        sent_profile = dict(match.get("sent_profile") or {})

        try:
            opened_thread_url = str(match.get("thread_url") or "")
            conversation_events = list(match.get("conversation_events") or [])
            replies = incoming_after_last_own(conversation_events)
            observed_profile_url = str(match.get("linkedin_url") or "")
            reply_profile_url = (
                observed_profile_url
                if profile_slug_key(observed_profile_url)
                else str(sent_profile.get("linkedin_url") or observed_profile_url or opened_thread_url)
            )

            if not conversation_events:
                failed_count += 1
                logger.warning(
                    (
                        "NO MESSAGE BODY FOUND | unread_name=%s | "
                        "db_target_id=%s"
                    ),
                    unread_name,
                    sent_profile.get("id"),
                )
            else:
                latest_reply = replies[-1] if replies else conversation_events[-1]
                try:
                    stored_reply = save_outreach_reply(
                        sent_target_id=str(sent_profile.get("id") or ""),
                        prospect_id=str(
                            sent_profile.get("prospect_id") or ""
                        ),
                        assigned_account_id=account_id,
                        user_name=unread_name,
                        linkedin_url=reply_profile_url,
                        thread_url=opened_thread_url,
                        message_text=str(latest_reply.get("text") or ""),
                        linkedin_message_time=str(
                            latest_reply.get("timestamp") or ""
                        ),
                        conversation_messages=conversation_events,
                        match_reason=str(match.get("match_reason") or ""),
                        match_similarity=float(
                            match.get("similarity") or 0.0
                        ),
                        client=client,
                    )
                    logger.info(
                        (
                            "REPLY UPSERTED | reply_id=%s | "
                            "sent_target_id=%s | user_name=%s | "
                            "conversation_messages=%d"
                        ),
                        stored_reply.get("id"),
                        sent_profile.get("id"),
                        unread_name,
                        len(conversation_events),
                    )
                except Exception as exc:
                    failed_count += 1
                    logger.exception(
                        (
                            "REPLY STORE FAILED | sent_target_id=%s | "
                            "user_name=%s | error=%s"
                        ),
                        sent_profile.get("id"),
                        unread_name,
                        exc,
                    )

            processed_count += 1

        except Exception as exc:
            failed_count += 1
            logger.exception(
                "Matched conversation processing failed | unread_name=%s | error=%s",
                unread_name,
                exc,
            )

    if failed_count:
        raise RuntimeError(
            f"Could not read, restore, or save {failed_count} Unread conversation(s)."
        )
    return processed_count


def _click_first_visible(
    page: Page,
    candidates: list[Callable[[Page], Locator]],
    *,
    description: str,
    timeout_ms: int = 3_000,
) -> None:
    """Use the proven old-worker flow across every matching candidate."""

    for build_locator in candidates:
        locator = build_locator(page)

        try:
            for index in range(locator.count()):
                candidate = locator.nth(index)
                if not _is_visible(candidate):
                    continue
                if _click_locator(candidate, timeout_ms=timeout_ms):
                    logger.info("Clicked %s", description)
                    return
        except Exception:
            continue

    raise RuntimeError(
        f"Could not find the LinkedIn {description} control."
    )


def open_messaging(page: Page) -> Page:
    """Open Messaging and return the page that owns the messaging UI."""

    candidates = [
        lambda active_page: active_page.get_by_role(
            "link", name="Messaging", exact=True
        ),
        lambda active_page: active_page.get_by_role(
            "button", name="Messaging", exact=True
        ),
        lambda active_page: active_page.locator(
            'a[href*="/messaging/"]'
        ),
        lambda active_page: active_page.get_by_text(
            "Messaging", exact=True
        ),
    ]

    try:
        _click_first_visible(
            page,
            candidates,
            description="Messaging",
        )
    except RuntimeError:
        # LinkedIn can hide the global nav at narrower widths.  The direct
        # route is only a navigation fallback; Unread is still clicked
        # as a UI control in the next step.
        logger.info(
            "Messaging nav item was not visible; opening its LinkedIn route."
        )
        page.goto(
            LINKEDIN_MESSAGING_URL,
            wait_until="domcontentloaded",
        )

    # Keep the same Page whenever possible. The old implementation returned
    # the first /messaging tab in the persistent context, which could be a
    # stale restored tab while the visible UI belonged to another page.
    for _ in range(40):
        surface = _find_unread_surface(page)
        if surface is not None:
            owner_page = surface if isinstance(surface, Page) else surface.page
            owner_page.bring_to_front()
            logger.info(
                "Messaging filters found | url=%s",
                owner_page.url,
            )
            return owner_page

        page.wait_for_timeout(500)

    if "/messaging" not in (page.url or "").lower():
        logger.info(
            "Messaging UI did not settle after click; opening direct route."
        )
        page.goto(
            LINKEDIN_MESSAGING_URL,
            wait_until="domcontentloaded",
        )

    for _ in range(40):
        surface = _find_unread_surface(page)
        if surface is not None:
            owner_page = surface if isinstance(surface, Page) else surface.page
            owner_page.bring_to_front()
            logger.info(
                "Messaging filters found after direct navigation | url=%s",
                owner_page.url,
            )
            return owner_page
        page.wait_for_timeout(500)

    _log_unread_diagnostics(page)
    return page


def open_unread(page: Page) -> None:
    """Click Unread inside LinkedIn Messaging."""

    deadline = time.monotonic() + 30
    selectors = (
        UNREAD_SELECTOR,
        (
            f'{UNREAD_CONTAINER_SELECTOR} '
            'button[data-test-messaging-inbox-filters__filter-pill="UNREAD"]'
        ),
        'button[role="button"]:has-text("Unread")',
        '[role="button"]:has-text("Unread")',
        'button:has-text("Unread")',
    )

    while time.monotonic() < deadline:
        surface = _find_unread_surface(page)

        if surface is None:
            page.wait_for_timeout(250)
            continue

        for selector in selectors:
            try:
                candidates = surface.locator(selector)
                for index in range(candidates.count()):
                    candidate = candidates.nth(index)

                    if not _is_visible(candidate):
                        continue

                    if _is_selected(candidate):
                        logger.info("Unread filter is already selected")
                        return

                    if not _click_locator(candidate):
                        continue

                    logger.info(
                        "Clicked Unread | selector=%s | candidate=%s",
                        selector,
                        index,
                    )

                    for _ in range(20):
                        if _is_selected(candidate):
                            logger.info("Unread filter selection confirmed")
                            return
                        page.wait_for_timeout(100)

            except Exception:
                continue

        page.wait_for_timeout(250)

    _log_unread_diagnostics(page)
    raise RuntimeError(
        "Could not find and confirm the LinkedIn Unread control."
    )


def _run_once(account_id: str) -> None:
    """Read only sent-list Unread threads, then restore their unread state."""

    pool = OutreachAccountPool()
    account = pool.get_account(account_id)
    browser = account.create_browser_manager()
    client = get_outreach_supabase_client()

    logger.info(
        "Starting reply-check worker | account=%s | profile=%s",
        account.account_id,
        account.profile_directory,
    )

    try:
        browser.start()
        page = browser.open_linkedin_url(LINKEDIN_HOME_URL)
        page = open_messaging(page)
        open_unread(page)
        sent_profiles = load_sent_message_profiles(
            account_id=account.account_id,
            client=client,
        )
        unread_names = scan_unread_names(page)
        # Outside-sent-list threads are intentional skips, not scan failures.
        matched_profiles = match_unread_by_profile_url(
            page,
            unread_names=unread_names,
            sent_profiles=sent_profiles,
            account_id=account.account_id,
        )
        logger.info(
            "Reply-check match coverage | account=%s | unread=%s | verified=%s | skipped=%s",
            account.account_id,
            len(unread_names),
            len(matched_profiles),
            len(unread_names) - len(matched_profiles),
        )
        processed_count = process_matched_conversations(
            matched_profiles,
            account_id=account.account_id,
            client=client,
        )

        print("")
        print("Reply-check scan completed.")
        print(f"Unread conversations: {len(unread_names)}")
        print(f"Linked to sent targets: {sum(bool(item.get('sent_profile')) for item in matched_profiles)}")
        print(f"Conversations saved: {processed_count}")
        print("Reply-check worker finished. Closing the browser.")
    except KeyboardInterrupt:
        logger.info("Reply-check worker stopped.")
    finally:
        browser.stop()


def run_once(account_id: str) -> None:
    """Scan one account while publishing its live activity heartbeat."""
    with worker_heartbeat("reply_check", account_id):
        _run_once(account_id)


def run_all_accounts() -> list[str]:
    """Scan all registered profiles sequentially, continuing after account errors."""

    failed_accounts: list[str] = []
    account_ids = [account.account_id for account in OutreachAccountPool().accounts]
    for account_id in account_ids:
        logger.info("Reply check starting | account=%s", account_id)
        try:
            run_once(account_id)
        except Exception:
            failed_accounts.append(account_id)
            logger.exception("Reply check failed | account=%s", account_id)

    if failed_accounts:
        logger.error(
            "Reply check finished with failed accounts: %s",
            ", ".join(failed_accounts),
        )
    else:
        logger.info("Reply check finished for all %s accounts", len(account_ids))
    return failed_accounts


def process_manual_reply_check_request() -> bool:
    """Claim and execute one dashboard request; return whether work ran."""
    try:
        request = claim_reply_check_request()
    except Exception:
        logger.exception("Could not poll manual reply-check requests")
        return False
    if not request:
        return False
    request_id = str(request.get("id") or "")
    started_at = str(request.get("started_at") or "").strip()
    logger.info("Starting dashboard-triggered reply check | request=%s", request_id)
    try:
        failed_accounts = run_all_accounts()
        if failed_accounts:
            finish_reply_check_request(
                request_id,
                error="Reply scan failed for: " + ", ".join(failed_accounts),
            )
            return True
        removed_count = prune_stale_outreach_replies(started_at)
        logger.info("Pruned %s stale Replies without send jobs", removed_count)
    except Exception as exc:
        logger.exception("Dashboard-triggered reply check failed")
        finish_reply_check_request(request_id, error=str(exc))
    else:
        finish_reply_check_request(request_id)
    return True


def run_scheduled_reply_check() -> None:
    """Record a scheduled scan so Replies can show when it last finished."""
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        failed_accounts = run_all_accounts()
        if failed_accounts:
            raise RuntimeError("Reply scan failed for: " + ", ".join(failed_accounts))
        removed_count = prune_stale_outreach_replies(started_at)
        logger.info("Pruned %s stale Replies without send jobs", removed_count)
    except Exception as exc:
        try:
            record_scheduled_reply_check(started_at, error=str(exc))
        except Exception:
            logger.exception("Could not record scheduled reply-check failure")
        raise

    try:
        record_scheduled_reply_check(started_at)
    except Exception:
        logger.exception("Could not record scheduled reply-check completion")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Open LinkedIn Messaging > Unread for reply checking."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--schedule",
        action="store_true",
        help=(
            "Continuously scan all registered accounts at 12:00 and 18:00 "
            "Asia/Ho_Chi_Minh time."
        ),
    )
    mode.add_argument(
        "--all-accounts",
        action="store_true",
        help="Scan all registered accounts once, sequentially.",
    )
    mode.add_argument(
        "--account-id",
        default=os.getenv(
            "OUTREACH_REPLY_CHECK_ACCOUNT_ID",
            DEFAULT_ACCOUNT_ID,
        ),
        help=(
            "Outreach account whose persistent LinkedIn profile is used "
            f"(default: {DEFAULT_ACCOUNT_ID})."
        ),
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    args = _parse_args()
    if args.schedule:
        run_reply_check_schedule(
            run_scheduled_reply_check,
            process_manual_request=process_manual_reply_check_request,
        )
    elif args.all_accounts:
        run_scheduled_reply_check()
    else:
        run_once(str(args.account_id).strip())


if __name__ == "__main__":
    main()
