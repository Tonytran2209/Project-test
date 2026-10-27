from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import signal
import sys
import time
from dataclasses import dataclass
from typing import Any

from app.linkedin_acceptance_checker import (
    LinkedInAcceptanceResult,
    check_profile_acceptance,
)
from app.outreach_acceptance_store import (
    claim_next_pending_acceptance_check,
    get_outreach_supabase_client,
    group_targets_by_account,
    load_acceptance_targets,
    save_acceptance_result,
    update_acceptance_check_run,
)
from app.outreach_account_pool import (
    OutreachAccountPool,
)
from app.outreach_acceptance_schedule import AcceptanceSchedule
from app.outreach_acceptance_recheck import scan_connect_week


# =========================================================
# CONSTANTS
# =========================================================

IDLE_POLL_SECONDS = 10
PROFILE_DELAY_SECONDS = 2.5
ACCOUNT_SWITCH_DELAY_SECONDS = 5


# =========================================================
# DATA
# =========================================================

@dataclass
class AcceptanceRunCounters:
    checked_count: int = 0
    new_accepted_count: int = 0
    still_pending_count: int = 0
    declined_or_unknown_count: int = 0
    failed_count: int = 0


def _record_result(
    *,
    counters: AcceptanceRunCounters,
    result: LinkedInAcceptanceResult,
) -> None:
    counters.checked_count += 1

    if result.status == "accepted":
        counters.new_accepted_count += 1
        return

    if result.status == "pending":
        counters.still_pending_count += 1
        return

    if result.status == "declined_or_unknown":
        counters.declined_or_unknown_count += 1
        return

    counters.failed_count += 1


# =========================================================
# WORKER
# =========================================================

