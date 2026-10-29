/* Short-lived, tab-scoped view cache; never cache errors or send actions. */
(() => {
  const memory = new Map(), pending = new Map();
  const key = window => `outreach.campaigns.v1.${window}`;
  const valid = window => ['1d','7d','30d','all'].includes(window);
  function read(window) {
    if (!valid(window)) return null;
    let entry = memory.get(window);
    if (!entry) {
      try { entry = JSON.parse(sessionStorage.getItem(key(window))); } catch (_) { return null; }
    }
    if (!entry || !Array.isArray(entry.data) || !Number.isFinite(entry.at) ||
        Date.now() - entry.at < 0 || Date.now() - entry.at > 300000) return null;
    memory.set(window, entry);
    return entry;
  }
  async function load(window, {force = false} = {}) {
    if (!valid(window)) throw Error('Invalid timeframe');
    if (pending.has(window)) {
      const active = pending.get(window);
      if (!force || active.force) return active.promise;
      // A manual refresh must not reuse an older, potentially cached request.
      try { await active.promise; } catch (_) {}
      return load(window, {force:true});
    }
    const cached = read(window);
    if (!force && cached && Date.now() - cached.at < 15000) return cached.data;
    const promise = (async () => {
      const response = await fetch(`/api/outreach/campaigns/performance?window=${encodeURIComponent(window)}${force ? '&refresh=true' : ''}`, {cache:'no-store'});
      const result = await response.json();
      if (!response.ok || !result.ok) throw Error(result.error || 'Could not load campaigns.');
      if (!Array.isArray(result.campaigns)) throw Error('Invalid campaign response.');
      const data = result.campaigns;
      const entry = {at:Date.now(), data};
      memory.set(window, entry);
      try { sessionStorage.setItem(key(window), JSON.stringify(entry)); } catch (_) {}
      return data;
    })();
    pending.set(window, {promise, force});
    try { return await promise; }
    finally { if (pending.get(window)?.promise === promise) pending.delete(window); }
  }
  window.outreachCampaignCache = {read, load};
})();
