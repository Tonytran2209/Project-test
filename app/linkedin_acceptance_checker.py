from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Literal

from playwright.sync_api import (
    Locator,
    Page,
    TimeoutError as PlaywrightTimeoutError,
)

from app.linkedin_browser import (
    LinkedInBrowserManager,
    LinkedInBrowserTimeoutError,
    LinkedInSessionError,
)


# =========================================================
# CONSTANTS
# =========================================================

PROFILE_TIMEOUT_MS = 15_000
MENU_VERIFY_WINDOW_MS = 1_500
STATE_POLL_MS = 120
MORE_MAX_ATTEMPTS = 2
PROFILE_SETTLE_DELAY_MS = 900
BEFORE_MENU_OPEN_DELAY_MS = 450
AFTER_MENU_OPEN_DELAY_MS = 500


AcceptanceStatus = Literal[
    "pending",
    "accepted",
    "declined_or_unknown",
    "check_failed",
]


@dataclass(frozen=True)
class LinkedInAcceptanceResult:
    linkedin_url: str
    final_url: str
    status: AcceptanceStatus
    message: str


class LinkedInAcceptanceCheckTimeout(RuntimeError):
    pass


# =========================================================
# TIMEOUT HELPERS
# =========================================================

def _build_deadline() -> float:
    return (
        time.monotonic()
        + (PROFILE_TIMEOUT_MS / 1000)
    )


def _check_deadline(
    deadline: float,
) -> None:
    if time.monotonic() >= deadline:
        raise LinkedInAcceptanceCheckTimeout(
            "Acceptance check exceeded "
            "the profile timeout."
        )


def _remaining_ms(
    deadline: float,
    *,
    maximum_ms: int,
) -> int:
    remaining = int(
        (
            deadline
            - time.monotonic()
        )
        * 1000
    )

    if remaining <= 0:
        raise LinkedInAcceptanceCheckTimeout(
            "Acceptance check exceeded "
            "the profile timeout."
        )

    return max(
        1,
        min(
            remaining,
            maximum_ms,
        ),
    )


def _sleep(
    page: Page,
    *,
    deadline: float,
    milliseconds: int,
) -> None:
    timeout = _remaining_ms(
        deadline,
        maximum_ms=milliseconds,
    )

    page.wait_for_timeout(
        min(
            timeout,
            milliseconds,
        )
    )


# =========================================================
# BASIC LOCATOR HELPERS
# =========================================================

def _is_visible_locator(
    locator: Locator,
    *,
    deadline: float,
    maximum_ms: int = 180,
) -> bool:
    _check_deadline(deadline)

    try:
        return locator.is_visible(
            timeout=_remaining_ms(
                deadline,
                maximum_ms=maximum_ms,
            )
        )

    except LinkedInAcceptanceCheckTimeout:
        raise

    except Exception:
        return False


def _click_locator(
    locator: Locator,
    *,
    deadline: float,
    maximum_ms: int = 500,
) -> bool:
    """
    Acceptance checker only clicks menu openers.

    Prefer Playwright click first.
    JS click is fallback only.
    """
    _check_deadline(deadline)

    try:
        locator.click(
            timeout=_remaining_ms(
                deadline,
                maximum_ms=maximum_ms,
            )
        )
        return True

    except Exception:
        pass

    try:
        locator.evaluate(
            """
            (element) => {
                element.scrollIntoView({
                    block: 'center',
                    inline: 'center'
                });
                element.click();
            }
            """
        )
        return True

    except Exception:
        return False


def _normalize_text(
    locator: Locator,
) -> str:
    try:
        value = (
            locator.inner_text()
            or ""
        )

    except Exception:
        value = ""

    return " ".join(
        value.split()
    ).strip()


# =========================================================
# PROFILE STATE
# =========================================================

def _is_profile_not_found(
    page: Page,
    *,
    deadline: float,
) -> bool:
    current_url = (
        page.url
        or ""
    ).lower()

    if (
        "/404" in current_url
        or "/error" in current_url
    ):
        return True

    try:
        body_text = (
            page.locator("body")
            .inner_text(
                timeout=_remaining_ms(
                    deadline,
                    maximum_ms=600,
                )
            )
            .lower()
        )

    except LinkedInAcceptanceCheckTimeout:
        raise

    except Exception:
        return False

    signals = (
        "this page doesn’t exist",
        "this page doesn't exist",
        "page not found",
        "profile not found",
        "this profile is not available",
        "the profile you requested does not exist",
    )

    return any(
        signal in body_text
        for signal in signals
    )


