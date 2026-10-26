"""Offline tests: no LinkedIn requests, browser sessions or DB writes."""
import unittest
from unittest.mock import MagicMock

from test_reply_worker_recovery import functions


class ProfileResolutionTests(unittest.TestCase):
    def setUp(self):
        self.ns = functions('_resolve_profile_redirect', '_resolve_profile_in_browser')
        self.page = MagicMock()
        self.url = 'https://www.linkedin.com/in/ACoCaseSensitive/'
        self.resolved = 'https://www.linkedin.com/in/stan-example/'
        self.request_response = self.page.context.request.get.return_value
        self.request_response.ok = True
        self.request_response.url = self.resolved
        self.request_response.text.return_value = ''
        self.browser = self.page.context.new_page.return_value
        self.browser.url = self.resolved
        self.browser.goto.return_value.ok = True
        self.browser.locator.return_value.inner_html.return_value = ''

    def test_successful_request_does_not_open_tab(self):
        self.assertEqual(self.ns['_resolve_profile_redirect'](self.page, self.url), self.resolved)
        self.page.context.new_page.assert_not_called()
        self.request_response.dispose.assert_called_once()

    def test_reset_falls_back_and_keeps_original_case(self):
        self.page.context.request.get.side_effect = RuntimeError('ECONNRESET cookie=SECRET')
        self.assertEqual(self.ns['_resolve_profile_redirect'](self.page, self.url), self.resolved)
        self.assertEqual(self.browser.goto.call_args.args[0], self.url)
        self.browser.close.assert_called_once()
        self.page.goto.assert_not_called()
        self.assertNotIn('SECRET', str(self.ns['logger'].mock_calls))

    def test_blocked_http_uses_browser(self):
        self.request_response.ok = False
        self.assertEqual(self.ns['_resolve_profile_redirect'](self.page, self.url), self.resolved)
        self.request_response.dispose.assert_called_once()

    def test_browser_uses_canonical_when_address_bar_keeps_opaque_id(self):
        self.browser.url = self.url
        self.browser.locator.return_value.inner_html.return_value = (
            '<link rel="canonical" href="' + self.resolved + '">')
        self.assertEqual(self.ns['_resolve_profile_in_browser'](self.page, self.url), self.resolved)
        self.browser.close.assert_called_once()

    def test_blocked_browser_response_is_not_identity_proof(self):
        self.browser.goto.return_value.ok = False
        with self.assertRaisesRegex(RuntimeError, 'preserving Replies'):
            self.ns['_resolve_profile_in_browser'](self.page, self.url)
        self.browser.close.assert_called_once()

    def test_browser_checkpoint_is_not_identity_proof(self):
        self.page.context.request.get.side_effect = RuntimeError('reset')
        self.browser.url = 'https://www.linkedin.com/checkpoint/challenge/'
        with self.assertRaisesRegex(RuntimeError, 'preserving Replies'):
            self.ns['_resolve_profile_redirect'](self.page, self.url)
        self.browser.close.assert_called_once()

    def test_browser_failure_has_no_cookie_in_error_or_log(self):
        self.page.context.request.get.side_effect = RuntimeError('cookie=SECRET')
        self.browser.goto.side_effect = RuntimeError('cookie=SECRET')
        with self.assertRaises(RuntimeError) as caught:
            self.ns['_resolve_profile_redirect'](self.page, self.url)
        self.assertNotIn('SECRET', str(caught.exception))
        self.assertTrue(caught.exception.__suppress_context__)
        self.assertNotIn('SECRET', str(self.ns['logger'].mock_calls))
        self.browser.close.assert_called_once()

    def test_conflicting_canonical_is_rejected(self):
        self.browser.locator.return_value.inner_html.return_value = (
            '<link rel="canonical" href="https://linkedin.com/in/one/">'
            '<meta property="og:url" content="https://linkedin.com/in/two/">')
        with self.assertRaisesRegex(RuntimeError, 'preserving Replies'):
            self.ns['_resolve_profile_in_browser'](self.page, self.url)
        self.browser.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
