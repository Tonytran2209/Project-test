import json
import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from app.lab_monitoring import build_report, job_history, JOB_SOURCES

NOW = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows

    def select(self, *_):
        return self

    def order(self, *_, **__):
        return self

    def limit(self, *_):
        return self

    def execute(self):
        if isinstance(self.rows, Exception):
            raise self.rows
        return type("R", (), {"data": self.rows})()


class FakeClient:
    def __init__(self, tables):
        self.tables = tables

    def table(self, name):
        return FakeQuery(self.tables.get(name, []))


TABLES = {
    "outreach_jobs": [
        {"status": "completed", "started_at": "2026-11-07T10:00:00Z", "completed_at": "2026-11-07T10:20:00Z",
         "processed_count": 20, "success_count": 15, "display_name": "Secret campaign"},
        {"status": "failed", "started_at": "2026-11-06T09:00:00Z", "completed_at": "2026-11-06T09:01:00Z",
         "last_error": "Playwright navigation timeout"},
        {"status": "completed", "started_at": "2026-10-01T09:00:00Z", "completed_at": "2026-10-01T09:30:00Z",
         "processed_count": 5, "success_count": 5},
        {"status": "running", "started_at": "2026-11-07T11:00:00Z"},
    ],
    "outreach_acceptance_checks": [
        {"status": "failed", "started_at": "2026-11-07T08:00:00Z", "completed_at": "2026-11-07T08:02:00Z",
         "last_error": "No accepted invitations matched"},
    ],
    "outreach_message_batches": [
        {"status": "completed", "started_at": "2026-11-07T11:00:00Z", "completed_at": "2026-11-07T11:05:00Z",
         "sent_count": 0, "failed_count": 3},
    ],
    "outreach_reply_send_jobs": [
        {"status": "sent", "started_at": "2026-11-07T11:30:00Z", "sent_at": "2026-11-07T11:31:00Z",
         "user_name": "Private Person"},
    ],
    "outreach_account_sessions": [
        {"status": "logged_in", "display_name": "acc-1"},
        {"status": "checkpoint", "display_name": "acc-2"},
    ],
}


class LabMonitoringTest(unittest.TestCase):
    def report(self, tables=TABLES, days=7):
        workers = lambda: {"tasks": [{"key": "connect", "label": "Connect", "count": 1, "details": ["JOB-1"]}]}
        return build_report(FakeClient(tables), days, worker_activity=workers, now=lambda: NOW)

    def test_report_matches_lab_protocol_and_window(self):
        report = self.report()
        self.assertEqual(report["protocol"], "app-monitoring-v1")
        self.assertEqual(report["appId"], "outreach")
        self.assertEqual(report["window"]["days"], 7)
        self.assertEqual(report["database"]["status"], "ready")
        self.assertEqual(report["profile"]["version"], "profile-v1")

    def test_job_history_balances_and_classifies_failures(self):
        period = self.report()["jobHistory"]
        self.assertEqual(period["executed"], 5)
        self.assertEqual(period["failed"], 2)
        self.assertEqual(period["technicalErrors"], 1, "Playwright timeout is technical")
        self.assertEqual(period["unclassifiedFailures"], 1, "no-match result is not called technical")
        self.assertEqual(period["validCompletions"], 2)
        self.assertEqual(period["unverifiedCompletions"], 1, "a batch that sent nothing is not a verified success")
        self.assertEqual(period["failed"] + period["validCompletions"] + period["unverifiedCompletions"], period["executed"])
        self.assertEqual(period["latestJob"], {"job": "Reply send", "durationMs": 60000,
                                               "completedAt": "2026-11-07T11:31:00+00:00"})
        self.assertEqual(self.report()["jobHistoryAllTime"]["executed"], 6)

    def test_report_carries_no_personal_text(self):
        text = json.dumps(self.report(), ensure_ascii=False)
        for secret in ("Secret campaign", "Private Person", "acc-1", "JOB-1"):
            self.assertNotIn(secret, text)

    def test_profile_sections_describe_outreach(self):
        profile = self.report()["profile"]
        funnel = {m["label"]: m["value"] for m in profile["sections"][0]["metrics"]}
        self.assertEqual(funnel["Lời mời connect đã gửi"], 15)
        self.assertEqual(funnel["Tỷ lệ gửi connect thành công"], 75.0)
        self.assertEqual(funnel["Tin nhắn lỗi"], 3)
        accounts = {m["label"]: m["value"] for m in profile["sections"][2]["metrics"]}
        self.assertEqual(accounts["Cần xử lý (đăng xuất / checkpoint / lỗi)"], 1)
        self.assertEqual(profile["sections"][3]["table"]["rows"], [["Connect", 1]])

    def test_unreachable_table_is_unknown_not_zero(self):
        tables = dict(TABLES, outreach_message_batches=RuntimeError("relation missing"))
        report = self.report(tables)
        self.assertEqual(report["database"]["status"], "degraded")
        self.assertFalse(report["jobHistory"]["complete"])
        self.assertIsNone(report["inventory"]["outreach_message_batches"])
        funnel = {m["label"]: m["value"] for m in report["profile"]["sections"][0]["metrics"]}
        self.assertIsNone(funnel["Tin nhắn đã gửi"])

    def test_job_targets_come_from_environment_for_known_jobs_only(self):
        with patch.dict(os.environ, {"LAB_JOB_TARGETS_MINUTES": '{"Connect batch": 30, "Other": 5, "Reply send": -1}'}):
            self.assertEqual(self.report()["profile"]["jobTargets"], {"Connect batch": 30})
        with patch.dict(os.environ, {"LAB_JOB_TARGETS_MINUTES": "not json"}):
            self.assertEqual(self.report()["profile"]["jobTargets"], {})

    def test_every_source_is_listed_once(self):
        self.assertEqual(len({s.key for s in JOB_SOURCES}), len(JOB_SOURCES))
        self.assertEqual(job_history({}, None, set())["complete"], False)


if __name__ == "__main__":
    unittest.main()
