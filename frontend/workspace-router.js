/* Page routing and lifecycle only. Business actions stay in the existing runtime. */
(() => {
  const pages = new Set(['connect', 'acceptance', 'messages', 'replies', 'campaigns']);
  let runtime, cleanup = () => {}, generation = 0, current = '';
  const pageFromPath = path => {
    const match = String(path).match(/^\/dashboard\/(connect|acceptance|messages|replies|campaigns)\/?$/);
    return match ? match[1] : null;
  };
  const href = page => `/dashboard/${pages.has(page) ? page : 'connect'}`;
  async function mount() {
    const page = pageFromPath(location.pathname) || 'connect';
    const revision = ++generation;
    cleanup(); cleanup = () => {};
    current = page;
    runtime.show(page);
    document.title = `${page[0].toUpperCase() + page.slice(1)} · Outreach Operations`;
    try {
      const module = await import(`./pages/${page}.js?v=20261029-pages-1`);
      if (revision !== generation) return;
      cleanup = module.start(runtime);
      if (page === 'messages') {
        const batch = new URLSearchParams(location.search).get('snapshot');
        if (batch) await runtime.openSnapshot(batch);
      }
    } catch (error) {
      if (revision === generation) console.error(`Could not open ${page}`, error);
      throw error;
    }
  }
  window.outreachPages = {
    pageFromPath, href,
    get current() { return current || pageFromPath(location.pathname) || 'connect'; },
    navigate(page, {snapshot} = {}) {
      const target = href(page) + (snapshot ? `?snapshot=${encodeURIComponent(snapshot)}` : '');
      if (location.pathname + location.search === target) return Promise.resolve();
      history.pushState(null, '', target);
      return mount();
    },
    start(api) {
      runtime = api;
      if (!pageFromPath(location.pathname)) history.replaceState(null, '', href('connect'));
      window.addEventListener('popstate', () => { void mount(); });
      window.addEventListener('pagehide', () => cleanup());
      return mount();
    },
    refresh() { return runtime.refresh(current); },
  };
})();
