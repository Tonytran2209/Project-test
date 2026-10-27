const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('frontend/app.js','utf8');
const html = fs.readFileSync('frontend/index.html','utf8');
function extract(from,to) { return source.slice(source.indexOf(from), source.indexOf(to,source.indexOf(from))); }
function setup() {
  const state={messageBatchPage:1,messageBatchWeekKey:'week',messageBatchSourceFilter:'all',messageBatches:[],messagePreparation:{items:[]},outreachAcceptedPool:{items:[]}};
  const context={state,Set,normaliseStatus:v=>String(v).toLowerCase(),
    renderOutreachAcceptedPool(){},renderMessagePreparation(){},getWeekInfo:()=>({key:'week'}),getMessageBatchSourceConnectIds:b=>b.sources || []};
  vm.createContext(context);
  vm.runInContext(extract('function getMessageWorkspaceRows(','function getMessageBatchWeekGroups('), context);
  return {context,state};
}
test('one Messages panel contains both recipients and message batches with no Recipients navigation',()=>{
  assert.doesNotMatch(html,/data-outreach-process-(?:tab|panel)="recipients"/);
  assert.equal((html.match(/data-outreach-process-panel="messages"/g)||[]).length,1);
  const start=html.indexOf('data-outreach-process-panel="messages"');
  const end=html.indexOf('</section>',start);
  for(const id of ['outreachAcceptedPoolPanel','messageBatchesPanel']) {
    const index=html.indexOf(`id="${id}"`,start); assert.ok(index>start && index<end);
  }
});
test('user only sends; no visible manual Prepare or recipient selection controls remain',()=>{
  assert.doesNotMatch(html,/id="messagePrepare(?:All|Selected)Button"/);
  assert.doesNotMatch(html,/data-accepted-select|data-recipient-campaign-select/);
  assert.match(html,/data-message-batch-send/);
  assert.doesNotMatch(html,/data-message-workspace-view/);
});
test('pending recipients appear as Needs info rows in the same list',()=>{
  const ui=setup();
  ui.state.messagePreparation.items=[{prospect_id:'p1'},{prospect_id:'p2'}];
  ui.state.outreachAcceptedPool.items=[
    {prospect_id:'p1',connect_batch_id:'source',batch_label:'Batch A',accepted_at:'2026-10-27'},
    {prospect_id:'p2',connect_batch_id:'source',batch_label:'Batch A',accepted_at:'2026-10-27'},
    {prospect_id:'already-prepared',connect_batch_id:'source'}];
  ui.state.messageBatches=[{id:'ready',status:'prepared'}];
  const result=ui.context.getMessageWorkspaceRows();
  assert.equal(result.length,2);
  const pending=result.find(r=>r.status==='needs_info');
  assert.equal(pending.target_count,2);
  assert.equal(pending.targets.length,2);
  assert.equal(ui.context.getFilteredMessageBatches().length,2);
});
test('all lifecycle states are shown together, preserving source filtering',()=>{
  const ui=setup();
  for(const status of ['prepared','queued','processing','completed','failed']) {
    ui.state.messageBatches.push({id:status,status,sources:[{id:'source'}]});
  }
  assert.equal(ui.context.getFilteredMessageBatches().length,5);
  ui.state.messageBatchSourceFilter='other';
  assert.equal(ui.context.getFilteredMessageBatches().length,0);
});
test('legacy Recipients entry and bell open the one Messages list',()=>{
  const fn=extract('function setOutreachProcessTab(','const LAST_TAB_STORAGE_KEY');
  assert.match(fn,/tabName === "recipients" \? "messages"/);
  assert.match(fn,/loadOutreachAcceptedPool\(\)/);
  assert.match(fn,/loadMessageBatches\(\)/);
  const bell=source.slice(source.indexOf('window.outreachReadyNavigation ='), source.indexOf('window.addEventListener("outreach-ready-updated"'));
  assert.match(bell,/openPreparedMessageBatch\(batchId\)/);
  assert.doesNotMatch(source,/setMessageWorkspaceView|messageWorkspaceView/);
});
test('four-step navigation and hidden recipient panel cannot leak layout',()=>{
  const nav=fs.readFileSync('frontend/workflow-nav.css','utf8');
  assert.doesNotMatch(nav,/repeat\(5/);
  assert.match(nav,/repeat\(4/);
  const css=fs.readFileSync('frontend/messages-workspace.css','utf8');
  assert.match(css,/#outreachAcceptedPoolPanel\[hidden\].*display:none !important/);
});