class OutreachAcceptanceWorker:
    """
    Always-on Mac worker for manual Acceptance Check runs.

    Railway only queues:
        outreach_acceptance_checks.status = pending

    This worker:
        pending
        -> claim as running
        -> read source_job_id
        -> load eligible targets
        -> group by assigned_account_id
        -> open the correct LinkedIn browser profile
        -> run read-only acceptance checker
        -> save target states
        -> complete the run

    It NEVER sends Connect requests.
    """

    def __init__(
        self,
        *, schedule_path: Path | None = None,
    ) -> None:
        self.client = (
            get_outreach_supabase_client()
        )

        self.account_pool = (
            OutreachAccountPool()
        )

        self._stop_requested = False
        self.schedule = AcceptanceSchedule(
            schedule_path, lambda week, checkpoint: scan_connect_week(self, week, checkpoint)
        ) if schedule_path is not None else None

    # =====================================================
    # RUN FOREVER
    # =====================================================

    def run_forever(
        self,
    ) -> int:
        self._register_signal_handlers()

        print("")
        print("=" * 60)
        print("OUTREACH ACCEPTANCE WORKER")
        print("=" * 60)
        print("Status: idle")
        print(
            "Poll interval:",
            f"{IDLE_POLL_SECONDS}s",
        )
        print(
            "Profile delay:",
            f"{PROFILE_DELAY_SECONDS}s",
        )
        print(
            "Account switch delay:",
            f"{ACCOUNT_SWITCH_DELAY_SECONDS}s",
        )
        print("Press Ctrl+C to stop.")

        try:
            while not self._stop_requested:
                self._prepare_ready_batches_safely()
                if self.schedule is not None:
                    try:
                        if self.schedule.tick(datetime.now(timezone.utc)):
                            continue
                    except Exception as exc:
                        print(f"Acceptance schedule error (progress preserved): {exc}", file=sys.stderr)
                        self._sleep_interruptibly(IDLE_POLL_SECONDS)
                        continue
                check_run = (
                    self._claim_next_check_safely()
                )

                if check_run is None:
                    self._sleep_interruptibly(
                        IDLE_POLL_SECONDS
                    )
                    continue

                started = datetime.now(timezone.utc)
                try:
                    self._process_check_run(check_run)
                finally:
                    if self.schedule is not None:
                        self.schedule.defer_busy_slots(started, datetime.now(timezone.utc))

            return 0

        except KeyboardInterrupt:
            self.request_stop()
            return 0

        finally:
            print("")
            print(
                "Outreach Acceptance Worker stopped."
            )

    # =====================================================
    # CLAIM
    # =====================================================

    def _prepare_ready_batches_safely(self, *, force=False):
        # @layer business
        # @feature messages
        now = time.monotonic()
        if not force and now - getattr(self, '_last_ready_prepare', -60) < 60:
            return
        self._last_ready_prepare = now
        try:
            from app.outreach_ready_batches import prepare_accepted_ready_batches
            summary = prepare_accepted_ready_batches(client=self.client)
            if summary['batches']:
                print('MESSAGES READY | batches=', len(summary['batches']), flush=True)
        except Exception as exc:
            # Acceptance must still be recorded if preparation/SQL is unavailable.
            print(f'Auto prepare failed (will retry): {type(exc).__name__}: {exc}', file=sys.stderr)

    def _claim_next_check_safely(
        self,
    ) -> dict | None:
        try:
            return (
                claim_next_pending_acceptance_check(
                    client=self.client
                )
            )

        except Exception as exc:
            print(
                (
                    "Could not claim Acceptance Check: "
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
                file=sys.stderr,
            )
            return None

    # =====================================================
    # PROCESS ONE CHECK RUN
    # =====================================================

    def _process_check_run(
        self,
        check_run: dict,
    ) -> None:
        check_id = str(
            check_run.get(
                "id",
                "",
            )
            or ""
        ).strip()

        source_job_id = str(
            check_run.get(
                "source_job_id",
                "",
            )
            or ""
        ).strip()

        run_number = int(
            check_run.get(
                "run_number",
                1,
            )
            or 1
        )

        print("")
        print("=" * 60)
        print("ACCEPTANCE CHECK CLAIMED")
        print("=" * 60)
        print(
            "Check ID:",
            check_id,
        )
        print(
            "Run number:",
            f"#{run_number}",
        )
        print(
            "Source job:",
            source_job_id,
        )

        counters = (
            AcceptanceRunCounters()
        )

        if (
            not check_id
            or not source_job_id
        ):
            print(
                "Invalid acceptance check row.",
                file=sys.stderr,
            )
            return

        try:
            targets = (
                load_acceptance_targets(
                    source_job_id=(
                        source_job_id
                    ),
                    client=self.client,
                )
            )

            print(
                "Targets to check:",
                len(targets),
            )

            # The queued total is a snapshot from button-click time.
            # The live target list is authoritative when worker starts.
            if not targets:
                update_acceptance_check_run(
                    check_id=check_id,
                    checked_count=0,
                    new_accepted_count=0,
                    still_pending_count=0,
                    declined_or_unknown_count=0,
                    failed_count=0,
                    completed=True,
                    client=self.client,
                )

                print(
                    "Nothing to check. Run completed."
                )
                return

            grouped = (
                group_targets_by_account(
                    targets
                )
            )

            previous_account_id: (
                str | None
            ) = None

            for (
                account_id,
                account_targets,
            ) in grouped.items():

                if self._stop_requested:
                    raise RuntimeError(
                        "Worker stop requested "
                        "before Acceptance Check completed."
                    )

                account = (
                    self.account_pool
                    .get_account(
                        account_id
                    )
                )

                # -----------------------------------------
                # ACCOUNT SWITCH DELAY
                # -----------------------------------------
                if (
                    previous_account_id
                    is not None
                    and previous_account_id
                    != account_id
                ):
                    print("")
                    print(
                        "Switching account:",
                        previous_account_id,
                        "->",
                        account_id,
                    )

                    print(
                        f"Waiting "
                        f"{ACCOUNT_SWITCH_DELAY_SECONDS}s "
                        "before next account..."
                    )

                    self._sleep_interruptibly(
                        ACCOUNT_SWITCH_DELAY_SECONDS
                    )

                    if self._stop_requested:
                        raise RuntimeError(
                            "Worker stop requested "
                            "during account switch."
                        )

                print("")
                print("=" * 60)
                print("ACCEPTANCE ACCOUNT")
                print("=" * 60)

                print(
                    "Account:",
                    account.display_name,
                    f"({account.account_id})",
                )

                print(
                    "Targets:",
                    len(account_targets),
                )

                browser = (
                    account
                    .create_browser_manager()
                )

                try:
                    browser.start()

                    for index, target in enumerate(
                        account_targets,
                        start=1,
                    ):
                        if self._stop_requested:
                            raise RuntimeError(
                                "Worker stop requested "
                                "during Acceptance Check."
                            )

                        print("")
                        print("-" * 60)

                        print(
                            f"[{index}/"
                            f"{len(account_targets)}]"
                        )

                        print(
                            "URL:",
                            target[
                                "linkedin_url"
                            ],
                        )

                        print(
                            "Previous acceptance state:",
                            target[
                                "acceptance_status"
                            ],
                        )

                        # ---------------------------------
                        # READ LINKEDIN STATE
                        # ---------------------------------
                        try:
                            result = (
                                check_profile_acceptance(
                                    browser=browser,
                                    linkedin_url=(
                                        target[
                                            "linkedin_url"
                                        ]
                                    ),
                                )
                            )

                        except Exception as exc:
                            result = (
                                LinkedInAcceptanceResult(
                                    linkedin_url=(
                                        target[
                                            "linkedin_url"
                                        ]
                                    ),
                                    final_url="",
                                    status="check_failed",
                                    message=(
                                        "worker_error: "
                                        f"{type(exc).__name__}: "
                                        f"{exc}"
                                    ),
                                )
                            )

                        # ---------------------------------
                        # SAVE TARGET
                        # ---------------------------------
                        save_acceptance_result(
                            target_id=(
                                target[
                                    "target_id"
                                ]
                            ),
                            result=result,
                            client=self.client,
                        )

                        _record_result(
                            counters=counters,
                            result=result,
                        )

                        if result.status == 'accepted':
                            try:
                                from app.linkedin_profile_message import get_profile_name
                                name = get_profile_name(browser.page)['first_name']
                                (self.client.table('outreach_job_targets')
                                 .update({'ready_first_name': name})
                                 .eq('id', target['target_id']).execute())
                            except Exception as exc:
                                print(f'Auto prepare name unavailable: {type(exc).__name__}: {exc}', file=sys.stderr)

                        # ---------------------------------
                        # LIVE RUN PROGRESS
                        # ---------------------------------
                        update_acceptance_check_run(
                            check_id=check_id,
                            checked_count=(
                                counters
                                .checked_count
                            ),
                            new_accepted_count=(
                                counters
                                .new_accepted_count
                            ),
                            still_pending_count=(
                                counters
                                .still_pending_count
                            ),
                            declined_or_unknown_count=(
                                counters
                                .declined_or_unknown_count
                            ),
                            failed_count=(
                                counters
                                .failed_count
                            ),
                            client=self.client,
                        )

                        print(
                            "Acceptance status:",
                            result.status,
                        )

                        print(
                            "Message:",
                            result.message,
                        )

                        print(
                            "Run progress:",
                            (
                                f"{counters.checked_count}"
                                f"/{len(targets)}"
                            ),
                        )

                        # ---------------------------------
                        # PROFILE DELAY
                        # ---------------------------------
                        if (
                            index
                            < len(account_targets)
                        ):
                            print(
                                f"Waiting "
                                f"{PROFILE_DELAY_SECONDS}s "
                                "before next profile..."
                            )

                            self._sleep_interruptibly(
                                PROFILE_DELAY_SECONDS
                            )

                finally:
                    try:
                        browser.stop()

                    except Exception as exc:
                        print(
                            "Could not close browser:",
                            (
                                f"{type(exc).__name__}: "
                                f"{exc}"
                            ),
                            file=sys.stderr,
                        )

                previous_account_id = (
                    account_id
                )

            # ---------------------------------------------
            # COMPLETE RUN
            # ---------------------------------------------
            self._prepare_ready_batches_safely(force=True)
            update_acceptance_check_run(
                check_id=check_id,
                checked_count=(
                    counters.checked_count
                ),
                new_accepted_count=(
                    counters
                    .new_accepted_count
                ),
                still_pending_count=(
                    counters
                    .still_pending_count
                ),
                declined_or_unknown_count=(
                    counters
                    .declined_or_unknown_count
                ),
                failed_count=(
                    counters.failed_count
                ),
                completed=True,
                client=self.client,
            )

            print("")
            print("=" * 60)
            print("ACCEPTANCE CHECK FINISHED")
            print("=" * 60)

            print(
                "Checked:",
                counters.checked_count,
            )

            print(
                "New accepted:",
                counters.new_accepted_count,
            )

            print(
                "Still pending:",
                counters.still_pending_count,
            )

            print(
                "Declined / unknown:",
                counters.declined_or_unknown_count,
            )

            print(
                "Check failed:",
                counters.failed_count,
            )

        except Exception as exc:
            error_message = (
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            print(
                (
                    "Acceptance Check failed: "
                    f"{error_message}"
                ),
                file=sys.stderr,
            )

            try:
                update_acceptance_check_run(
                    check_id=check_id,
                    checked_count=(
                        counters.checked_count
                    ),
                    new_accepted_count=(
                        counters
                        .new_accepted_count
                    ),
                    still_pending_count=(
                        counters
                        .still_pending_count
                    ),
                    declined_or_unknown_count=(
                        counters
                        .declined_or_unknown_count
                    ),
                    failed_count=(
                        counters.failed_count
                    ),
                    failed=True,
                    client=self.client,
                )

            except Exception as save_exc:
                print(
                    (
                        "Could not mark Acceptance "
                        "Check failed: "
                        f"{type(save_exc).__name__}: "
                        f"{save_exc}"
                    ),
                    file=sys.stderr,
                )

    # =====================================================
    # STOP
    # =====================================================

    def request_stop(
        self,
        signum: int | None = None,
        frame: Any = None,
    ) -> None:
        del frame

        self._stop_requested = True

        print("")

        if signum is not None:
            print(
                "Stop signal received:",
                signum,
            )

        print(
            "Acceptance worker will stop safely."
        )

    def _register_signal_handlers(
        self,
    ) -> None:
        signal.signal(
            signal.SIGINT,
            self.request_stop,
        )

        if hasattr(
            signal,
            "SIGTERM",
        ):
            signal.signal(
                signal.SIGTERM,
                self.request_stop,
            )

    # =====================================================
    # INTERRUPTIBLE WAIT
    # =====================================================

    def _sleep_interruptibly(
        self,
        seconds: float,
    ) -> None:
        remaining = max(
            0.0,
            float(seconds),
        )

        while (
            remaining > 0
            and not self._stop_requested
        ):
            step = min(
                0.5,
                remaining,
            )

            time.sleep(
                step
            )

            remaining -= step


# =========================================================
# MAIN
# =========================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="Manual and scheduled Acceptance checks")
    parser.add_argument("--schedule", action="store_true", help="Enable newest-first 00:00 / backlog 06:00 Vietnam rotation, with 20-minute batch gaps")
    parser.add_argument("--schedule-state", type=Path,
                        default=Path(__file__).resolve().parent / "output" / "acceptance-schedule.json")
    args = parser.parse_args()
    try:
        # Manual and scheduled modes share one process lock on this worker Mac.
        import fcntl
        lock_path = Path(__file__).resolve().parent / "output" / "acceptance-worker.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a+") as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RuntimeError("Another Acceptance worker is running. Stop it before starting this one.")
            worker = OutreachAcceptanceWorker(schedule_path=args.schedule_state if args.schedule else None)
            if args.schedule:
                print(f"Acceptance schedule: 00:00 daily; old-cycle backlog 06:00; newest first; batch gap 20 minutes | state={args.schedule_state}", flush=True)
            return worker.run_forever()

    except Exception as exc:
        print(
            (
                "Could not start Outreach "
                "Acceptance Worker: "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
