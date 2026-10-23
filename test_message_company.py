import unittest
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

from app.linkedin_message_template import build_message, template_uses_company
from app.outreach_message_company import attach_target_companies, company_for_target

try:
    from app import outreach_message_queue_store as queue_store
except ModuleNotFoundError as exc:
    if exc.name not in {"supabase", "dotenv"}:
        raise
    supabase = ModuleType("supabase")
    supabase.Client = object
    supabase.create_client = lambda *args, **kwargs: None
    settings = ModuleType("app.settings")
    settings.load_settings = lambda: None
    with patch.dict(sys.modules, {"supabase": supabase, "app.settings": settings}):
        from app import outreach_message_queue_store as queue_store


class MessageCompanyTest(unittest.TestCase):
    def test_renders_both_fields_without_interpreting_company_braces(self):
        self.assertEqual(build_message("Alice", "Hi {first_name}, how is {company}?", company="A {Studio} & Co"),
                         "Hi Alice, how is A {Studio} & Co?")

    def test_missing_company_only_blocks_templates_that_use_it(self):
        self.assertEqual(build_message("Alice", "Hi {first_name}"), "Hi Alice")
        self.assertEqual(build_message("Alice", "Literal {{company}}"), "Literal {company}")
        with self.assertRaisesRegex(ValueError, "no saved company"):
            build_message("Alice", "Hi {first_name} at {company}")
        self.assertTrue(template_uses_company("Hi {company!s}"))
        self.assertFalse(template_uses_company("{{company}}"))

    def test_unsupported_fields_still_fail(self):
        with self.assertRaisesRegex(ValueError, "Unsupported template variable"):
            build_message("Alice", "{other}", company="Company")

    def test_companies_match_prospect_identity_not_query_order(self):
        client = MagicMock()
        client.table.return_value.select.return_value.in_.return_value.execute.return_value = SimpleNamespace(data=[
            {"id": "b", "normalized_url": "https://linkedin.com/in/b", "company_name": "Company B"},
            {"id": "a", "linkedin_url": "https://www.linkedin.com/in/a/?trk=profile", "company_name": "Company A"},
        ])
        targets = [{"prospect_id": "a", "linkedin_url": "https://linkedin.com/in/a"},
                   {"prospect_id": "b", "linkedin_url": "https://linkedin.com/in/b"}]
        attach_target_companies(targets, client=client)
        self.assertEqual([target["company_name"] for target in targets], ["Company A", "Company B"])

    def test_mismatched_url_cannot_use_another_prospects_company(self):
        client = MagicMock()
        client.table.return_value.select.return_value.in_.return_value.execute.return_value = SimpleNamespace(data=[
            {"id": "a", "linkedin_url": "https://linkedin.com/in/other", "company_name": "Wrong Company"},
        ])
        with self.assertRaisesRegex(ValueError, "Cannot match company"):
            company_for_target({"prospect_id": "a", "linkedin_url": "https://linkedin.com/in/a"}, client=client)

    def test_old_prospect_without_company_resolves_empty(self):
        client = MagicMock()
        client.table.return_value.select.return_value.in_.return_value.execute.return_value = SimpleNamespace(data=[
            {"id": "a", "linkedin_url": "https://linkedin.com/in/a", "company_name": None},
        ])
        self.assertEqual(company_for_target({"prospect_id": "a", "linkedin_url": "https://linkedin.com/in/a"}, client=client), "")

    def test_stale_normalized_url_cannot_override_actual_send_url(self):
        client = MagicMock()
        client.table.return_value.select.return_value.in_.return_value.execute.return_value = SimpleNamespace(data=[
            {"id": "a", "linkedin_url": "https://linkedin.com/in/a", "company_name": "Company A"},
        ])
        with self.assertRaisesRegex(ValueError, "Cannot match company"):
            company_for_target({"prospect_id": "a", "linkedin_url": "https://linkedin.com/in/b", "normalized_url": "https://linkedin.com/in/a"}, client=client)

    def test_queue_rejects_missing_company_before_any_status_update(self):
        client = MagicMock()
        tables = {}
        for name, rows in {
            "outreach_message_batches": [{"id": "batch", "status": "prepared"}],
            "outreach_message_targets": [{"id": "target", "prospect_id": "a", "linkedin_url": "https://linkedin.com/in/a"}],
            "outreach_prospects": [{"id": "a", "linkedin_url": "https://linkedin.com/in/a", "company_name": None}],
        }.items():
            query = MagicMock()
            for method in ("select", "eq", "limit", "in_"):
                getattr(query, method).return_value = query
            query.execute.return_value = SimpleNamespace(data=rows)
            tables[name] = query
        client.table.side_effect = tables.__getitem__
        with self.assertRaisesRegex(queue_store.OutreachMessageQueueStoreError, "no saved company name"):
            queue_store.queue_message_batch(batch_id="batch", message_template="Hi {first_name} at {company}", client=client)
        for table in tables.values():
            table.update.assert_not_called()

    def test_queue_allows_company_template_when_identity_matches(self):
        client = MagicMock()
        tables = {}
        for name, rows in {
            "outreach_message_batches": [{"id": "batch", "status": "prepared", "batch_code": "MSG-1"}],
            "outreach_message_targets": [{"id": "target", "prospect_id": "a", "linkedin_url": "https://linkedin.com/in/a"}],
            "outreach_prospects": [{"id": "a", "linkedin_url": "https://linkedin.com/in/a", "company_name": "Company A"}],
        }.items():
            query = MagicMock()
            for method in ("select", "eq", "limit", "in_", "update"):
                getattr(query, method).return_value = query
            query.execute.return_value = SimpleNamespace(data=rows)
            tables[name] = query
        client.table.side_effect = tables.__getitem__
        queue_store.queue_message_batch(batch_id="batch", message_template="Hi {first_name} at {company}", client=client)
        tables["outreach_message_batches"].update.assert_called_once()
        self.assertEqual(tables["outreach_message_batches"].update.call_args.args[0]["status"], "queued")


if __name__ == "__main__":
    unittest.main()
