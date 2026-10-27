"""Offline tests: never start browsers, send invitations or access Supabase."""
import ast
from datetime import date, datetime, timezone, timedelta
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from app.outreach_acceptance_schedule import AcceptanceSchedule, VIETNAM, cycle_weeks


def clock(day, hour=0, minute=0):
    return datetime.fromisoformat(day).replace(hour=hour, minute=minute, tzinfo=VIETNAM)


class ZeroDurationSchedule(AcceptanceSchedule):
    """Keep simulated runs on their injected date, not the machine's real clock."""
    def tick(self, now):
        with patch('app.outreach_acceptance_schedule.datetime', wraps=datetime) as frozen:
            frozen.now.return_value = now
            return super().tick(now)


class AcceptanceScheduleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "schedule.json"
        self.calls = []
        self.scheduler = ZeroDurationSchedule(self.path, self.scan)

    def scan(self, week, checkpoint):
        self.calls.append((week["start"], week["end"]))
        week["progress"]["saved"] = True
        checkpoint()
        return True

    def test_partial_week_and_upper_boundary(self):
        weeks = cycle_weeks(date(2026, 10, 26))
        self.assertEqual(weeks[0]["start"], "2026-10-26")
        self.assertEqual(weeks[0]["end"], "2026-11-02")
        self.assertEqual(weeks[-1], {"start":"2026-09-01", "end":"2026-09-07", "progress":{}})
        self.assertEqual(len(weeks), 9)
        self.assertTrue(all(w["start"] < w["end"] for w in weeks))

    def test_year_boundary_and_leap_month(self):
        self.assertEqual(cycle_weeks(date(2027, 1, 4))[-1]["start"], "2026-12-01")
        self.assertEqual(cycle_weeks(date(2028, 3, 6))[-1]["start"], "2028-02-01")
        self.assertEqual(cycle_weeks(date(2028, 3, 6))[0]["end"], "2028-03-13")

    def test_daily_one_week_and_no_duplicate_slot(self):
        self.assertTrue(self.scheduler.tick(clock("2026-10-26")))
        self.assertFalse(self.scheduler.tick(clock("2026-10-26", minute=2)))
        self.scheduler.tick(clock("2026-10-27"))
        self.assertEqual(self.calls, [("2026-10-26", "2026-11-02"), ("2026-10-19", "2026-10-26")])

    def test_monday_main_reset_and_independent_backlog(self):
        for day in range(26, 32):
            self.scheduler.tick(clock(f"2026-10-{day}"))
        self.scheduler.tick(clock("2026-11-01"))
        old = self.scheduler.state["cycles"]["2026-10-26"]
        self.assertEqual(old["cursor"], 7)
        self.scheduler.tick(clock("2026-11-02"))
        new = self.scheduler.state["cycles"]["2026-11-02"]
        self.assertEqual(new["weeks"][0]["start"], "2026-11-02")
        self.assertEqual(new["cursor"], 1)
        self.scheduler.tick(clock("2026-11-02", 6))
        self.assertEqual(self.calls[-1], ("2026-09-07", "2026-09-14"))
        self.assertEqual(old["cursor"], 8)
        self.assertEqual(new["cursor"], 1)
        self.assertTrue(self.scheduler.tick(clock("2026-11-03", 6)))
        self.assertEqual(self.calls[-1], ("2026-09-01", "2026-09-07"))
        self.assertFalse(self.scheduler.tick(clock("2026-11-04", 6)))

    def test_backlog_continues_tuesday_and_wednesday(self):
        self.scheduler.tick(clock("2026-10-26"))
        for day in ("2026-11-02", "2026-11-03", "2026-11-04"):
            before = self.scheduler.state["cycles"]["2026-10-26"]["cursor"]
            self.assertTrue(self.scheduler.tick(clock(day, 6)))
            self.assertEqual(self.scheduler.state["cycles"]["2026-10-26"]["cursor"], before+1)

    def test_no_catchup_before_seven_days(self):
        self.scheduler.tick(clock("2026-10-26"))
        self.assertFalse(self.scheduler.tick(clock("2026-10-27", 6)))

    def test_restart_preserves_cursor_and_slot(self):
        self.scheduler.tick(clock("2026-10-26"))
        restored = ZeroDurationSchedule(self.path, self.scan)
        self.assertFalse(restored.tick(clock("2026-10-26", minute=3)))
        restored.tick(clock("2026-10-27"))
        self.assertEqual(self.calls[-1][0], "2026-10-19")

    def test_interrupted_week_resumes_even_outside_slot(self):
        def crash(week, checkpoint):
            week["progress"]["batch"] = "already-saved"
            checkpoint()
            raise RuntimeError("power loss")
        self.scheduler.scan_week = crash
        with self.assertRaises(RuntimeError):
            self.scheduler.tick(clock("2026-10-26"))
        resumed = ZeroDurationSchedule(self.path, self.scan)
        self.assertTrue(resumed.tick(clock("2026-10-26", 11)))
        self.assertEqual(resumed.state["cycles"]["2026-10-26"]["cursor"], 1)

    def test_failed_week_not_advanced_or_repeated_same_slot(self):
        self.scheduler.scan_week = lambda *args: False
        self.scheduler.tick(clock("2026-10-26"))
        self.assertEqual(self.scheduler.state["cycles"]["2026-10-26"]["cursor"], 0)
        self.assertFalse(self.scheduler.tick(clock("2026-10-26", minute=1)))

    def test_offline_slots_are_not_replayed(self):
        self.assertFalse(self.scheduler.tick(clock("2026-10-26", 9)))
        self.assertEqual(self.calls, [])

    def test_vietnam_timezone_and_naive_rejection(self):
        self.assertTrue(self.scheduler.tick(datetime(2026, 10, 25, 17, tzinfo=timezone.utc)))
        with self.assertRaises(ValueError):
            self.scheduler.tick(datetime(2026, 10, 26))

    def test_corrupt_state_is_not_silently_reset(self):
        self.path.write_text('{"version": 99}')
        with self.assertRaises(ValueError):
            AcceptanceSchedule(self.path, self.scan)

    def test_slot_crossed_while_busy_runs_late_once(self):
        self.scheduler.tick(clock("2026-10-26"))
        self.scheduler.defer_busy_slots(clock("2026-11-02", 5), clock("2026-11-02", 8))
        resumed = ZeroDurationSchedule(self.path, self.scan)
        self.assertTrue(resumed.tick(clock("2026-11-02", 8)))
        self.assertEqual(resumed.state["cycles"]["2026-10-26"]["cursor"], 2)
        self.assertFalse(resumed.tick(clock("2026-11-02", 8)))

    def test_empty_week_still_only_advances_one_week(self):
        self.scheduler.scan_week = lambda week, checkpoint: True
        self.scheduler.tick(clock("2026-10-26"))
        self.assertEqual(self.scheduler.state["cycles"]["2026-10-26"]["cursor"], 1)

    def test_cooldown_keeps_week_active_and_resumes_after_restart_outside_slot(self):
        def cooling(week, checkpoint):
            week['progress']['next_batch_at'] = clock('2026-10-26', minute=20).isoformat()
            checkpoint()
            return None
        self.scheduler.scan_week = MagicMock(side_effect=cooling)
        self.assertFalse(self.scheduler.tick(clock('2026-10-26')))
        self.assertIsNotNone(self.scheduler.state['active'])
        restored = ZeroDurationSchedule(self.path, self.scan)
        self.assertFalse(restored.tick(clock('2026-10-26', minute=19)))
        self.assertEqual(self.calls, [])
        self.assertTrue(restored.tick(clock('2026-10-26', minute=20)))
        self.assertEqual(restored.state['cycles']['2026-10-26']['cursor'], 1)

    def test_v1_migration_backs_up_and_reverses_only_unfinished_weeks(self):
        old_weeks = list(reversed(cycle_weeks(date(2026,10,26))))[:-1]
        old_weeks[0]['progress'] = {'done':['saved-batch']}
        original = {'version':1,'cycles':{'2026-10-26':{'cursor':1,'weeks':old_weeks}},
                    'slots':['2026-10-26T00:00'],'active':None}
        self.path.write_text(json.dumps(original))
        restored = ZeroDurationSchedule(self.path, self.scan)
        cycle = restored.state['cycles']['2026-10-26']
        self.assertEqual(restored.state['version'], 2)
        self.assertEqual(cycle['weeks'][0]['progress']['done'], ['saved-batch'])
        self.assertEqual(cycle['weeks'][cycle['cursor']]['start'], '2026-10-26')
        backup = self.path.with_name(self.path.name+'.v1-backup')
        self.assertEqual(json.loads(backup.read_text())['version'], 1)
        self.assertEqual(restored.state['slots'], original['slots'])

    def test_v1_inflight_batch_is_preserved_before_newest_first_rotation(self):
        old_weeks = list(reversed(cycle_weeks(date(2026,10,26))))[:-1]
        old_weeks[1]['progress'] = {'run':{'id':'inflight','job_id':'old-batch'},'done':[]}
        self.path.write_text(json.dumps({'version':1,'cycles':{'2026-10-26':{'cursor':1,'weeks':old_weeks}},
            'slots':[], 'active':{'cycle':'2026-10-26','slot':'2026-10-27T00:00'}}))
        restored = ZeroDurationSchedule(self.path, self.scan)
        cycle = restored.state['cycles']['2026-10-26']
        self.assertEqual(cycle['weeks'][1]['progress']['run']['id'], 'inflight')
        self.assertEqual(cycle['weeks'][2]['start'], '2026-10-26')