def _has_pending_state(
    page: Page,
    *,
    deadline: float,
) -> bool:
    """
    CASE 1:
    Current profile visibly shows Pending.

    Scope to <main> so unrelated page content does not
    create a false Pending state.
    """
    _check_deadline(deadline)

    try:
        main = page.locator("main")

        if main.count() == 0:
            print(
                "ACCEPTANCE PENDING: "
                "<main> not found"
            )
            return False

        selectors = (
            "button:has-text('Pending')",
            "[role='button']:has-text('Pending')",
            "a:has-text('Pending')",
            "[aria-label*='Pending']",
            "[aria-label*='pending']",
        )

        for selector in selectors:
            _check_deadline(deadline)

            candidates = main.locator(
                selector
            )

            for index in range(
                candidates.count()
            ):
                candidate = candidates.nth(
                    index
                )

                if not _is_visible_locator(
                    candidate,
                    deadline=deadline,
                    maximum_ms=140,
                ):
                    continue

                text_value = (
                    _normalize_text(
                        candidate
                    )
                    .lower()
                )

                try:
                    aria_label = (
                        candidate.get_attribute(
                            "aria-label"
                        )
                        or ""
                    ).strip().lower()

                except Exception:
                    aria_label = ""

                if (
                    text_value == "pending"
                    or "pending" in aria_label
                ):
                    print(
                        "ACCEPTANCE STATE: pending"
                    )
                    return True

    except LinkedInAcceptanceCheckTimeout:
        raise

    except Exception as exc:
        print(
            "ACCEPTANCE PENDING error:",
            f"{type(exc).__name__}: {exc}",
        )

    return False


# =========================================================
# SHARED MENU READ HELPER
# =========================================================

def _visible_menu_exists(
    page: Page,
    *,
    deadline: float,
) -> bool:
    """
    Read-only helper.

    Only answers whether at least one visible [role='menu']
    currently exists.
    """
    _check_deadline(deadline)

    try:
        menus = page.locator(
            "[role='menu']"
        )

        for index in range(
            menus.count()
        ):
            if _is_visible_locator(
                menus.nth(index),
                deadline=deadline,
                maximum_ms=100,
            ):
                return True

    except LinkedInAcceptanceCheckTimeout:
        raise

    except Exception:
        pass

    return False


def _wait_for_visible_menu(
    page: Page,
    *,
    deadline: float,
) -> bool:
    wait_deadline = min(
        deadline,
        time.monotonic()
        + (MENU_VERIFY_WINDOW_MS / 1000),
    )

    while (
        time.monotonic()
        < wait_deadline
    ):
        _check_deadline(deadline)

        if _visible_menu_exists(
            page,
            deadline=deadline,
        ):
            return True

        _sleep(
            page,
            deadline=deadline,
            milliseconds=STATE_POLL_MS,
        )

    return False


# =========================================================
# ACCEPTANCE CASE 2:
# ELLIPSIS / THREE-DOT MENU
# =========================================================

