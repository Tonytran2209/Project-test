"""Offline preparation tests; no browser, Supabase or message sending."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
import sys
from unittest.mock import MagicMock, patch

from test_message_preparation_sources import store  # dependency-safe import
with patch.dict(sys.modules, {'app.outreach_message_preparation_store': store}):
    from app import outreach_ready_batches as ready


class AutoReadyTests(unittest.TestCase):
    def setUp(self):
        self.candidates = [dict(prospect_id='p1', source_target_id='t1', connect_batch_id='s1',
                                campaign_id='video', assigned_account_id='outreach_account_06',
                                linkedin_url='https://linkedin.com/in/person/', normalized_url='')]
        self.rows = [dict(id='t1', ready_first_name='Frank', auto_message_dismissed=False)]
        self.client = MagicMock()
        self.client.table.return_value.select.return_value.in_.return_value.execute.side_effect = lambda: SimpleNamespace(data=self.rows)
        self.client.rpc.return_value.execute.return_value.data = {'created':True,'batch_id':'b1'}
        self.patches = [patch.object(ready, 'get_message_preparation_candidates', side_effect=lambda **kw: {'items':self.candidates}),
                        patch.object(ready, 'get_campaign_message_template_for_batch', return_value={'message_template':'Hello {first_name} at {company}'}),
                        patch.object(ready, 'attach_target_companies', side_effect=lambda targets, **kw: targets[0].update(company_name='Studio'))]
        self.mocks = [p.start() for p in self.patches]
        self.addCleanup(lambda: [p.stop() for p in self.patches])

    def test_renders_company_and_name_and_never_queues(self):
        result = ready.prepare_accepted_ready_batches(client=self.client)
        self.assertEqual(len(result['batches']), 1)
        name, payload = self.client.rpc.call_args.args
        self.assertEqual(name, 'prepare_outreach_ready_batch')
        self.assertEqual(payload['p_targets'][0]['message_text'], 'Hello Frank at Studio')
        self.assertEqual(payload['p_targets'][0]['assigned_account_id'], 'outreach_account_06')
        self.assertEqual(payload['p_source_id'], 's1')

    def test_groups_by_original_connect_batch(self):
        self.candidates.append(dict(self.candidates[0], prospect_id='p2', source_target_id='t2',connect_batch_id='s2'))
        self.rows.append(dict(id='t2',ready_first_name='Phoebe'))
        ready.prepare_accepted_ready_batches(client=self.client)
        self.assertEqual([c.args[1]['p_source_id'] for c in self.client.rpc.call_args_list], ['s1','s2'])
        self.assertEqual(self.mocks[1].call_count, 1)

    def test_missing_template_still_creates_sendable_recipient_snapshot(self):
        self.mocks[1].return_value = {'message_template':''}
        self.assertEqual(ready.prepare_accepted_ready_batches(client=self.client)['skipped'], 0)
        self.assertEqual(self.client.rpc.call_args.args[1]['p_template'], '')

    def test_missing_company_does_not_block_snapshot(self):
        self.mocks[2].side_effect = lambda targets, **kw: targets[0].update(company_name='')
        self.assertEqual(ready.prepare_accepted_ready_batches(client=self.client)['skipped'], 0)
        self.assertIsNone(self.client.rpc.call_args.args[1]['p_targets'][0]['message_text'])

    def test_missing_name_is_read_by_sender_not_a_preparation_blocker(self):
        self.rows[0]['ready_first_name'] = ''
        ready.prepare_accepted_ready_batches(client=self.client)
        self.assertIsNone(self.client.rpc.call_args.args[1]['p_targets'][0]['first_name'])

    def test_deleted_batch_is_not_automatically_recreated(self):
        self.rows[0]['auto_message_dismissed'] = True
        ready.prepare_accepted_ready_batches(client=self.client)
        self.client.rpc.assert_not_called()

    def test_rpc_retry_does_not_report_duplicate_as_created(self):
        self.client.rpc.return_value.execute.return_value.data = {'created':False}
        self.assertEqual(ready.prepare_accepted_ready_batches(client=self.client)['batches'], [])

    def test_company_not_required_when_template_has_no_company(self):
        self.mocks[1].return_value = {'message_template':'Hi {first_name}'}
        ready.prepare_accepted_ready_batches(client=self.client)
        self.mocks[2].assert_not_called()

    def test_invalid_template_keeps_snapshot_for_user_review_before_queue(self):
        self.mocks[1].return_value = {'message_template':'Hi {unknown}'}
        ready.prepare_accepted_ready_batches(client=self.client)
        self.assertIsNone(self.client.rpc.call_args.args[1]['p_targets'][0]['message_text'])

    def test_delete_validates_and_deduplicates_ids(self):
        batch_id = '00000000-0000-0000-0000-000000000001'
        ready.delete_ready_message_batches([batch_id,batch_id], client=self.client)
        self.client.rpc.assert_called_once_with('delete_outreach_ready_batches', {'p_batch_ids':[batch_id]})
        self.client.reset_mock()
        with self.assertRaises(ValueError): ready.delete_ready_message_batches(['bad'], client=self.client)
        with self.assertRaises(ValueError): ready.delete_ready_message_batches([], client=self.client)
        self.client.rpc.assert_not_called()

    def test_acceptance_worker_includes_idle_retry_and_post_scan_preparation(self):
        source = Path('outreach_acceptance_worker.py').read_text()
        ast.parse(source)
        self.assertIn('self._prepare_ready_batches_safely(force=True)', source)
        self.assertIn(".update({'ready_first_name': name})", source)
        self.assertIn('self._prepare_ready_batches_safely()', source)

    def test_sql_transaction_protects_drafts_and_keeps_source_history(self):
        sql = Path('outreach_ready_batches.sql').read_text()
        self.assertIn("b.status = 'prepared'", sql)
        self.assertIn("t.status <> 'prepared'", sql)
        self.assertIn('for update', sql)
        self.assertIn('auto_message_dismissed = true', sql)
        self.assertIn('pg_advisory_xact_lock', sql)
        self.assertIn('on delete cascade', sql)
        self.assertNotIn('delete from public.outreach_jobs', sql)
        self.assertNotIn('delete from public.outreach_job_targets', sql)
        self.assertIn('from public, anon, authenticated', sql)


if __name__ == '__main__': unittest.main()
