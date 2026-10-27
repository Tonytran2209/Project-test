"""Persistent weekly Acceptance rotation; all calendar boundaries use Vietnam time."""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

VIETNAM = ZoneInfo("Asia/Ho_Chi_Minh")


# @layer business
# @feature acceptance
def cycle_weeks(monday: date) -> list[dict]:
    """Current week first, then backwards to the previous month's first day."""
    month_start = monday.replace(day=1)
    start = (month_start - timedelta(days=1)).replace(day=1)
    weeks = []
    upper = monday + timedelta(days=7)
    while start < upper:
        end = min(start + timedelta(days=7 - start.weekday()), upper)
        weeks.append({"start": start.isoformat(), "end": end.isoformat(), "progress": {}})
        start = end
    return list(reversed(weeks))


class AcceptanceSchedule:
    """One main week at midnight; one old-cycle week at 06:00 after seven days.

    State is checkpointed before work and after each batch by scan_week.
    A single Acceptance worker owns the file (enforced by its process lock).
    Missed slots are skipped, but interrupted weeks resume after restart.
    """

    def __init__(self, path: Path, scan_week):
        self.path = path
        self.scan_week = scan_week
        self.state = json.loads(path.read_text()) if path.exists() else {
            "version": 2, "cycles": {}, "slots": [], "active": None,
        }
        if self.state.get("version") not in (1, 2):
            raise ValueError("Unsupported Acceptance schedule state; do not overwrite it.")
        self.state.setdefault("pending_slots", [])
        if self.state['version'] == 1:
            # Preserve an untouched backup and completed batch checkpoints.
            backup = path.with_name(path.name + '.v1-backup')
            if not backup.exists():
                with backup.open('x') as stream:
                    json.dump(self.state, stream, ensure_ascii=False, indent=2)
            for key, cycle in self.state['cycles'].items():
                done = cycle['weeks'][:cycle['cursor']]
                remaining = cycle['weeks'][cycle['cursor']:]
                inflight = remaining[0] if remaining and (self.state.get('active') or {}).get('cycle') == key else None
                known = {(week['start'], week['end']) for week in cycle['weeks']}
                remaining += [week for week in cycle_weeks(date.fromisoformat(key))
                              if (week['start'], week['end']) not in known]
                remaining.sort(key=lambda week: week['start'], reverse=True)
                if inflight is not None:
                    remaining.remove(inflight)
                    remaining.insert(0, inflight)
                cycle['weeks'] = done + remaining
                cycle['cursor'] = len(done)
            self.state['version'] = 2
            self.save()

    def defer_busy_slots(self, start: datetime, end: datetime):
        """Queue slots crossed while this live process was busy, not while offline."""
        start, end = start.astimezone(VIETNAM), end.astimezone(VIETNAM)
        day = start.date()
        while day <= end.date():
            for hour in (0, 6):
                slot_at = datetime(day.year, day.month, day.day, hour, tzinfo=VIETNAM)
                slot = f"{day.isoformat()}T{hour:02}:00"
                if start < slot_at <= end and slot not in self.state["slots"]:
                    self.state["slots"].append(slot)
                    self.state["pending_slots"].append(slot)
            day += timedelta(days=1)
        self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        with temporary.open("w") as stream:
            json.dump(self.state, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(self.path)

    def tick(self, now: datetime) -> bool:
        if now.tzinfo is None:
            raise ValueError("Schedule clock must be timezone-aware")
        local = now.astimezone(VIETNAM)
        monday = local.date() - timedelta(days=local.weekday())
        key = monday.isoformat()
        cycles = self.state["cycles"]
        if key not in cycles:
            cycles[key] = {"cursor": 0, "weeks": cycle_weeks(monday)}
            self.save()

        # Record the current slot before servicing older deferred work.
        if local.hour in (0, 6) and local.minute < 15:
            current_slot = f"{local.date().isoformat()}T{local.hour:02}:00"
            if current_slot not in self.state["slots"]:
                self.state["slots"] = (self.state["slots"] + [current_slot])[-120:]
                self.state["pending_slots"].append(current_slot)
                self.save()

        active = self.state["active"]
        if active is None:
            if not self.state["pending_slots"]:
                return False
            slot = self.state["pending_slots"].pop(0)
            local = datetime.fromisoformat(slot).replace(tzinfo=VIETNAM)
            monday = local.date() - timedelta(days=local.weekday())
            key = monday.isoformat()
            if key not in cycles:
                cycles[key] = {"cursor": 0, "weeks": cycle_weeks(monday)}
            selected = key
            if local.hour == 6:
                selected = next((candidate for candidate in sorted(cycles)
                                 if candidate < key
                                 and (local.date() - date.fromisoformat(candidate)).days >= 7
                                 and cycles[candidate]["cursor"] < len(cycles[candidate]["weeks"])), None)
            if selected is None or cycles[selected]["cursor"] >= len(cycles[selected]["weeks"]):
                self.save()
                return False
            active = {"cycle": selected, "slot": slot}
            self.state["active"] = active
            self.save()

        cycle = cycles[active["cycle"]]
        week = cycle["weeks"][cycle["cursor"]]
        next_batch_at = week.get('progress', {}).get('next_batch_at')
        if next_batch_at and now.astimezone(VIETNAM) < datetime.fromisoformat(next_batch_at):
            return False
        print(f"ACCEPTANCE SCHEDULE | slot={active['slot']} | cycle={active['cycle']} "
              f"| connect_week={week['start']}..{week['end']}", flush=True)
        # Exceptions leave active intact: never silently skip an interrupted week.
        started = now
        try:
            complete = self.scan_week(week, self.save)
        finally:
            self.defer_busy_slots(started, datetime.now(VIETNAM))
        if complete is None:
            # The scheduled week is cooling down between batches. Keep active
            # so the same week resumes outside the 00:00/06:00 start window.
            self.save()
            return False
        if complete:
            cycle["cursor"] += 1
        self.state["active"] = None
        self.save()
        return True
