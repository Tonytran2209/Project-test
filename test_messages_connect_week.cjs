const test=require('node:test'), assert=require('node:assert/strict'), fs=require('node:fs'), vm=require('node:vm');
const code=fs.readFileSync('frontend/app.js','utf8');
function part(a,b) { return code.slice(code.indexOf(a),code.indexOf(b,code.indexOf(a))); }
function setup() {
  class FixedDate extends Date { constructor(...args) { super(...(args.length ? args : ['2026-10-27T08:00:00Z'])); } }
  const ctx={Date:FixedDate,Intl,Set,Map,state:{messageBatches:[],messagePreparation:{items:[]},outreachAcceptedPool:{items:[]},messageBatchSourceFilter:'all'},
    getMessageBatchSourceConnectIds:b=>b.source_connect_ids || [],normaliseStatus:s=>s};
  vm.createContext(ctx);
  vm.runInContext(part('function getWeekInfo(','function getAcceptancePeriodRows('),ctx);
  vm.runInContext(part('function getMessageConnectDate(','function renderMessageBatchWeekOption('),ctx);
  vm.runInContext(part('function getMessageBatchWeekSelection(','function renderMessageBatchWeekList('),ctx);
  return ctx;
}
test('batch prepared Oct 27 remains in original Oct 23 Connect week',()=>{
  const ctx=setup();
  const batch={id:'b',status:'prepared',created_at:'2026-10-27T08:00:00Z',target_count:4,
    source_connect_ids:[{id:'connect',created_at:'2026-10-23T08:00:00Z'}]};
  ctx.state.messageBatches=[batch];
  const originalWeek=ctx.getWeekInfo('2026-10-23T08:00:00Z').key;
  ctx.state.messageBatchWeekKey=originalWeek;
  assert.equal(ctx.getFilteredMessageBatches()[0].id,'b');
  ctx.state.messageBatchWeekKey=ctx.getWeekInfo('2026-10-27T08:00:00Z').key;
  assert.equal(ctx.getFilteredMessageBatches().length,0);
  assert.equal(batch.created_at,'2026-10-27T08:00:00Z');
});
test('Sep 3 batch accepted Oct 26 stays in September and can be sent',()=>{
  const ctx=setup();
  ctx.state.messagePreparation.items=[{prospect_id:'p'}];
  ctx.state.outreachAcceptedPool.items=[{prospect_id:'p',connect_batch_id:'connect',job_created_at:'2026-09-03T08:00:00Z',accepted_at:'2026-10-26T08:00:00Z'}];
  const row=ctx.getMessageWorkspaceRows()[0];
  assert.equal(row.status,'prepared');
  assert.equal(ctx.getWeekInfo(ctx.getMessageConnectDate(row)).key,ctx.getWeekInfo('2026-09-03T08:00:00Z').key);
});
test('default selection recovers original week after initial empty API load',()=>{
  const ctx=setup();
  ctx.getMessageBatchWeekSelection();
  ctx.state.messageBatches=[{status:'prepared',created_at:'2026-10-27T08:00:00Z',source_connect_ids:[{id:'old',created_at:'2026-10-23T08:00:00Z'}]}];
  assert.equal(ctx.getMessageBatchWeekSelection().selected.key,ctx.getWeekInfo('2026-10-23T08:00:00Z').key);
});
test('explicit week selection is not overwritten by automatic refresh',()=>{
  const ctx=setup();
  ctx.state.messageBatchWeekKey=ctx.getWeekInfo('2026-10-27T08:00:00Z').key;
  ctx.state.messageBatchWeekUserSelected=true;
  ctx.state.messageBatches=[{status:'prepared',source_connect_ids:[{id:'old',created_at:'2026-10-23T08:00:00Z'}]}];
  assert.equal(ctx.getMessageBatchWeekSelection().selected.key,ctx.state.messageBatchWeekKey);
});
test('missing source date never falls back to acceptance or preparation date',()=>{
  const ctx=setup();
  const batch={status:'prepared',created_at:'2026-10-27T08:00:00Z',source_connect_ids:[{id:'unknown'}]};
  ctx.state.messageBatches=[batch];
  assert.equal(ctx.getMessageConnectDate(batch),undefined);
  assert.equal(ctx.getMessageBatchWeekGroups().length,0);
});
test('Send messages stages pending accepted recipients then opens confirmation, never queues',async()=>{
  const calls=[],opened=[],errors=[];
  const ctx={fetch:async(url,options)=>{calls.push({url,options});return {ok:true,json:async()=>({ok:true,created:true,batch:{id:'prepared-id'}})};},
    loadOutreachAcceptedPool:async()=>{},loadMessagePreparation:async()=>{},loadMessageBatches:async()=>{},
    focusPreparedMessageResult(){},openMessageSendModal:async id=>opened.push(id),window:{alert:message=>errors.push(message)}};
  vm.createContext(ctx);
  vm.runInContext(part('async function openAcceptedBatchForSending(','function focusPreparedMessageResult('),ctx);
  const button={disabled:false};
  await ctx.openAcceptedBatchForSending({targets:[{prospect_id:'p1'},{prospect_id:'p2'}]},button);
  assert.deepEqual(JSON.parse(calls[0].options.body),{prospect_ids:['p1','p2']});
  assert.equal(calls.length,1);
  assert.equal(calls[0].url,'/api/outreach/messages/prepare-selected');
  assert.deepEqual(opened,['prepared-id']);
  assert.equal(button.disabled,false);
  assert.equal(errors.length,0);
});
