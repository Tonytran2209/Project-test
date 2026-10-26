"""URL-only reply matching; offline tests, never opens LinkedIn or sends messages."""
import ast
from pathlib import Path
import re
import unicodedata
import unittest
from unittest.mock import MagicMock

from app.outreach_reply_identity import match_sent_profile_url, canonical_member_url
from app.outreach_reply_direction import profile_slug_key, verify_sent_message_events


class SentOnlyReplyTests(unittest.TestCase):
    def setUp(self):
        tree=ast.parse(Path('outreach_reply_check_worker.py').read_text())
        nodes=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)]
        nodes += [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in
                  {'_normalize_name','match_unread_by_profile_url'}]
        self.ns=dict(re=re,unicodedata=unicodedata,logger=MagicMock(),
                     match_sent_profile_url=match_sent_profile_url,profile_slug_key=profile_slug_key,
                     verify_sent_message_events=verify_sent_message_events,BETWEEN_CONVERSATIONS_MS=0)
        for name in ['open_matched_conversation','_active_thread_profile_url','load_full_conversation',
                     'mark_active_thread_as_unread','_resolve_profile_redirect']:
            self.ns[name]=MagicMock()
        self.ns['open_matched_conversation'].return_value='https://www.linkedin.com/messaging/thread/test/'
        self.ns['_active_thread_profile_url'].return_value='https://www.linkedin.com/in/josh-lynch/'
        self.ns['_resolve_profile_redirect'].side_effect=lambda page,url:url
        self.ns['load_full_conversation'].return_value=[{'text':'New reply','sender_type':'incoming','is_incoming':True}]
        self.ns['_messaging_surfaces']=lambda page:[page]
        exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'url_matching_test','exec'),self.ns)
        self.page=MagicMock()
        self.profile={'id':'sent-1','assigned_account_id':'outreach_account_05','status':'sent',
                      'linkedin_url':'https://www.linkedin.com/in/josh-lynch/','message_text':'Original outreach text.'}

    def match(self, name='Josh Lynch', profiles=None, **fields):
        return self.ns['match_unread_by_profile_url'](self.page,
            unread_names=[{'name':name,'thread_url':'',**fields}],
            sent_profiles=profiles if profiles is not None else [self.profile],account_id='outreach_account_05')

    def test_empty_sent_list_never_opens_golden_gate(self):
        self.assertEqual(self.match('Golden Gate University',profiles=[]),[])
        self.ns['open_matched_conversation'].assert_not_called()

    def test_company_chat_is_inspected_for_url_but_history_is_not_read(self):
        self.ns['_active_thread_profile_url'].return_value='https://www.linkedin.com/company/golden-gate/'
        self.assertEqual(self.match('Golden Gate University'),[])
        self.ns['load_full_conversation'].assert_not_called()
        self.ns['_resolve_profile_redirect'].assert_not_called()
        self.ns['mark_active_thread_as_unread'].assert_called_once()

    def test_wrong_account_and_unsent_targets_are_not_checked(self):
        for change in [{'assigned_account_id':'outreach_account_07'},{'status':'pending'},{'status':'failed'}]:
            self.assertEqual(self.match(profiles=[{**self.profile,**change}]),[])
        self.ns['open_matched_conversation'].assert_not_called()

    def test_stan_abbreviated_name_does_not_gate_matching(self):
        result=self.match('Stan M.')
        self.assertEqual(result[0]['sent_profile']['id'],'sent-1')
        self.assertEqual(result[0]['match_reason'],'verified_member_url')
        self.ns['_resolve_profile_redirect'].assert_not_called()

    def test_display_name_completely_different_does_not_change_url_identity(self):
        self.assertEqual(self.match('Different Name')[0]['sent_profile']['id'],'sent-1')

    def test_outside_member_is_not_read_even_when_name_matches(self):
        self.ns['_active_thread_profile_url'].return_value='https://www.linkedin.com/in/other-person/'
        self.assertEqual(self.match(),[])
        self.ns['load_full_conversation'].assert_not_called()

    def test_header_identity_is_not_overridden_by_a_stale_row_url(self):
        self.ns['_active_thread_profile_url'].return_value='https://www.linkedin.com/in/other-person/'
        self.assertEqual(self.match(linkedin_url=self.profile['linkedin_url']),[])
        self.ns['load_full_conversation'].assert_not_called()

    def test_unknown_url_is_an_error_not_a_silent_skip(self):
        self.ns['_active_thread_profile_url'].return_value=''
        with self.assertRaisesRegex(RuntimeError,'URL unresolved'):
            self.match()
        self.ns['load_full_conversation'].assert_not_called()

    def test_missing_url_cannot_be_verified_by_identical_message_text(self):
        self.ns['_active_thread_profile_url'].return_value=''
        self.ns['load_full_conversation'].return_value=[{'text':self.profile['message_text'],'is_own_message':True}]
        with self.assertRaisesRegex(RuntimeError,'URL unresolved'):
            self.match()

    def test_verified_saved_thread_remains_available(self):
        self.profile['verified_threads']=['https://www.linkedin.com/messaging/thread/test']
        self.ns['_active_thread_profile_url'].return_value=''
        self.assertEqual(self.match('Stan M.')[0]['sent_profile']['id'],'sent-1')

    def test_row_url_fallback_requires_exact_opened_thread(self):
        self.ns['_active_thread_profile_url'].return_value=''
        result=self.match(thread_url='https://www.linkedin.com/messaging/thread/test/',linkedin_url=self.profile['linkedin_url'])
        self.assertEqual(result[0]['sent_profile']['id'],'sent-1')
        with self.assertRaisesRegex(RuntimeError,'URL unresolved'):
            self.match(thread_url='https://www.linkedin.com/messaging/thread/wrong/',linkedin_url=self.profile['linkedin_url'])

    def test_redirect_keeps_original_target_and_url(self):
        self.ns['_active_thread_profile_url'].return_value='https://www.linkedin.com/in/ACoJosh/'
        self.ns['_resolve_profile_redirect'].side_effect=lambda page,url:'https://www.linkedin.com/in/josh-lynch/'
        result=self.match()
        self.assertEqual(result[0]['sent_profile']['id'],'sent-1')
        self.assertEqual(result[0]['linkedin_url'],self.profile['linkedin_url'])

    def test_failed_redirect_preserves_snapshot_instead_of_skipping(self):
        self.ns['_active_thread_profile_url'].return_value='https://www.linkedin.com/in/new-josh/'
        self.ns['_resolve_profile_redirect'].side_effect=RuntimeError('HTTP 429')
        with self.assertRaisesRegex(RuntimeError,'429'):
            self.match()
        self.ns['load_full_conversation'].assert_not_called()

    def test_read_and_unread_restore_use_actual_conversation_page(self):
        owner=MagicMock(); owner.url='https://www.linkedin.com/messaging/thread/test/?filter=unread'
        self.ns['_messaging_surfaces']=lambda page:[page,owner]
        self.match()
        self.assertIs(self.ns['load_full_conversation'].call_args.args[0],owner)
        self.assertIs(self.ns['mark_active_thread_as_unread'].call_args.args[0],owner)

    def test_history_error_remains_a_failure(self):
        self.ns['load_full_conversation'].side_effect=RuntimeError('missing scroll container')
        with self.assertRaisesRegex(RuntimeError,'missing scroll container'):
            self.match()
        self.ns['mark_active_thread_as_unread'].assert_called_once()


