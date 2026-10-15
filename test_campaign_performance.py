import sys
import unittest
from types import ModuleType
from unittest.mock import patch

from app.outreach_campaign_identity import (
    canonical_campaign_name, campaign_id_for_name, connect_batch_label,
    connect_batch_name,
)

VERIFIED_CONVERSATION = [
    {"sender_type": "own", "text": "Hello, reaching out about your creative work."},
    {"sender_type": "incoming", "text": "Thanks for reaching out!"},
]


try:
    from app.outreach_campaign_performance_store import aggregate_campaign_performance
except ModuleNotFoundError as exc:
    if exc.name != "supabase":
        raise
    supabase = ModuleType("supabase")
    supabase.Client = object
    dashboard = ModuleType("app.outreach_dashboard_store")
    dashboard.get_outreach_client = lambda: None
    with patch.dict(sys.modules, {"supabase": supabase, "app.outreach_dashboard_store": dashboard}):
        from app.outreach_campaign_performance_store import aggregate_campaign_performance


class CampaignPerformanceTest(unittest.TestCase):
    def test_legacy_date_and_run_labels_share_campaign_identity(self):
        first = "29/9/2026 - Video Production Agency"
        later = "28/9/2026 - lần 3- Video Production Agency"
        self.assertEqual(canonical_campaign_name(later), "Video Production Agency")
        self.assertEqual(campaign_id_for_name(first), campaign_id_for_name(later))
        self.assertEqual(canonical_campaign_name("MKT mana"), "MKT mana")

    def test_legacy_batches_use_local_run_date_without_changing_campaign(self):
        created_at = "2026-10-14T18:30:00Z"
        self.assertEqual(connect_batch_name(None, created_at), "15/10/2026")
        self.assertEqual(
            connect_batch_label(None, "14/10/2026 - Video Production Agency", created_at),
            "15/10/2026 - Video Production Agency",
        )
        self.assertEqual(
            connect_batch_label("Agency outreach", "Video Production Agency", created_at),
            "Agency outreach - Video Production Agency",
        )

    def test_same_campaign_aggregates_batches_without_duplicate_replies(self):
        jobs = [
            {"id": "b1", "job_code": "B-01", "display_name": "29/9/2026 - Video Agency", "created_at": "2026-10-06T10:00:00Z"},
            {"id": "b2", "job_code": "B-02", "display_name": "28/9/2026 - lần 3- video  agency ", "created_at": "2026-10-05T10:00:00Z"},
            {"id": "b3", "job_code": "B-03", "display_name": "Other", "created_at": "2026-10-04T10:00:00Z"},
        ]
        targets = [
            {"id": "t1", "job_id": "b1", "prospect_id": "p1", "assigned_account_id": "account-1"},
            {"id": "t2", "job_id": "b2", "prospect_id": "p2", "assigned_account_id": "account-2"},
            {"id": "t3", "job_id": "b3", "prospect_id": "p3", "assigned_account_id": "account-1"},
        ]
        sent = [
            {"id": "m1", "source_target_id": "t1", "assigned_account_id": "account-1", "linkedin_url": "https://linkedin.com/in/person-one/"},
            {"id": "m2", "source_target_id": "t2", "assigned_account_id": "account-2", "linkedin_url": "https://linkedin.com/in/person-two/"},
            {"id": "m3", "source_target_id": "t3", "assigned_account_id": "account-1", "linkedin_url": "https://linkedin.com/in/person-three/"},
        ]
        replies = [
            {"sent_target_id": "m1", "assigned_account_id": "account-1", "linkedin_url": "https://www.linkedin.com/in/person-one/?trk=feed", "conversation_messages": VERIFIED_CONVERSATION, "created_at": "2026-10-12T00:00:00+07:00"},
            {"sent_target_id": "m1", "assigned_account_id": "account-1", "linkedin_url": "https://linkedin.com/in/person-one", "conversation_messages": VERIFIED_CONVERSATION, "created_at": "2026-10-13T00:00:00+07:00"},
            {"sent_target_id": "m3", "assigned_account_id": "account-1", "linkedin_url": "https://linkedin.com/in/person-three", "conversation_messages": VERIFIED_CONVERSATION, "created_at": "2026-10-12T00:00:00+07:00"},
        ]
        campaigns = aggregate_campaign_performance(jobs, targets, sent, replies)
        video = next(row for row in campaigns if row["campaign_name"] == "Video Agency")
        other = next(row for row in campaigns if row["campaign_name"] == "Other")
        self.assertEqual(video["batch_ids"], ["B-01", "B-02"])
        self.assertEqual((video["added"], video["messaged"], video["replies"]), (2, 2, 1))
        self.assertEqual(video["reply_rate"], 50.0)
        self.assertEqual([(row["account_id"], row["messaged"], row["replies"])
                          for row in video["accounts"]], [("account-1", 1, 1), ("account-2", 1, 0)])
        self.assertEqual((other["added"], other["messaged"], other["replies"]), (1, 1, 1))

    def test_old_reply_stays_excluded_after_rescan_and_accounts_follow_sender(self):
        jobs = [{"id": "b1", "job_code": "B-01", "display_name": "Video Agency",
                 "created_at": "2026-10-06T10:00:00Z"}]
        targets = [{"id": "t1", "job_id": "b1", "prospect_id": "p1",
                    "assigned_account_id": "account-1"}]
        sent = [{"id": "m1", "source_target_id": "t1", "assigned_account_id": "account-2", "linkedin_url": "https://linkedin.com/in/person-one"}]
        replies = [{"sent_target_id": "m1", "created_at": "2026-10-11T16:59:59Z",
                    "captured_at": "2026-10-20T10:00:00Z", "assigned_account_id": "account-2",
                    "linkedin_url": "https://linkedin.com/in/person-one", "conversation_messages": VERIFIED_CONVERSATION}]
        campaign = aggregate_campaign_performance(jobs, targets, sent, replies)[0]
        self.assertEqual((campaign["added"], campaign["messaged"], campaign["replies"]), (1, 1, 0))
        accounts = {row["account_id"]: row for row in campaign["accounts"]}
        self.assertEqual((accounts["account-1"]["added"], accounts["account-1"]["messaged"]), (1, 0))
        self.assertEqual((accounts["account-2"]["added"], accounts["account-2"]["messaged"]), (0, 1))

    def test_url_only_reply_resolves_batch_but_own_only_and_wrong_url_do_not(self):
        jobs = [
            {"id": "b1", "job_code": "B-01", "display_name": "Video", "created_at": "2026-10-10T10:00:00Z"},
            {"id": "b2", "job_code": "B-02", "display_name": "Marketing", "created_at": "2026-10-10T09:00:00Z"},
        ]
        targets = [
            {"id": "t1", "job_id": "b1", "prospect_id": "p1", "assigned_account_id": "account-1"},
            {"id": "t2", "job_id": "b2", "prospect_id": "p2", "assigned_account_id": "account-1"},
        ]
        sent = [
            {"id": "m1", "source_target_id": "t1", "assigned_account_id": "account-1", "linkedin_url": "https://linkedin.com/in/alpha"},
            {"id": "m2", "source_target_id": "t2", "assigned_account_id": "account-1", "linkedin_url": "https://linkedin.com/in/beta"},
        ]
        replies = [
            {"sent_target_id": None, "assigned_account_id": "account-1", "linkedin_url": "https://www.linkedin.com/in/alpha/?trk=abc", "conversation_messages": VERIFIED_CONVERSATION, "created_at": "2026-10-13T00:00:00Z"},
            {"sent_target_id": "m2", "assigned_account_id": "account-1", "linkedin_url": "https://linkedin.com/in/alpha", "conversation_messages": VERIFIED_CONVERSATION, "created_at": "2026-10-13T00:00:00Z"},
            {"sent_target_id": "m2", "assigned_account_id": "account-1", "linkedin_url": "https://linkedin.com/in/beta", "conversation_messages": [{"sender_type": "own", "text": "Just checking in"}], "created_at": "2026-10-13T00:00:00Z"},
            {"sent_target_id": "m2", "assigned_account_id": "account-1", "linkedin_url": "https://linkedin.com/in/beta", "conversation_messages": [{"sender_type": "incoming", "text": "A message without verified send context"}], "created_at": "2026-10-13T00:00:00Z"},
        ]
        campaigns = {row["campaign_name"]: row for row in aggregate_campaign_performance(jobs, targets, sent, replies)}
        self.assertEqual(campaigns["Video"]["replies"], 1)
        self.assertEqual(campaigns["Marketing"]["replies"], 0)

    def test_ambiguous_profile_across_batches_is_not_guessed(self):
        jobs = [
            {"id": "b1", "job_code": "B-01", "display_name": "Video", "created_at": "2026-10-10T10:00:00Z"},
            {"id": "b2", "job_code": "B-02", "display_name": "Marketing", "created_at": "2026-10-10T09:00:00Z"},
        ]
        targets = [
            {"id": "t1", "job_id": "b1", "prospect_id": "p1", "assigned_account_id": "account-1"},
            {"id": "t2", "job_id": "b2", "prospect_id": "p1", "assigned_account_id": "account-1"},
        ]
        sent = [
            {"id": "m1", "source_target_id": "t1", "assigned_account_id": "account-1", "linkedin_url": "https://linkedin.com/in/alpha", "message_text": "Message unique to the video batch."},
            {"id": "m2", "source_target_id": "t2", "assigned_account_id": "account-1", "linkedin_url": "https://linkedin.com/in/alpha", "message_text": "Message unique to the marketing batch."},
        ]
        reply = {"sent_target_id": "m2", "assigned_account_id": "account-1", "linkedin_url": "https://linkedin.com/in/alpha", "conversation_messages": VERIFIED_CONVERSATION, "created_at": "2026-10-13T00:00:00Z"}
        campaigns = {row["campaign_name"]: row for row in aggregate_campaign_performance(jobs, targets, sent, [reply])}
        self.assertEqual((campaigns["Video"]["replies"], campaigns["Marketing"]["replies"]), (0, 0))
        reply["conversation_messages"] = [
            {"sender_type": "own", "text": "Message unique to the marketing batch."},
            {"sender_type": "incoming", "text": "Thank you!"},
        ]
        campaigns = {row["campaign_name"]: row for row in aggregate_campaign_performance(jobs, targets, sent, [reply])}
        self.assertEqual((campaigns["Video"]["replies"], campaigns["Marketing"]["replies"]), (0, 1))


if __name__ == "__main__":
    unittest.main()
