from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from app.linkedin_browser import (
    LinkedInBrowserManager,
    LinkedInBrowserSettings,
)


DEFAULT_OUTREACH_ACCOUNT_IDS = (
    "outreach_account_01",
    "outreach_account_02",
    "outreach_account_03",
    "outreach_account_04",
    "outreach_account_05",
    "outreach_account_06",
    "outreach_account_07",
)

LEGACY_OUTREACH_ACCOUNT_IDS = frozenset(
    f"outreach_account_{number:02d}" for number in range(1, 6)
)


# =========================================================
# DISPLAY NAMES
# =========================================================
#
# CHỈ ĐỔI TÊN HIỂN THỊ Ở ĐÂY.
# KHÔNG đổi account_id vì account_id đang gắn với:
# - browser profile folder
# - scheduler state
# - Supabase records
#
OUTREACH_ACCOUNT_DISPLAY_NAMES = {
    "outreach_account_01": "Minh Anh",
    "outreach_account_02": "Trang Liu",
    "outreach_account_03": "Minh Ánh",
    "outreach_account_04": "Linh Giang",
    "outreach_account_05": "Huyền Linh",
    "outreach_account_06": "Frank Nguyen",
    "outreach_account_07": "Phoebe",
}

DEFAULT_OUTREACH_PROFILE_ROOT = (
    "outreach_browser_profiles"
)

DEFAULT_PROFILES_PER_ACCOUNT_TURN = 10


def _read_positive_int_env(
    key: str,
    *,
    default: int,
    maximum: int | None = None,
) -> int:
    raw_value = os.getenv(key)

    if raw_value is None:
        value = default
    else:
        try:
            value = int(
                raw_value.strip()
            )
        except ValueError as exc:
            raise ValueError(
                f"{key} must be an integer"
            ) from exc

    if value < 1:
        raise ValueError(
            f"{key} must be at least 1"
        )

    if (
        maximum is not None
        and value > maximum
    ):
        raise ValueError(
            f"{key} cannot exceed {maximum}"
        )

    return value


def _read_outreach_account_ids(
) -> tuple[str, ...]:
    """
    Cho phép override danh sách Outreach account
    qua .env.

    Ví dụ:
        OUTREACH_ACCOUNT_IDS=
        outreach_account_01,outreach_account_02

    Nếu không cấu hình,
    mặc định dùng toàn bộ account đã đăng ký.
    """

    raw_value = os.getenv(
        "OUTREACH_ACCOUNT_IDS",
        "",
    ).strip()

    if not raw_value:
        return DEFAULT_OUTREACH_ACCOUNT_IDS

    account_ids: list[str] = []
    seen: set[str] = set()

    for raw_account_id in raw_value.split(","):
        account_id = (
            raw_account_id.strip()
        )

        if not account_id:
            continue

        if account_id in seen:
            continue

        seen.add(account_id)
        account_ids.append(account_id)

    if not account_ids:
        raise ValueError(
            "OUTREACH_ACCOUNT_IDS does not "
            "contain any valid account ID"
        )

    # Older .env files explicitly listed the original complete pool. Expand
    # that legacy configuration as the registered pool grows. Intentional
    # smaller/custom pools still keep their configured membership and order.
    if LEGACY_OUTREACH_ACCOUNT_IDS.issubset(seen) and seen.issubset(DEFAULT_OUTREACH_ACCOUNT_IDS):
        additions = [account_id for account_id in DEFAULT_OUTREACH_ACCOUNT_IDS if account_id not in seen]
        account_ids.extend(additions)
        if additions:
            logging.getLogger(__name__).warning(
                "Upgrading legacy OUTREACH_ACCOUNT_IDS configuration; added: %s",
                ", ".join(additions),
            )

    return tuple(account_ids)


@dataclass(frozen=True)
class OutreachAccount:
    """
    Một Outreach account tương ứng
    với một LinkedIn browser profile.

    Không chứa email hoặc password.

    Session đăng nhập LinkedIn được lưu
    trong profile_directory.
    """

    account_id: str
    display_name: str
    profile_directory: Path
    enabled: bool = True

    @property
    def exists(self) -> bool:
        return self.profile_directory.exists()

    def create_browser_settings(
        self,
    ) -> LinkedInBrowserSettings:
        base_settings = (
            LinkedInBrowserSettings
            .from_environment()
        )

        return LinkedInBrowserSettings(
            profile_directory=(
                self.profile_directory
            ),
            headless=base_settings.headless,
            navigation_timeout_ms=(
                base_settings
                .navigation_timeout_ms
            ),
            operation_timeout_ms=(
                base_settings
                .operation_timeout_ms
            ),
            slow_mo_ms=(
                base_settings.slow_mo_ms
            ),
            viewport_width=(
                base_settings.viewport_width
            ),
            viewport_height=(
                base_settings.viewport_height
            ),
        )

    def create_browser_manager(
        self,
    ) -> LinkedInBrowserManager:
        return LinkedInBrowserManager(
            settings=(
                self.create_browser_settings()
            )
        )