def _open_acceptance_ellipsis_menu(
    page: Page,
    *,
    deadline: float,
) -> bool:
    """
    ACCEPTANCE CASE 2 ONLY.

    Open the profile ellipsis / three-dot menu.

    IMPORTANT:
    - Completely separate from Connect CASE 2.
    - Completely separate from Acceptance More path.
    - Does NOT call _open_acceptance_more_menu().
    - Ignores a button whose visible text is exactly "More".
    - Does not use x/y positioning.
    """
    _check_deadline(deadline)

    selectors = (
        "button[aria-label='More actions']",
        "button[aria-label*='More actions']",
        "button[aria-label='More']",
        "button[title='More actions']",
        "button[title='More']",
    )

    seen: set[str] = set()

    for selector in selectors:
        _check_deadline(deadline)

        try:
            candidates = page.locator(
                selector
            )

            for index in range(
                candidates.count()
            ):
                button = candidates.nth(
                    index
                )

                if not _is_visible_locator(
                    button,
                    deadline=deadline,
                    maximum_ms=180,
                ):
                    continue

                visible_text = (
                    _normalize_text(
                        button
                    )
                    .lower()
                )

                # Critical isolation:
                # visible text "More" belongs to the other path.
                if visible_text == "more":
                    continue

                try:
                    key = button.evaluate(
                        """
                        (el) => {
                            if (!el.dataset.acceptanceEllipsisKey) {
                                el.dataset.acceptanceEllipsisKey =
                                    Math.random().toString(36).slice(2);
                            }
                            return el.dataset.acceptanceEllipsisKey;
                        }
                        """
                    )

                except Exception:
                    key = (
                        f"{selector}:{index}"
                    )

                if key in seen:
                    continue

                seen.add(key)

                try:
                    aria_label = (
                        button.get_attribute(
                            "aria-label"
                        )
                        or ""
                    )

                except Exception:
                    aria_label = ""

                try:
                    title = (
                        button.get_attribute(
                            "title"
                        )
                        or ""
                    )

                except Exception:
                    title = ""

                print(
                    "ACCEPTANCE ELLIPSIS candidate:",
                    "aria-label=",
                    repr(aria_label),
                    "title=",
                    repr(title),
                )

                try:
                    expanded = (
                        button.get_attribute(
                            "aria-expanded"
                        )
                        or ""
                    ).strip().lower()

                except Exception:
                    expanded = ""

                if (
                    expanded == "true"
                    and _visible_menu_exists(
                        page,
                        deadline=deadline,
                    )
                ):
                    print(
                        "ACCEPTANCE ELLIPSIS: "
                        "menu already open"
                    )
                    return True

                _sleep(
                    page,
                    deadline=deadline,
                    milliseconds=BEFORE_MENU_OPEN_DELAY_MS,
                )

                if not _click_locator(
                    button,
                    deadline=deadline,
                    maximum_ms=500,
                ):
                    print(
                        "ACCEPTANCE ELLIPSIS: "
                        "candidate click failed"
                    )
                    continue

                print(
                    "ACCEPTANCE ELLIPSIS: clicked"
                )

                if _wait_for_visible_menu(
                    page,
                    deadline=deadline,
                ):
                    _sleep(
                        page,
                        deadline=deadline,
                        milliseconds=AFTER_MENU_OPEN_DELAY_MS,
                    )

                    print(
                        "ACCEPTANCE ELLIPSIS: "
                        "visible role=menu confirmed"
                    )
                    return True

                print(
                    "ACCEPTANCE ELLIPSIS: "
                    "click completed but menu "
                    "was not confirmed"
                )

        except LinkedInAcceptanceCheckTimeout:
            raise

        except Exception as exc:
            print(
                "ACCEPTANCE ELLIPSIS error:",
                f"{type(exc).__name__}: {exc}",
            )

    print(
        "ACCEPTANCE ELLIPSIS: "
        "no valid overflow button opened"
    )

    return False


def _has_remove_connection_in_ellipsis_menu(
    page: Page,
    *,
    deadline: float,
) -> bool:
    """
    ACCEPTANCE CASE 2 ONLY.

    Inspect visible role=menu / role=menuitem nodes after
    the ellipsis path has opened its menu.

    Exact accepted signal:
        exact visible text == "Remove connection"

    NEVER clicks Remove connection.
    """
    _check_deadline(deadline)

    menus = page.locator(
        "[role='menu']"
    )

    visible_menu_found = False

    for menu_index in range(
        menus.count()
    ):
        menu = menus.nth(
            menu_index
        )

        if not _is_visible_locator(
            menu,
            deadline=deadline,
            maximum_ms=120,
        ):
            continue

        visible_menu_found = True

        menuitems = menu.locator(
            "[role='menuitem']"
        )

        for item_index in range(
            menuitems.count()
        ):
            item = menuitems.nth(
                item_index
            )

            if not _is_visible_locator(
                item,
                deadline=deadline,
                maximum_ms=120,
            ):
                continue

            text_value = (
                _normalize_text(
                    item
                )
            )

            print(
                "ACCEPTANCE ELLIPSIS MENUITEM:",
                item_index,
                repr(text_value),
            )

            if (
                text_value.lower()
                == "remove connection"
            ):
                print(
                    "ACCEPTANCE ELLIPSIS: "
                    "Remove connection found"
                )
                return True

    if not visible_menu_found:
        raise RuntimeError(
            "Ellipsis menu is not visible."
        )

    return False


