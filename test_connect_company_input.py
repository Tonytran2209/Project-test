import sys
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

from app.outreach_connect_input import prepare_connect_entries

try:
    from app import outreach_job_store as store
except ModuleNotFoundError as exc:
    if exc.name not in {"supabase", "dotenv"}:
        raise
    supabase = ModuleType("supabase")
    supabase.Client = object
    supabase.create_client = lambda *args, **kwargs: None
    settings = ModuleType("app.settings")
    settings.load_settings = lambda: None
    with patch.dict(sys.modules, {"supabase": supabase, "app.settings": settings}):
        from app import outreach_job_store as store


class ConnectCompanyInputTest(unittest.TestCase):
    def test_blank_urls_are_not_removed_when_pairing(self):
        with self.assertRaisesRegex(ValueError, "Row 2"):
            prepare_connect_entries(["url-a", "", "url-c"], ["A", "B", "C"])

    def test_mismatch_and_missing_names_are_rejected(self):
        for names in (["A"], ["A", ""], "A\nB", ["A", 2]):
            with self.subTest(names=names), self.assertRaises(ValueError):
                prepare_connect_entries(["url-a", "url-b"], names)

    def test_optional_companies_keep_existing_url_input(self):
        self.assertEqual(prepare_connect_entries([" url-a ", "", "url-b"]),
                         [("url-a", ""), ("url-b", "")])

    def test_skipped_urls_do_not_shift_companies(self):
        client = MagicMock()
        tables = {name: MagicMock() for name in (store.JOB_TABLE, store.PROSPECT_TABLE, store.TARGET_TABLE)}
        client.table.side_effect = tables.__getitem__
        tables[store.JOB_TABLE].insert.return_value.execute.return_value = SimpleNamespace(data=[{"id": "job-1"}])
        tables[store.PROSPECT_TABLE].insert.return_value.execute.return_value = SimpleNamespace(data=[{"id": "prospect-1"}])
        urls = ["invalid", "https://linkedin.com/in/a", "https://www.linkedin.com/in/a/", "https://linkedin.com/in/old", "https://linkedin.com/in/b"]
        names = ["Invalid Co", "Company A", "Duplicate Co", "Existing Co", "Company B"]
        with patch.object(store, "_build_job_code", return_value="code"), patch.object(
            store, "_find_existing_prospect", side_effect=lambda **kw: {"id": "old"} if kw["normalized_url"].endswith("/old") else None
        ):
            result = store.create_connect_job(urls, company_names=names, client=client)
        inserts = tables[store.PROSPECT_TABLE].insert.call_args_list
        self.assertEqual([call.args[0]["company_name"] for call in inserts], ["Company A", "Company B"])
        self.assertEqual([call.args[0]["normalized_url"] for call in inserts], ["https://www.linkedin.com/in/a", "https://www.linkedin.com/in/b"])
        self.assertEqual((result.target_count, result.duplicate_count, result.invalid_count), (2, 2, 1))

    def test_bad_counts_fail_before_any_database_write(self):
        client = MagicMock()
        with self.assertRaises(store.OutreachJobStoreError):
            store.create_connect_job(["url-a", "url-b"], company_names=["A"], client=client)
        client.table.assert_not_called()

    def test_unavailable_column_fails_before_job_creation(self):
        client = MagicMock()
        client.table.return_value.select.return_value.limit.return_value.execute.side_effect = RuntimeError("column missing")
        with self.assertRaisesRegex(store.OutreachJobStoreError, "company-name storage"):
            store.create_connect_job(["https://linkedin.com/in/a"], company_names=["A"], client=client)
        client.table.return_value.insert.assert_not_called()


if __name__ == "__main__":
    unittest.main()
