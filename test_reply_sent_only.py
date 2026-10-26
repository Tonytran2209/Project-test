"""Offline regression tests for sent-only Unread gating; no LinkedIn/DB access."""
import ast
from pathlib import Path
import re
from types import SimpleNamespace
import unicodedata
import unittest
from unittest.mock import MagicMock
from urllib.parse import unquote, urlparse

from app.outreach_reply_direction import (
    profile_slug_key, same_person_name, sent_target_from_own_messages,
    sent_target_from_unverified_message, verify_sent_message_events,
)


class SentOnlyReplyTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(Path('outreach_reply_check_worker.py').read_text())
        names = {'_normalize_name', '_profile_name_from_linkedin_url',
                 'sent_candidates_for_unread_thread', 'match_unread_by_profile_url'}
        nodes = [ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0)]
        nodes += [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
        self.ns = dict(re=re, unicodedata=unicodedata, urlparse=urlparse, unquote=unquote,
                       profile_slug_key=profile_slug_key, same_person_name=same_person_name,
                       sent_target_from_own_messages=sent_target_from_own_messages,
                       sent_target_from_unverified_message=sent_target_from_unverified_message,
                       verify_sent_message_events=verify_sent_message_events,
                       BETWEEN_CONVERSATIONS_MS=0, logger=MagicMock())
        for name in ['open_matched_conversation', '_active_thread_profile_key',
                     'load_full_conversation', 'mark_active_thread_as_unread']:
            self.ns[name] = MagicMock()
        self.ns['open_matched_conversation'].return_value = 'https://www.linkedin.com/messaging/thread/test/'
        self.ns['_active_thread_profile_key'].return_value = 'josh-lynch'
        self.ns['load_full_conversation'].return_value = [{'text': 'Hello', 'sender_type': 'incoming', 'is_incoming': True}]
        exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), 'sent_only_test', 'exec'), self.ns)
        self.page = MagicMock()
        self.profile = {'id': 'sent-1', 'assigned_account_id': 'outreach_account_05',
                        'status': 'sent', 'linkedin_url': 'https://www.linkedin.com/in/josh-lynch/',
                        'normalized_name': 'josh lynch', 'message_text': 'A unique outbound message long enough to match.'}

    def match(self, thread, profiles=None):
        return self.ns['match_unread_by_profile_url'](
            self.page, unread_names=[thread], sent_profiles=profiles if profiles is not None else [self.profile],
            account_id='outreach_account_05')

    def test_golden_gate_with_empty_sent_list_is_not_opened(self):
        self.assertEqual(self.match({'name': 'Golden Gate University', 'thread_url': ''}, []), [])
        self.ns['open_matched_conversation'].assert_not_called()
        self.ns['load_full_conversation'].assert_not_called()
        self.ns['mark_active_thread_as_unread'].assert_not_called()

    def test_outside_name_is_skipped_before_browser_action(self):
        self.assertEqual(self.match({'name': 'Golden Gate University', 'thread_url': ''}), [])
        self.ns['open_matched_conversation'].assert_not_called()

    def test_wrong_account_or_unsent_target_is_skipped(self):
        for change in [{'assigned_account_id': 'outreach_account_07'}, {'status': 'pending'}, {'status': 'failed'}]:
            self.assertEqual(self.match({'name': 'Josh Lynch', 'thread_url': ''}, [{**self.profile, **change}]), [])
        self.ns['open_matched_conversation'].assert_not_called()

    def test_known_member_is_read_and_linked_to_original_target(self):
        result = self.match({'name': 'Josh Lynch', 'thread_url': ''})
        self.assertEqual(result[0]['sent_profile']['id'], 'sent-1')
        self.assertEqual(result[0]['match_reason'], 'exact_thread_profile_url')
        self.ns['load_full_conversation'].assert_called_once()
        self.ns['mark_active_thread_as_unread'].assert_called_once()

    def test_row_profile_url_handles_changed_display_name(self):
        result = self.match({'name': 'Different Display Name', 'thread_url': '', 'linkedin_url': self.profile['linkedin_url']})
        self.assertEqual(len(result), 1)

    def test_explicit_unknown_row_url_overrides_same_name(self):
        self.assertEqual(self.match({'name': 'Josh Lynch', 'thread_url': '', 'linkedin_url': '/in/someone-else/'}), [])
        self.ns['open_matched_conversation'].assert_not_called()

    def test_opened_profile_mismatch_is_not_read(self):
        self.ns['_active_thread_profile_key'].return_value = 'other-josh'
        self.assertEqual(self.match({'name': 'Josh Lynch', 'thread_url': ''}), [])
        self.ns['load_full_conversation'].assert_not_called()
        self.ns['mark_active_thread_as_unread'].assert_called_once()

    def test_name_only_without_sent_identity_is_not_saved(self):
        self.ns['_active_thread_profile_key'].return_value = ''
        self.assertEqual(self.match({'name': 'Josh Lynch', 'thread_url': ''}), [])

    def test_exact_own_sent_text_can_verify_missing_profile_link(self):
        self.ns['_active_thread_profile_key'].return_value = ''
        self.ns['load_full_conversation'].return_value = [
            {'text': self.profile['message_text'], 'sender_type': 'own', 'is_own_message': True}]
        result = self.match({'name': 'Josh Lynch', 'thread_url': ''})
        self.assertEqual(result[0]['sent_profile']['id'], 'sent-1')
        self.assertEqual(result[0]['match_reason'], 'exact_own_sent_message')

    def test_eligible_thread_read_failure_still_fails_and_restores_unread(self):
        self.ns['load_full_conversation'].side_effect = RuntimeError('missing scroll container')
        with self.assertRaisesRegex(RuntimeError, 'missing scroll container'):
            self.match({'name': 'Josh Lynch', 'thread_url': ''})
        self.ns['mark_active_thread_as_unread'].assert_called_once()


if __name__ == '__main__':
    unittest.main()
