import sys
import os
import importlib.util
from pathlib import Path
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

try:
    from app import outreach_reply_store as replies
    from app import outreach_dashboard_store as dashboard
except ModuleNotFoundError as exc:
    if exc.name not in {"supabase", "playwright", "dotenv"}:
        raise
    supabase = ModuleType("supabase")
    supabase.Client = object
    supabase.create_client = lambda *args, **kwargs: None
    settings = ModuleType("app.settings")
    settings.Settings = object
    settings.load_settings = lambda: None
    browser = ModuleType("app.linkedin_browser")
    browser.LinkedInBrowserManager = object
    browser.LinkedInBrowserSettings = object
    with patch.dict(sys.modules, {"supabase": supabase, "app.settings": settings, "app.linkedin_browser": browser}):
        from app import outreach_reply_store as replies
        from app import outreach_dashboard_store as dashboard

from app import outreach_account_pool as pool


class OutreachAccountsTest(unittest.TestCase):
    def test_legacy_environment_expands_to_seven_accounts(self):
        old_ids = ",".join(f"outreach_account_{number:02d}" for number in range(1, 6))
        with patch.dict(os.environ, {"OUTREACH_ACCOUNT_IDS": old_ids}):
            configured = pool._read_outreach_account_ids()
        self.assertEqual(configured, pool.DEFAULT_OUTREACH_ACCOUNT_IDS)

    def test_partial_six_account_upgrade_includes_seventh(self):
        old_ids = ",".join(f"outreach_account_{number:02d}" for number in range(1, 7))
        with patch.dict(os.environ, {"OUTREACH_ACCOUNT_IDS": old_ids}):
            self.assertEqual(pool._read_outreach_account_ids(), pool.DEFAULT_OUTREACH_ACCOUNT_IDS)

    def test_check_all_sessions_queues_all_seven_with_legacy_configuration(self):
        supabase = ModuleType("supabase")
        supabase.Client = object
        supabase.create_client = MagicMock()
        settings = ModuleType("app.settings")
        settings.load_settings = MagicMock()
        spec = importlib.util.spec_from_file_location(
            "session_status_under_test", Path(__file__).parent / "app" / "outreach_session_status.py"
        )
        sessions = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"supabase": supabase, "app.settings": settings, "app.outreach_account_pool": pool}):
            spec.loader.exec_module(sessions)
        client = MagicMock()
        def upsert(payload, **kwargs):
            return SimpleNamespace(execute=lambda: SimpleNamespace(data=payload))
        client.table.return_value.upsert.side_effect = upsert
        old_ids = ",".join(f"outreach_account_{number:02d}" for number in range(1, 6))
        with patch.dict(os.environ, {"OUTREACH_ACCOUNT_IDS": old_ids}):
            queued = sessions.queue_outreach_session_checks(client=client)
        self.assertEqual([row["account_id"] for row in queued], list(pool.DEFAULT_OUTREACH_ACCOUNT_IDS))
        self.assertTrue(all(row["status"] == "pending" for row in queued))
        payload = client.table.return_value.upsert.call_args.args[0]
        self.assertEqual([row["display_name"] for row in payload[-2:]], ["Frank Nguyen", "Phoebe"])

    def test_custom_subset_is_preserved(self):
        with patch.dict(os.environ, {"OUTREACH_ACCOUNT_IDS": "outreach_account_07,outreach_account_06"}):
            self.assertEqual(pool._read_outreach_account_ids(), ("outreach_account_07", "outreach_account_06"))

    def test_round_robin_and_worker_lookup_include_new_accounts(self):
        settings = pool.OutreachAccountPoolSettings(
            profile_root=Path("/tmp/outreach-test-profiles"),
            account_ids=pool.DEFAULT_OUTREACH_ACCOUNT_IDS,
            profiles_per_account_turn=10,
        )
        accounts = pool.OutreachAccountPool(settings=settings)
        self.assertEqual([accounts.get_next_account().account_id for _ in range(8)],
                         list(pool.DEFAULT_OUTREACH_ACCOUNT_IDS) + ["outreach_account_01"])
        self.assertEqual(accounts.get_account("outreach_account_06").display_name, "Frank Nguyen")
        self.assertEqual(accounts.get_account("outreach_account_07").display_name, "Phoebe")
        self.assertNotEqual(accounts.get_account("outreach_account_06").profile_directory,
                            accounts.get_account("outreach_account_07").profile_directory)

    def test_reply_metadata_includes_new_accounts_without_database_activity(self):
        accounts = replies.list_outreach_reply_accounts()
        self.assertEqual(len(accounts), 7)
        self.assertEqual(accounts[-2:], [
            {"account_id": "outreach_account_06", "display_name": "Frank Nguyen"},
            {"account_id": "outreach_account_07", "display_name": "Phoebe"},
        ])

    def test_new_accounts_can_load_their_reply_pages(self):
        query = MagicMock()
        for method in ("select", "eq", "order", "range"):
            getattr(query, method).return_value = query
        query.execute.return_value = SimpleNamespace(data=[])
        client = SimpleNamespace(table=lambda name: query)
        for account_id in ("outreach_account_06", "outreach_account_07"):
            page = replies.list_outreach_reply_page(account_id=account_id, client=client)
            self.assertEqual(page["replies"], [])
            self.assertFalse(page["has_more"])

    def test_dashboard_adds_new_accounts_and_preserves_existing_statuses(self):
        client = MagicMock()
        client.table.return_value.select.return_value.order.return_value.execute.return_value = SimpleNamespace(data=[
            {"account_id": "outreach_account_01", "status": "disabled", "profile_directory": "existing"},
        ])
        accounts = dashboard.get_raw_accounts(client=client)
        self.assertEqual(len(accounts), 7)
        self.assertEqual(accounts[0]["status"], "disabled")
        self.assertEqual(accounts[-1]["account_id"], "outreach_account_07")
        self.assertEqual(accounts[-1]["status"], "unknown")
        client.table.return_value.insert.assert_not_called()


if __name__ == "__main__":
    unittest.main()