def runner_namespace():
    source = Path(__file__).with_name("app").joinpath("outreach_acceptance_recheck.py").read_text()
    tree = ast.parse(source)
    nodes = [ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)]
    nodes += [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    ns = {"datetime": datetime, "timedelta": timedelta, "BATCH_GAP_SECONDS":1200, "VIETNAM": VIETNAM,
          "JOB_TABLE": "outreach_jobs", "ACCEPTANCE_CHECK_TABLE": "outreach_acceptance_checks"}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), "test_runner", "exec"), ns)
    return ns


class ScheduledBatchTests(unittest.TestCase):
    def setUp(self):
        self.ns = runner_namespace()
        self.client = MagicMock()
        self.worker = SimpleNamespace(client=self.client, _stop_requested=False, _process_check_run=MagicMock())
        self.week = {"start": "2026-09-01", "end": "2026-09-07", "progress": {"jobs": ["original-batch"], "done": [], "run": None}}
        self.checkpoint = MagicMock()
        self.ns["load_acceptance_targets"] = MagicMock(return_value=[{"target_id": "old-target"}])
        self.ns["create_acceptance_check_run"] = MagicMock(return_value={"id": "run-1", "source_job_id": "original-batch"})
        # Shared fluent client: existing-run query and result query are independent chains.
        self.client.table.return_value.select.return_value.eq.return_value.in_.return_value.limit.return_value.execute.return_value.data = []
        self.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"status": "completed", "failed_count": 0}]

    def test_original_batch_and_existing_checker_used(self):
        self.assertTrue(self.ns["scan_connect_week"](self.worker, self.week, self.checkpoint))
        self.ns["create_acceptance_check_run"].assert_called_once_with(
            source_job_id="original-batch", total_to_check=1, status="running", client=self.client)
        self.worker._process_check_run.assert_called_once()
        self.assertEqual(self.week["progress"]["done"], ["original-batch"])

    def test_twenty_minutes_from_completion_and_persisted_resume(self):
        frozen = MagicMock(wraps=datetime)
        self.ns['datetime'] = frozen
        frozen.now.return_value = clock('2026-10-26')
        self.week['progress']['jobs'].append('second-batch')
        def finish(run):
            frozen.now.return_value = clock('2026-10-26', minute=5)
        self.worker._process_check_run.side_effect = finish
        self.assertIsNone(self.ns['scan_connect_week'](self.worker, self.week, self.checkpoint))
        self.assertEqual(self.week['progress']['next_batch_at'], clock('2026-10-26', minute=25).isoformat())
        self.assertEqual(self.week['progress']['done'], ['original-batch'])
        # Recreate the runner and restore only serialized progress, like a restart.
        restored = runner_namespace()
        for key in ('load_acceptance_targets', 'create_acceptance_check_run'):
            restored[key] = self.ns[key]
        restored['datetime'] = frozen
        week = json.loads(json.dumps(self.week))
        frozen.now.return_value = clock('2026-10-26', minute=24)
        self.assertIsNone(restored['scan_connect_week'](self.worker, week, self.checkpoint))
        self.assertEqual(self.worker._process_check_run.call_count, 1)
        frozen.now.return_value = clock('2026-10-26', minute=25)
        self.worker._process_check_run.side_effect = None
        self.assertTrue(restored['scan_connect_week'](self.worker, week, self.checkpoint))
        self.assertEqual(self.worker._process_check_run.call_count, 2)
        self.assertEqual(week['progress']['done'], ['original-batch', 'second-batch'])

    def test_exception_saves_cooldown_before_retry(self):
        frozen = MagicMock(wraps=datetime)
        self.ns['datetime'] = frozen
        frozen.now.return_value = clock('2026-10-26', minute=7)
        self.worker._process_check_run.side_effect = RuntimeError('browser closed')
        with self.assertRaises(RuntimeError):
            self.ns['scan_connect_week'](self.worker, self.week, self.checkpoint)
        self.assertEqual(self.week['progress']['next_batch_at'], clock('2026-10-26', minute=27).isoformat())
        self.assertEqual(self.week['progress']['done'], [])
        frozen.now.return_value = clock('2026-10-26', minute=26)
        self.assertIsNone(self.ns['scan_connect_week'](self.worker, self.week, self.checkpoint))
        self.assertEqual(self.worker._process_check_run.call_count, 1)

    def test_no_pending_targets_does_not_open_browser(self):
        self.ns["load_acceptance_targets"].return_value = []
        self.assertTrue(self.ns["scan_connect_week"](self.worker, self.week, self.checkpoint))
        self.worker._process_check_run.assert_not_called()

    def test_existing_manual_run_is_deferred(self):
        self.client.table.return_value.select.return_value.eq.return_value.in_.return_value.limit.return_value.execute.return_value.data = [{"id": "manual"}]
        self.assertFalse(self.ns["scan_connect_week"](self.worker, self.week, self.checkpoint))
        self.ns["create_acceptance_check_run"].assert_not_called()

    def test_failed_batch_retains_progress(self):
        self.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"status": "completed", "failed_count": 1}]
        self.assertFalse(self.ns["scan_connect_week"](self.worker, self.week, self.checkpoint))
        self.assertEqual(self.week["progress"]["done"], [])

    def test_resume_completed_batch_does_not_check_again(self):
        self.week["progress"]["run"] = {"id": "run-1", "job_id": "original-batch"}
        self.assertTrue(self.ns["scan_connect_week"](self.worker, self.week, self.checkpoint))
        self.worker._process_check_run.assert_not_called()

    def test_completed_batches_are_not_repeated_on_retry(self):
        self.week["progress"]["done"] = ["original-batch"]
        self.assertTrue(self.ns["scan_connect_week"](self.worker, self.week, self.checkpoint))
        self.ns["load_acceptance_targets"].assert_not_called()

    def test_jobs_are_paginated_using_original_connect_dates(self):
        self.week["progress"] = {}
        query = self.client.table.return_value.select.return_value
        pages = query.gte.return_value.lt.return_value.order.return_value.order.return_value.range.return_value.execute
        pages.side_effect = [SimpleNamespace(data=[{"id": str(i)} for i in range(500)]), SimpleNamespace(data=[{"id": "last"}])]
        self.ns["load_acceptance_targets"].return_value = []
        self.assertTrue(self.ns["scan_connect_week"](self.worker, self.week, self.checkpoint))
        self.assertEqual(len(self.week["progress"]["done"]), 501)
        self.assertEqual(query.gte.call_count, 2)
        query.gte.assert_called_with("created_at", "2026-09-01T00:00:00+07:00")
        query.gte.return_value.lt.assert_called_with("created_at", "2026-09-07T00:00:00+07:00")

    def test_interrupted_run_is_closed_before_retry(self):
        self.week["progress"]["run"] = {"id": "old-run", "job_id": "original-batch"}
        self.client.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            SimpleNamespace(data=[{"status": "running"}]),
            SimpleNamespace(data=[{"status": "completed", "failed_count": 0}]),
        ]
        self.assertTrue(self.ns["scan_connect_week"](self.worker, self.week, self.checkpoint))
        self.client.table.return_value.update.assert_called_once_with({"status": "failed"})


if __name__ == "__main__":
    unittest.main()
