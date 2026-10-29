const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
function setup(path='/dashboard/connect') {
  const calls=[], events={}, location={pathname:path, search:''};
  const ctx={URLSearchParams, console, location, document:{title:''}, window:{addEventListener:(name,fn)=>{events[name]=fn;}},
    history:{pushState(_,__,url){const u=new URL(url,'http://local');location.pathname=u.pathname;location.search=u.search;},
      replaceState(_,__,url){this.pushState(_,__,url);}},
    loadModule:async path=>({start(){calls.push(['start',path]);return ()=>calls.push(['stop',path]);}})};
  vm.createContext(ctx);
  const code=fs.readFileSync('frontend/workspace-router.js','utf8').replace('await import(', 'await loadModule(');
  vm.runInContext(code, ctx);
  const router=ctx.window.outreachPages;
  const runtime={show:page=>calls.push(['show',page]),refresh:page=>calls.push(['refresh',page]),openSnapshot:async id=>calls.push(['snapshot',id])};
  return {router,ctx,runtime,calls,events};
}
test('five URLs resolve and assets or unknown pages never become workspaces',()=>{
  const {router}=setup();
  for(const page of ['connect','acceptance','messages','replies','campaigns']) {
    assert.equal(router.pageFromPath(`/dashboard/${page}`), page);
    assert.equal(router.pageFromPath(`/dashboard/${page}/`), page);
  }
  assert.equal(router.pageFromPath('/dashboard/app.js'),null);
  assert.equal(router.pageFromPath('/dashboard/not-a-page'),null);
});
test('direct page link wins over old saved tabs and loads only its module',async()=>{
  const s=setup('/dashboard/replies'); await s.router.start(s.runtime);
  assert.deepEqual(s.calls,[['show','replies'],['start','./pages/replies.js?v=20261029-pages-1']]);
});
test('navigation stops old page, changes URL and refreshes only current page',async()=>{
  const s=setup(); await s.router.start(s.runtime); await s.router.navigate('messages');
  assert.equal(s.ctx.location.pathname,'/dashboard/messages');
  assert.ok(s.calls.some(c=>c[0]==='stop' && c[1].includes('connect')));
  s.router.refresh(); assert.deepEqual(s.calls.at(-1),['refresh','messages']);
  const before=s.calls.length; await s.router.navigate('messages');assert.equal(s.calls.length,before);
});
test('Back/Forward mounts the URL, not the last selected tab',async()=>{
  const s=setup();await s.router.start(s.runtime);await s.router.navigate('campaigns');
  s.ctx.location.pathname='/dashboard/acceptance';s.events.popstate();
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(s.router.current,'acceptance');
  assert.equal(s.calls.at(-1)[1],'./pages/acceptance.js?v=20261029-pages-1');
});
test('Ready notification deep link opens Messages snapshot without sending',async()=>{
  const s=setup();await s.router.start(s.runtime);await s.router.navigate('messages',{snapshot:'batch/1'});
  assert.equal(s.ctx.location.search,'?snapshot=batch%2F1');
  assert.deepEqual(s.calls.at(-1),['snapshot','batch/1']);
});
test('late module imports cannot start a page after leaving it',async()=>{
  const s=setup();let complete;
  s.ctx.loadModule=path=>path.includes('connect')?new Promise(resolve=>{complete=resolve;}):Promise.resolve({start(){s.calls.push(['latest']);return ()=>{};}});
  const first=s.router.start(s.runtime);await s.router.navigate('replies');
  complete({start(){throw Error('Stale page started');}});await first;
  assert.equal(s.router.current,'replies');
});
test('legacy root URL is canonicalized to Connect',async()=>{
  const s=setup('/dashboard/');await s.router.start(s.runtime);
  assert.equal(s.ctx.location.pathname,'/dashboard/connect');
});
test('page controllers call only their own loaders',()=>{
  for(const [page,loader] of Object.entries({connect:'loadConnect',acceptance:'loadAcceptance',messages:'loadMessages',replies:'loadReplies',campaigns:'loadCampaigns'})) {
    const calls=[];
    const runtime=new Proxy({}, {get:(_,key)=>()=>calls.push(key)});
    const ctx={runtime,poll:(fn)=>{fn();return ()=>{};}};vm.createContext(ctx);
    const code=fs.readFileSync(`frontend/pages/${page}.js`,'utf8').replace(/^import.*$/m,'').replace('export function','function');
    vm.runInContext(code+';start(runtime);',ctx);
    assert.ok(calls.includes(loader));
    assert.ok(!calls.some(name=>/^load/.test(name) && name!==loader && !(page==='connect' && name==='loadConnectCampaigns')));
  }
});
test('disposed page polling never schedules another request',async()=>{
  const tasks=[],timers=new Map();let next=0;
  const ctx={document:{hidden:false},console,window:{setTimeout:fn=>{timers.set(++next,fn);return next;},clearTimeout:id=>timers.delete(id)}};
  vm.createContext(ctx);vm.runInContext(fs.readFileSync('frontend/pages/polling.js','utf8').replace('export function','function'),ctx);
  let resolve;
  const stop=ctx.poll(()=>{tasks.push('load');return new Promise(done=>resolve=done);},1000);
  stop();resolve();await new Promise(done=>setImmediate(done));
  assert.equal(tasks.length,1);assert.equal(timers.size,0);
});
