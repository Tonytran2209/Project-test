import unittest
import sys
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
