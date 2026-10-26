const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('frontend/ready-notifications.js','utf8');
class Element {
  constructor() { this.events={}; this.children=[]; this.hidden=false; this.checked=false; this.open=false; }
  addEventListener(name, fn) { (this.events[name] ||= []).push(fn); }
  async fire(name) { for(const fn of this.events[name] || []) await fn({target:this,preventDefault(){}}); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children=nodes; }
  setAttribute(name,value) { this[name]=value; }
  focus() { this.focused=true; }
  contains(node) { return this===node || this.children.some(c => c.contains(node)); }
  showModal() { this.open=true; }
  close() { this.open=false; void this.fire('close'); }
}
const rows = () => [{batch_id:'a',label:'Batch A - Video',recipient_count:2,created_at:'2026-10-26T00:00:00Z',seen_at:null},
                    {batch_id:'b',label:'Batch B - MKT',recipient_count:1,created_at:'2026-10-25T00:00:00Z',seen_at:'2026-10-25'}];
const settle = () => new Promise(resolve => setImmediate(resolve));
async function setup() {
  const elements = new Map(); const requests=[], navigation=[], intervals=[];
  const el = id => { if(!elements.has(id)) elements.set(id,new Element()); return elements.get(id); };
  el('readyNotificationsPopover').hidden=true;
  let result={ok:true,items:rows()};
  const context = {
    document:{getElementById:el,createElement:()=>new Element(),addEventListener(){},hidden:false},
    window:{setInterval:fn=>intervals.push(fn),dispatchEvent(){},outreachReadyNavigation:async id=>navigation.push(id)},
    Event:class{}, Set, Date, JSON, encodeURIComponent,
    fetch:async (url,options)=>{
      requests.push({url,options});
      const data = url.endsWith('/ready-notifications') ? result : context.actionResult || {ok:true};
      return {ok:data.ok,json:async()=>data};
    },
  };
  vm.runInNewContext(source,context); await settle();
  return {el,context,requests,navigation,intervals,setResult:value=>{result=value;}};
}
test('bell displays persistent batch labels, counts and unread dot without HTML injection',async()=>{
  const ui=await setup();
  assert.equal(ui.el('readyNotificationsBadge').hidden,false);
  const row=ui.el('readyNotificationsList').children[0];
  assert.equal(row.children[1].children[0].textContent,'Batch A - Video');
  assert.match(row.children[1].children[1].textContent,/2 ready/);
  assert.equal(row.children[0].children[0].type,'checkbox');
});
test('checkbox select-all requires confirmation and deletes selected batches, not notifications',async()=>{
  const ui=await setup(); const all=ui.el('readyNotificationsSelectAll');
  all.checked=true; await all.fire('change');
  assert.equal(ui.el('readyNotificationsDelete').disabled,false);
  await ui.el('readyNotificationsDelete').fire('click');
  assert.equal(ui.el('readyDeleteDialog').open,true);
  assert.equal(ui.requests.filter(r=>r.url.endsWith('/ready-batches/delete')).length,0);
  await ui.el('readyDeleteConfirm').fire('click');
  const request=ui.requests.find(r=>r.url.endsWith('/ready-batches/delete'));
  assert.deepEqual(JSON.parse(request.options.body),{batch_ids:['a','b']});
  assert.equal(ui.el('readyDeleteDialog').open,false);
  assert.equal(ui.el('readyNotificationsBadge').hidden,true);
});
test('deletion conflict preserves selections and drafts with a visible error',async()=>{
  const ui=await setup();
  const checkbox=ui.el('readyNotificationsList').children[0].children[0].children[0];
  checkbox.checked=true; await checkbox.fire('change');
  await ui.el('readyNotificationsDelete').fire('click');
  ui.context.actionResult={ok:false,error:'Batch is already queued'};
  await ui.el('readyDeleteConfirm').fire('click');
  assert.equal(ui.el('readyDeleteDialog').open,true);
  assert.equal(ui.el('readyDeleteError').textContent,'Batch is already queued');
  assert.equal(ui.el('readyNotificationsList').children.length,2);
  assert.equal(ui.el('readyNotificationsList').children[0].children[0].children[0].checked,true);
});
test('opening a batch navigates before marking it seen and never sends',async()=>{
  const ui=await setup();
  await ui.el('readyNotificationsList').children[0].children[1].fire('click');
  assert.deepEqual(ui.navigation,['a']);
  assert.ok(ui.requests.some(r=>r.url.endsWith('/ready-notifications/a/seen')));
  assert.equal(ui.requests.some(r=>/queue|send/.test(r.url)),false);
});
test('poll errors preserve existing notifications and show an error',async()=>{
  const ui=await setup(); ui.setResult({ok:false,error:'Unavailable'});
  await ui.intervals[0](); await settle();
  assert.equal(ui.el('readyNotificationsList').children.length,2);
  assert.equal(ui.el('readyNotificationsError').textContent,'Unavailable');
});
