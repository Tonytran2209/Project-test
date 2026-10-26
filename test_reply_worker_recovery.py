"""DOM adapters are mocked; no live browser or database is used."""
import ast
from pathlib import Path
import re
import unicodedata
import unittest
from unittest.mock import MagicMock
from urllib.parse import unquote, urlparse

from app.outreach_reply_direction import profile_slug_key, same_person_name


def functions(*names):
    tree=ast.parse(Path('outreach_reply_check_worker.py').read_text())
    nodes=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)]
    nodes += [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    ns=dict(re=re, unicodedata=unicodedata, urlparse=urlparse, unquote=unquote,
            logger=MagicMock(), profile_slug_key=profile_slug_key, same_person_name=same_person_name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'recovery_test','exec'),ns)
    return ns


class ThreadIdentityTests(unittest.TestCase):
    def identify(self, links):
        ns=functions('_active_thread_profile_key','_normalize_name')
        anchors=[]
        for label,url in links:
            anchor=MagicMock(); anchor.inner_text.return_value=label
            anchor.get_attribute.side_effect=lambda attr, url=url: url if attr=='href' else ''
            anchors.append(anchor)
        scope=MagicMock(); scope.locator.return_value.all.return_value=anchors
        page=MagicMock(); page.locator.return_value.count.return_value=1
        page.locator.return_value.nth.return_value=scope
        ns.update(_find_unread_surface=lambda p:p,_is_visible=lambda p:True,
                  MESSAGE_SCROLL_CONTAINER_SELECTORS=())
        return ns['_active_thread_profile_key'](page,'Oleg Kurchenko')

    def test_own_and_customer_links_do_not_hide_customer_identity(self):
        self.assertEqual(self.identify([('Valerie Nguyen','/in/valerie/'),
                                        ('Oleg Kurchenko','/in/olegkurchenko/')]),'olegkurchenko')

    def test_repeated_author_links_for_same_recipient_are_not_ambiguous(self):
        self.assertEqual(self.identify([('Oleg Kurchenko','/in/oleg/'),
                                        ('Oleg Kurchenko','/in/oleg/?trk=x')]),'oleg')

    def test_same_name_different_profiles_is_not_guessed(self):
        self.assertEqual(self.identify([('Oleg Kurchenko','/in/oleg-one/'),
                                        ('Oleg Kurchenko','/in/oleg-two/')]),'')

    def test_accessible_profile_label_can_identify_recipient(self):
        self.assertEqual(self.identify([("View Oleg Kurchenko’s profile",'/in/oleg/'),
                                        ('Valerie Nguyen','/in/valerie/')]),'oleg')

    def test_only_own_author_link_is_not_mistaken_for_recipient(self):
        self.assertEqual(self.identify([('Valerie Nguyen','/in/valerie/')]),'')


class UnreadRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.ns=functions('_recover_unread_surface')
        self.page=MagicMock(); self.surface=object(); self.owner=object()
        self.ns.update(_find_unread_surface=MagicMock(),open_messaging=MagicMock(return_value=self.owner),
                       open_unread=MagicMock(),_log_unread_diagnostics=MagicMock())

    def test_transient_rerender_is_retried_without_navigation(self):
        self.ns['_find_unread_surface'].side_effect=[None,None,self.surface]
        self.assertIs(self.ns['_recover_unread_surface'](self.page),self.surface)
        self.assertEqual(self.page.wait_for_timeout.call_count,2)
        self.ns['open_messaging'].assert_not_called()

    def test_missing_filter_reopens_messaging_and_unread(self):
        self.ns['_find_unread_surface'].side_effect=[None]*8+[self.surface]
        self.assertIs(self.ns['_recover_unread_surface'](self.page),self.surface)
        self.ns['open_messaging'].assert_called_once_with(self.page)
        self.ns['open_unread'].assert_called_once_with(self.owner)

    def test_persistent_failure_is_not_reported_as_success(self):
        self.ns['_find_unread_surface'].return_value=None
        with self.assertRaisesRegex(RuntimeError,'could not be recovered'):
            self.ns['_recover_unread_surface'](self.page)

    def test_click_reacquires_surface_instead_of_using_stale_frame(self):
        ns=functions('open_matched_conversation')
        class Page: pass
        page=Page(); page.url='https://www.linkedin.com/messaging/'
        page.wait_for_timeout=MagicMock()
        thread='https://www.linkedin.com/messaging/thread/known/'
        row=MagicMock(); row.get_attribute.return_value=thread
        def click(target): page.url=thread; return True
        ns.update(Page=Page,_recover_unread_surface=MagicMock(return_value=page),
                  _find_unread_surface=MagicMock(return_value=None),
                  _scroll_unread_list_to_start=MagicMock(),
                  _find_visible_unread_row=MagicMock(return_value=row),_click_locator=click,
                  CONVERSATION_SETTLE_MS=0)
        self.assertEqual(ns['open_matched_conversation'](page,'Oleg Kurchenko',thread),thread)
        self.assertEqual(ns['_recover_unread_surface'].call_count,2)


class StoredIdentityTests(unittest.TestCase):
    def test_saved_thread_links_require_matching_profile_and_target(self):
        ns=functions('load_sent_message_profiles','_profile_name_from_linkedin_url','_normalize_name')
        sent=MagicMock(); history=MagicMock(); client=MagicMock()
        client.table.side_effect=lambda name: sent if name=='outreach_message_targets' else history
        target={'id':'t1','status':'sent','assigned_account_id':'outreach_account_01',
                'linkedin_url':'https://www.linkedin.com/in/olegkurchenko/'}
        sent.select.return_value.eq.return_value.eq.return_value.order.return_value.order.return_value.range.return_value.execute.return_value.data=[target]
        history.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data=[
            {'sent_target_id':'t1','linkedin_url':'/in/olegkurchenko/','thread_url':'https://www.linkedin.com/messaging/thread/yes/?x=1','user_name':'Oleg Kurchenko'},
            {'sent_target_id':'t1','linkedin_url':'/in/wrong-person/','thread_url':'https://www.linkedin.com/messaging/thread/no/','user_name':'Wrong Person'},
            {'sent_target_id':'unknown','linkedin_url':'/in/olegkurchenko/','thread_url':'https://www.linkedin.com/messaging/thread/no2/','user_name':'Wrong Link'}]
        profiles=ns['load_sent_message_profiles'](account_id='outreach_account_01',client=client)
        self.assertEqual(profiles[0]['verified_threads'],['https://www.linkedin.com/messaging/thread/yes'])
        self.assertEqual(profiles[0]['verified_names'],['oleg kurchenko'])
        history.select.return_value.eq.assert_called_once_with('assigned_account_id','outreach_account_01')


if __name__=='__main__': unittest.main()