# =========================================================
# ACCEPTANCE CASE 3:
# TEXT "MORE" MENU
# =========================================================

def _open_acceptance_more_menu(
    page: Page,
    *,
    deadline: float,
) -> bool:
    """
    ACCEPTANCE CASE 3 ONLY.

    Open the profile's visible text button "More".

    IMPORTANT:
    - Completely separate from ellipsis path.
    - Does NOT call _open_acceptance_ellipsis_menu().
    - Scope to <main>.
    - Exact visible text "More".
    - The text match itself may be the button, or a child inside it.
    - aria-expanded is optional; verify that the menu actually opens instead.
    - No x/y positioning.
    """
    _check_deadline(deadline)

    for attempt in range(
        1,
        MORE_MAX_ATTEMPTS + 1,
    ):
        print(
            "ACCEPTANCE MORE attempt "
            f"{attempt}/{MORE_MAX_ATTEMPTS}"
        )

        try:
            main = page.locator(
                "main"
            )

            if main.count() == 0:
                print(
                    "ACCEPTANCE MORE: "
                    "<main> not found"
                )
                _sleep(page, deadline=deadline, milliseconds=STATE_POLL_MS)
                continue

            more_texts = (
                main.get_by_text(
                    "More",
                    exact=True,
                )
            )

            buttons: list[Locator] = []
            seen: set[str] = set()

            for index in range(
                more_texts.count()
            ):
                _check_deadline(deadline)

                node = more_texts.nth(
                    index
                )

                if not _is_visible_locator(
                    node,
                    deadline=deadline,
                    maximum_ms=180,
                ):
                    continue

                button = node.locator(
                    "xpath=ancestor-or-self::*[self::button or @role='button'][1]"
                )

                if button.count() == 0:
                    continue

                button = button.first

                if not _is_visible_locator(
                    button,
                    deadline=deadline,
                    maximum_ms=180,
                ):
                    continue

                try:
                    key = button.evaluate(
                        """
                        (el) => {
                            if (!el.dataset.acceptanceMoreKey) {
                                el.dataset.acceptanceMoreKey =
                                    Math.random().toString(36).slice(2);
                            }
                            return el.dataset.acceptanceMoreKey;
                        }
                        """
                    )

                except Exception:
                    key = str(index)

                if key in seen:
                    continue

                seen.add(key)
                buttons.append(
                    button
                )

            print(
                "ACCEPTANCE MORE: "
                "profile candidates inside <main> =",
                len(buttons),
            )

            if not buttons:
                print(
                    "ACCEPTANCE MORE: "
                    "no visible button "
                    "with exact text More "
                    "inside <main>"
                )
                _sleep(page, deadline=deadline, milliseconds=STATE_POLL_MS)
                continue

            for candidate_index, button in enumerate(
                buttons,
                start=1,
            ):
                try:
                    current_state = (
                        button.get_attribute(
                            "aria-expanded"
                        )
                        or ""
                    ).strip().lower()

                except Exception:
                    current_state = ""

                print(
                    "ACCEPTANCE MORE profile candidate",
                    candidate_index,
                    "aria-expanded=",
                    current_state,
                )

                if (
                    current_state == "true"
                    and _visible_menu_exists(
                        page,
                        deadline=deadline,
                    )
                ):
                    print(
                        "ACCEPTANCE MORE: "
                        "menu already open"
                    )
                    return True

                _sleep(
                    page,
                    deadline=deadline,
                    milliseconds=BEFORE_MENU_OPEN_DELAY_MS,
                )

                if not _click_locator(
                    button,
                    deadline=deadline,
                    maximum_ms=500,
                ):
                    print(
                        "ACCEPTANCE MORE: "
                        "candidate click failed"
                    )
                    continue

                print("ACCEPTANCE MORE: clicked")

                if _wait_for_visible_menu(
                    page,
                    deadline=deadline,
                ):
                    _sleep(
                        page,
                        deadline=deadline,
                        milliseconds=AFTER_MENU_OPEN_DELAY_MS,
                    )

                    print(
                        "ACCEPTANCE MORE: "
                        "visible role=menu confirmed"
                    )
                    return True

                print(
                    "ACCEPTANCE MORE: "
                    "click completed but menu "
                    "was not confirmed"
                )

        except LinkedInAcceptanceCheckTimeout:
            raise

        except Exception as exc:
            print(
                "ACCEPTANCE MORE error:",
                f"{type(exc).__name__}: {exc}",
            )

        if attempt < MORE_MAX_ATTEMPTS:
            _sleep(
                page,
                deadline=deadline,
                milliseconds=120,
            )

    print(
        "ACCEPTANCE MORE: "
        "menu could not be opened"
    )

    return False