class CanonicalUrlTests(unittest.TestCase):
    def test_url_normalization_and_direct_matching_need_no_requests(self):
        profiles=[{'id':'t','status':'sent','assigned_account_id':'a','linkedin_url':'https://linkedin.com/in/oleg/'}]
        resolve=MagicMock()
        self.assertEqual(match_sent_profile_url('https://www.linkedin.com/in/OLEG/?trk=x',profiles,'a',resolve,{})[0]['id'],'t')
        resolve.assert_not_called()

    def test_aliases_are_cached_within_the_scan(self):
        profiles=[{'id':'t','status':'sent','assigned_account_id':'a','linkedin_url':'https://linkedin.com/in/current/'}]
        resolve=MagicMock(return_value='https://linkedin.com/in/current/'); cache={}
        for _ in range(2):
            self.assertEqual(match_sent_profile_url('https://linkedin.com/in/ACoObserved/',profiles,'a',resolve,cache)[0]['id'],'t')
        resolve.assert_called_once_with('https://linkedin.com/in/ACoObserved/')

    def test_unmatched_recipient_never_resolves_sent_list(self):
        profiles=[{'id':str(i),'status':'sent','assigned_account_id':'a',
                   'linkedin_url':f'https://linkedin.com/in/stored-{i}/'} for i in range(150)]
        resolve=MagicMock(return_value='https://linkedin.com/in/outsider/')
        self.assertEqual(match_sent_profile_url('https://linkedin.com/in/ACoObserved/',profiles,'a',resolve,{}),[])
        resolve.assert_called_once_with('https://linkedin.com/in/ACoObserved/')

    def test_matching_recipient_never_resolves_other_stored_profiles(self):
        profiles=[{'id':str(i),'status':'sent','assigned_account_id':'a',
                   'linkedin_url':f'https://linkedin.com/in/stored-{i}/'} for i in range(150)]
        resolve=MagicMock(return_value='https://linkedin.com/in/stored-149/')
        self.assertEqual(match_sent_profile_url('https://linkedin.com/in/ACoObserved/',profiles,'a',resolve,{})[0]['id'],'149')
        resolve.assert_called_once_with('https://linkedin.com/in/ACoObserved/')

    def test_html_canonical_handles_unchanged_url_bar(self):
        self.assertEqual(canonical_member_url('https://linkedin.com/in/old/',
            '<link href="/in/current/" rel="canonical">'),'https://linkedin.com/in/current/')

    def test_login_or_external_canonical_does_not_prove_identity(self):
        with self.assertRaises(RuntimeError): canonical_member_url('https://linkedin.com/login','')
        with self.assertRaises(RuntimeError):
            canonical_member_url('https://linkedin.com/in/oleg/',
                                 '<link rel="canonical" href="https://evil.test/in/other/">')


if __name__=='__main__': unittest.main()