@dataclass(frozen=True)
class OutreachAccountPoolSettings:
    """
    Cấu hình cho pool Outreach.

    profile_root:
        Folder chứa browser profile.

    account_ids:
        Danh sách account Outreach.

    profiles_per_account_turn:
        Số profile tối đa một account
        xử lý trong một turn.
    """

    profile_root: Path
    account_ids: tuple[str, ...]
    profiles_per_account_turn: int

    @classmethod
    def from_environment(
        cls,
        project_root: Path | None = None,
    ) -> "OutreachAccountPoolSettings":
        root = (
            project_root
            if project_root is not None
            else Path.cwd()
        )

        raw_profile_root = os.getenv(
            "OUTREACH_ACCOUNT_PROFILE_ROOT",
            DEFAULT_OUTREACH_PROFILE_ROOT,
        ).strip()

        profile_root = Path(
            raw_profile_root
        )

        if not profile_root.is_absolute():
            profile_root = (
                root / profile_root
            ).resolve()

        return cls(
            profile_root=profile_root,
            account_ids=(
                _read_outreach_account_ids()
            ),
            profiles_per_account_turn=(
                _read_positive_int_env(
                    "OUTREACH_PROFILES_PER_ACCOUNT_TURN",
                    default=(
                        DEFAULT_PROFILES_PER_ACCOUNT_TURN
                    ),
                    maximum=10,
                )
            ),
        )


class OutreachAccountPool:
    """
    Quản lý các browser sessions
    dành riêng cho Outreach.

    Pool này dùng chung cho:
    - LinkedIn Connect
    - Mass Send sau này

    _next_index chỉ giữ con trỏ
    trong memory.

    Persistent state thực sự sẽ được
    lưu trong Supabase bởi scheduler.
    """

    def __init__(
        self,
        settings: (
            OutreachAccountPoolSettings
            | None
        ) = None,
    ) -> None:
        self.settings = (
            settings
            if settings is not None
            else (
                OutreachAccountPoolSettings
                .from_environment()
            )
        )

        self.accounts = tuple(
            OutreachAccount(
                account_id=account_id,
                display_name=(
                    OUTREACH_ACCOUNT_DISPLAY_NAMES
                    .get(
                        account_id,
                        account_id,
                    )
                ),
                profile_directory=(
                    self.settings
                    .profile_root
                    / account_id
                ).resolve(),
                enabled=True,
            )
            for account_id
            in self.settings.account_ids
        )

        if not self.accounts:
            raise RuntimeError(
                "Outreach account pool is empty"
            )

        self._next_index = 0

    @property
    def next_account_id(self) -> str:
        return self.accounts[
            self._next_index
        ].account_id

    def validate_profiles(
        self,
    ) -> list[str]:
        """
        Kiểm tra browser profile
        của từng Outreach account.

        Trả về list lỗi.
        Nếu list rỗng nghĩa là OK.
        """

        errors: list[str] = []

        for account in self.accounts:
            if (
                not account
                .profile_directory
                .exists()
            ):
                errors.append(
                    f"{account.account_id}: "
                    "profile directory does not exist"
                )
                continue

            try:
                has_files = any(
                    account
                    .profile_directory
                    .iterdir()
                )
            except OSError as exc:
                errors.append(
                    f"{account.account_id}: "
                    "cannot read profile directory: "
                    f"{exc}"
                )
                continue

            if not has_files:
                errors.append(
                    f"{account.account_id}: "
                    "profile directory is empty"
                )

        return errors

    def get_account(
        self,
        account_id: str,
    ) -> OutreachAccount:
        cleaned_account_id = str(
            account_id or ""
        ).strip()

        for account in self.accounts:
            if (
                account.account_id
                == cleaned_account_id
            ):
                return account

        raise KeyError(
            "Outreach account not found: "
            f"{cleaned_account_id}"
        )

    def get_account_index(
        self,
        account_id: str,
    ) -> int:
        cleaned_account_id = str(
            account_id or ""
        ).strip()

        for index, account in enumerate(
            self.accounts
        ):
            if (
                account.account_id
                == cleaned_account_id
            ):
                return index

        raise KeyError(
            "Outreach account not found: "
            f"{cleaned_account_id}"
        )

    def get_next_account(
        self,
    ) -> OutreachAccount:
        """
        Lấy account hiện tại
        rồi dịch con trỏ sang account sau.

        Ví dụ:
        outreach_account_01
        → outreach_account_02
        """

        account = self.accounts[
            self._next_index
        ]

        self._next_index = (
            self._next_index + 1
        ) % len(self.accounts)

        return account

    def set_next_account(
        self,
        account_id: str,
    ) -> None:
        """
        Chỉ định account sẽ chạy
        ở lượt tiếp theo.
        """

        self._next_index = (
            self.get_account_index(
                account_id
            )
        )

    def set_next_after(
        self,
        account_id: str | None,
    ) -> None:
        """
        Đặt account tiếp theo
        sau account vừa hoàn thành turn.

        Ví dụ:

        outreach_account_02
        → next = outreach_account_03
        """

        if not account_id:
            self._next_index = 0
            return

        try:
            last_index = (
                self.get_account_index(
                    account_id
                )
            )
        except KeyError:
            self._next_index = 0
            return

        self._next_index = (
            last_index + 1
        ) % len(self.accounts)

    def iter_round_robin(
        self,
    ) -> Iterator[OutreachAccount]:
        while True:
            yield self.get_next_account()

    def list_accounts(
        self,
    ) -> list[dict[str, str | bool]]:
        """
        Dùng cho debug / Dashboard sau này.
        """

        return [
            {
                "account_id": (
                    account.account_id
                ),
                "display_name": (
                    account.display_name
                ),
                "profile_directory": str(
                    account.profile_directory
                ),
                "profile_exists": (
                    account.exists
                ),
                "enabled": account.enabled,
            }
            for account in self.accounts
        ]