def _has_remove_connection_in_more_menu(
    page: Page,
    *,
    deadline: float,
) -> bool:
    """
    ACCEPTANCE CASE 3 ONLY.

    Inspect only visible role=menu containers opened by
    the text More path.

    DOM confirmed:
        <div role="menuitem"> ... Remove connection ... </div>

    Exact accepted signal:
        exact visible text == "Remove connection"

    NEVER clicks Remove connection.
    """
    _check_deadline(deadline)

    menus = page.locator(
        "[role='menu']"
    )

    visible_menu_found = False

    for menu_index in range(
        menus.count()
    ):
        menu = menus.nth(
            menu_index
        )

        if not _is_visible_locator(
            menu,
            deadline=deadline,
            maximum_ms=120,
        ):
            continue

        visible_menu_found = True

        menuitems = menu.locator(
            "[role='menuitem']"
        )

        print(
            "ACCEPTANCE MORE MENU:",
            menu_index,
            "menuitems=",
            menuitems.count(),
        )

        for item_index in range(
            menuitems.count()
        ):
            item = menuitems.nth(
                item_index
            )

            if not _is_visible_locator(
                item,
                deadline=deadline,
                maximum_ms=120,
            ):
                continue

            text_value = (
                _normalize_text(
                    item
                )
            )

            print(
                "ACCEPTANCE MORE MENUITEM:",
                item_index,
                repr(text_value),
            )

            if (
                text_value.lower()
                == "remove connection"
            ):
                print(
                    "ACCEPTANCE MORE: "
                    "Remove connection found"
                )
                return True

    if not visible_menu_found:
        raise RuntimeError(
            "More menu is not visible."
        )

    return False


# =========================================================
# MAIN ACCEPTANCE CHECK
# =========================================================

