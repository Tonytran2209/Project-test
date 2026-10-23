import sys
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


class OutreachAccountsTest(unittest.TestCase):
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
