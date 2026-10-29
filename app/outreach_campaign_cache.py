"""Bounded, process-local campaign cache; no database writes or HTTP shared cache."""
from copy import deepcopy
from threading import Lock
from time import monotonic


class CampaignCache:
    def __init__(self, ttl=30, clock=monotonic):
        self.ttl, self.clock = ttl, clock
        self.entries = {}
        self.locks = {window: Lock() for window in ('1d', '7d', '30d', 'all')}

    def get(self, window, loader, *, force=False):
        if window not in self.locks:
            raise ValueError('Unsupported campaign timeframe.')
        requested = self.clock()
        # Coalesce concurrent requests for this timeframe, including Refresh.
        with self.locks[window]:
            entry = self.entries.get(window)
            if entry and ((not force and self.clock() - entry[0] < self.ttl)
                          or entry[0] > requested):
                return deepcopy(entry[1])
            data = loader(window)
            self.entries[window] = (self.clock(), deepcopy(data))
            return data


campaign_cache = CampaignCache()
