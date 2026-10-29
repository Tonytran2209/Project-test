/* Stop every page timer on navigation; do not overlap slow requests. */
export function poll(task, milliseconds, {immediate = true} = {}) {
  let disposed = false, timer;
  async function run() {
    try { if (!document.hidden && !disposed) await task(); }
    catch (error) { console.error('Workspace refresh failed', error); }
    finally { if (!disposed) timer = window.setTimeout(run, typeof milliseconds === 'function' ? milliseconds() : milliseconds); }
  }
  if (immediate) void run();
  else timer = window.setTimeout(run, milliseconds);
  return () => { disposed = true; window.clearTimeout(timer); };
}