def check_profile_acceptance(
    *,
    browser: LinkedInBrowserManager,
    linkedin_url: str,
) -> LinkedInAcceptanceResult:
    """
    READ-ONLY acceptance checker.

    STATE RULES:

    CASE 1
        Pending visible
        -> pending

    CASE 2
        No Pending
        -> try ellipsis / three-dot menu
        -> exact "Remove connection"
        -> accepted

    CASE 3
        If ellipsis path does not confirm accepted
        -> try text "More" menu
        -> exact "Remove connection"
        -> accepted

    FINAL NON-ACCEPTED STATE
        At least one menu path opened successfully
        but neither path contained "Remove connection"
        -> declined_or_unknown

    TECHNICAL FAILURE
        Neither menu path can be opened
        OR navigation/session/browser error
        -> check_failed

    This checker NEVER clicks:
    - Connect
    - Remove connection
    - Message
    - Follow
    """
    cleaned_url = str(
        linkedin_url
        or ""
    ).strip()

    if not cleaned_url:
        return LinkedInAcceptanceResult(
            linkedin_url="",
            final_url="",
            status="check_failed",
            message=(
                "invalid_url: LinkedIn URL "
                "cannot be empty."
            ),
        )

    deadline = _build_deadline()
    page: Page | None = None

    try:
        print("")
        print("=" * 60)
        print("LINKEDIN ACCEPTANCE CHECK")
        print("=" * 60)
        print(
            f"URL: {cleaned_url}"
        )

        page = browser.open_linkedin_url(
            cleaned_url,
            overall_timeout_ms=_remaining_ms(
                deadline,
                maximum_ms=PROFILE_TIMEOUT_MS,
            ),
            raise_on_navigation_timeout=True,
        )

        _check_deadline(deadline)

        # Small fixed pause so LinkedIn's UI has time to finish rendering.
        # This is stability pacing, not selector logic.
        _sleep(
            page,
            deadline=deadline,
            milliseconds=PROFILE_SETTLE_DELAY_MS,
        )

        if _is_profile_not_found(
            page,
            deadline=deadline,
        ):
            return LinkedInAcceptanceResult(
                linkedin_url=cleaned_url,
                final_url=page.url,
                status="check_failed",
                message=(
                    "url_not_found: LinkedIn profile "
                    "does not exist or is unavailable."
                ),
            )

        # -------------------------------------------------
        # CASE 1: PENDING
        # -------------------------------------------------
        print(
            "Checking ACCEPTANCE CASE 1: Pending"
        )

        if _has_pending_state(
            page,
            deadline=deadline,
        ):
            return LinkedInAcceptanceResult(
                linkedin_url=cleaned_url,
                final_url=page.url,
                status="pending",
                message=(
                    "Connection invitation is "
                    "still pending."
                ),
            )

        # Track whether we successfully inspected at least one menu.
        inspected_menu = False

        # -------------------------------------------------
        # CASE 2: ELLIPSIS / THREE-DOT
        # -------------------------------------------------
        print(
            "Checking ACCEPTANCE CASE 2: "
            "three-dot / ellipsis menu"
        )

        ellipsis_opened = (
            _open_acceptance_ellipsis_menu(
                page,
                deadline=deadline,
            )
        )

        if ellipsis_opened:
            inspected_menu = True

            if _has_remove_connection_in_ellipsis_menu(
                page,
                deadline=deadline,
            ):
                return LinkedInAcceptanceResult(
                    linkedin_url=cleaned_url,
                    final_url=page.url,
                    status="accepted",
                    message=(
                        "Connection accepted: "
                        "'Remove connection' was found "
                        "in the ellipsis menu."
                    ),
                )

            print(
                "ACCEPTANCE CASE 2: "
                "Remove connection not found"
            )

        else:
            print(
                "ACCEPTANCE CASE 2: "
                "ellipsis menu not opened"
            )

        # -------------------------------------------------
        # CASE 3: TEXT MORE
        # -------------------------------------------------
        print(
            "Checking ACCEPTANCE CASE 3: "
            "text More menu"
        )

        more_opened = (
            _open_acceptance_more_menu(
                page,
                deadline=deadline,
            )
        )

        if more_opened:
            inspected_menu = True

            if _has_remove_connection_in_more_menu(
                page,
                deadline=deadline,
            ):
                return LinkedInAcceptanceResult(
                    linkedin_url=cleaned_url,
                    final_url=page.url,
                    status="accepted",
                    message=(
                        "Connection accepted: "
                        "'Remove connection' was found "
                        "in the More menu."
                    ),
                )

            print(
                "ACCEPTANCE CASE 3: "
                "Remove connection not found"
            )

        else:
            print(
                "ACCEPTANCE CASE 3: "
                "More menu not opened"
            )

        # -------------------------------------------------
        # FINAL STATE
        # -------------------------------------------------
        if inspected_menu:
            print(
                "ACCEPTANCE STATE: "
                "declined_or_unknown"
            )

            return LinkedInAcceptanceResult(
                linkedin_url=cleaned_url,
                final_url=page.url,
                status="declined_or_unknown",
                message=(
                    "Pending is not visible and "
                    "'Remove connection' was not found "
                    "in the available profile menus."
                ),
            )

        print(
            "ACCEPTANCE STATE: check_failed"
        )

        return LinkedInAcceptanceResult(
            linkedin_url=cleaned_url,
            final_url=page.url,
            status="check_failed",
            message=(
                "menu_error: Could not open either "
                "the profile ellipsis menu or "
                "the text More menu."
            ),
        )

    except (
        LinkedInAcceptanceCheckTimeout,
        LinkedInBrowserTimeoutError,
        PlaywrightTimeoutError,
    ) as exc:
        return LinkedInAcceptanceResult(
            linkedin_url=cleaned_url,
            final_url=(
                page.url
                if page is not None
                else ""
            ),
            status="check_failed",
            message=(
                "timeout: acceptance check failed. "
                f"{exc}"
            ),
        )

    except LinkedInSessionError as exc:
        return LinkedInAcceptanceResult(
            linkedin_url=cleaned_url,
            final_url=(
                page.url
                if page is not None
                else ""
            ),
            status="check_failed",
            message=(
                f"session_error: {exc}"
            ),
        )

    except Exception as exc:
        return LinkedInAcceptanceResult(
            linkedin_url=cleaned_url,
            final_url=(
                page.url
                if page is not None
                else ""
            ),
            status="check_failed",
            message=(
                "acceptance_error: "
                f"{type(exc).__name__}: {exc}"
            ),
        )
