from concurrent.futures import ThreadPoolExecutor
from threading import Event
import unittest
from unittest.mock import Mock

from app.outreach_campaign_cache import CampaignCache


class CampaignCacheTests(unittest.TestCase):
    def setUp(self):
        self.now = 100
        self.cache = CampaignCache(clock=lambda:self.now)
        self.loader = Mock(return_value=[{'added':10}])

    def test_warm_requests_reuse_aggregation_until_thirty_seconds(self):
        self.cache.get('all', self.loader)
        self.now += 29
        self.assertEqual(self.cache.get('all', self.loader), [{'added':10}])
        self.loader.assert_called_once_with('all')
        self.now += 1
        self.cache.get('all', self.loader)
        self.assertEqual(self.loader.call_count, 2)

    def test_manual_refresh_bypasses_cache_and_windows_do_not_mix(self):
        self.cache.get('all', self.loader)
        self.cache.get('all', self.loader, force=True)
        self.cache.get('7d', self.loader)
        self.assertEqual(self.loader.call_count, 3)
        self.assertEqual(set(self.cache.entries), {'all','7d'})

    def test_callers_cannot_mutate_cached_metrics(self):
        result = self.cache.get('all', self.loader)
        result[0]['added'] = 999
        self.assertEqual(self.cache.get('all', self.loader)[0]['added'], 10)

    def test_failed_refresh_keeps_old_entry_without_extending_ttl(self):
        self.cache.get('all', self.loader)
        self.now += 31
        self.loader.side_effect = RuntimeError('DB unavailable')
        with self.assertRaises(RuntimeError): self.cache.get('all', self.loader)
        self.assertEqual(self.cache.entries['all'][0], 100)
        self.loader.side_effect = None
        self.cache.get('all', self.loader)
        self.assertEqual(self.loader.call_count, 3)

    def test_parallel_cold_requests_perform_only_one_database_load(self):
        entered, finish = Event(), Event()
        def slow(window):
            entered.set()
            if not finish.wait(2): raise TimeoutError('Test timeout')
            return [{'added':1}]
        loader = Mock(side_effect=slow)
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.cache.get, 'all', loader) for _ in range(4)]
            self.assertTrue(entered.wait(1)); finish.set()
            self.assertTrue(all(future.result() == [{'added':1}] for future in futures))
        loader.assert_called_once()

    def test_invalid_window_never_queries_database(self):
        with self.assertRaises(ValueError): self.cache.get('invalid', self.loader)
        self.loader.assert_not_called()


if __name__ == '__main__':
    unittest.main()
