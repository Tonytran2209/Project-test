import unittest
import sys
from types import SimpleNamespace
from types import ModuleType
from unittest.mock import patch
from app import outreach_campaign_identity as campaign


try:
    from app import outreach_message_preparation_store as store
except ModuleNotFoundError as exc:
    if exc.name != "supabase":
        raise
    # Exercise grouping logic even on a machine without service dependencies.
    supabase = ModuleType("supabase")
    supabase.Client = object
    supabase.create_client = lambda *args, **kwargs: None
    accepted_pool = ModuleType("app.outreach_accepted_pool_store")
    accepted_pool.get_accepted_pool = lambda **kwargs: None
    settings = ModuleType("app.settings")
    settings.load_settings = lambda: None
    with patch.dict(sys.modules, {
        "supabase": supabase,
        "app.outreach_accepted_pool_store": accepted_pool,
        "app.outreach_campaign_identity": campaign,
        "app.settings": settings,
    }):
        from app import outreach_message_preparation_store as store


class MessagePreparationSourcesTest(unittest.TestCase):
    def test_snapshot_companies_follow_prospect_identity_not_query_order(self):
        rows = {
            store.MESSAGE_BATCH_TABLE: [{'id':'message', 'batch_code':'October'}],
            store.MESSAGE_TARGET_TABLE: [
                {'id':'m1','prospect_id':'p1','source_target_id':'t1','linkedin_url':'https://linkedin.com/in/alice'},
                {'id':'m2','prospect_id':'p2','source_target_id':'t2','linkedin_url':'https://linkedin.com/in/bob'}],
            'outreach_prospects': [
                {'id':'p2','linkedin_url':'https://linkedin.com/in/bob','company_name':'Company B'},
                {'id':'p1','linkedin_url':'https://linkedin.com/in/alice','company_name':'Company A'}],
            store.CONNECT_TARGET_TABLE: [{'id':'t1','job_id':'connect'},{'id':'t2','job_id':'connect'}],
            store.CONNECT_JOB_TABLE: [{'id':'connect','created_at':'2026-10-23T08:00:00Z','display_name':'Video'}],
        }
        class Query:
            def __init__(self, name): self.name = name
            def __getattr__(self, name): return lambda *args, **kwargs: self
            def execute(self): return SimpleNamespace(data=rows[self.name])
        result = store.get_prepared_message_batch('message', client=SimpleNamespace(table=lambda name: Query(name)))
        self.assertEqual([target['company_name'] for target in result['targets']], ['Company A','Company B'])
        self.assertEqual(result['targets'][0]['connect_created_at'], '2026-10-23T08:00:00Z')

    def test_message_batch_exposes_original_connect_date_without_rewriting_prepare_date(self):
        rows = {
            store.MESSAGE_TARGET_TABLE: [{'batch_id':'message','source_target_id':'target'}],
            store.CONNECT_TARGET_TABLE: [{'id':'target','job_id':'connect'}],
            store.CONNECT_JOB_TABLE: [{'id':'connect','created_at':'2026-09-03T08:00:00Z',
                                       'display_name':'Video','batch_name':'September'}],
        }
        class Query:
            def __init__(self, name): self.name = name
            def __getattr__(self, name): return lambda *args, **kwargs: self
            def execute(self): return SimpleNamespace(data=rows[self.name])
        client = SimpleNamespace(table=lambda name: Query(name))
        result = store._attach_source_connect_ids_to_batches(client=client,
            batches=[{'id':'message','created_at':'2026-10-27T08:00:00Z'}])
        self.assertEqual(result[0]['source_connect_ids'][0]['created_at'], '2026-09-03T08:00:00Z')
        self.assertEqual(result[0]['created_at'], '2026-10-27T08:00:00Z')

    def test_preparation_splits_by_connect_batch(self):
        candidates = [
            {"connect_batch_id": "source-a", "campaign_id": "campaign-1", "prospect_id": "p1"},
            {"connect_batch_id": "source-b", "campaign_id": "campaign-2", "prospect_id": "p2"},
            {"connect_batch_id": "source-a", "campaign_id": "campaign-1", "prospect_id": "p3"},
        ]

        def create(*, candidates, client):
            return {"batch": {"id": candidates[0]["connect_batch_id"]},
                    "target_count": len(candidates)}

        with patch.object(store, "_create_prepared_batch_from_candidates", side_effect=create) as mocked:
            result = store._prepare_batches_by_connect_source(candidates=candidates, client=None)

        self.assertEqual([batch["id"] for batch in result["batches"]], ["source-a", "source-b"])
        self.assertEqual(result["target_count"], 3)
        self.assertEqual([len(call.kwargs["candidates"]) for call in mocked.call_args_list], [2, 1])

    def test_missing_source_is_rejected_before_writes(self):
        with patch.object(store, "_create_prepared_batch_from_candidates") as mocked:
            with self.assertRaises(store.OutreachMessagePreparationStoreError):
                store._prepare_batches_by_connect_source(
                    candidates=[{"connect_batch_id": "source-a"}, {"connect_batch_id": ""}],
                    client=None,
                )
        mocked.assert_not_called()


if __name__ == "__main__":
    unittest.main()
