const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('frontend/app.js', 'utf8');
const start = source.indexOf('async function refreshOutreachRepliesAfterScan()');
const end = source.indexOf('\nasync function pollOutreachReplyRevision()', start);
const accounts = [{account_id:'outreach_account_01',reply_count:0},
                  {account_id:'outreach_account_05',reply_count:1}];

function harness({selected=null, fail=false, metadataFail=false, switchDuringFetch=false}={}) {
  let pages=0, renders=0;
  const state = {outreachReplySelectedAccountId:selected, outreachReplyAccounts:[],
    outreachReplyNextOffsetByAccount:{}, outreachReplySelectedIdByAccount:{},
    outreachReplyHasMoreByAccount:{}, outreachReplies:[], outreachReplyRequestGeneration:0};
  const els={outreachReplyError:{hidden:true,textContent:''}};
  const ctx={state,els,OUTREACH_REPLY_BATCH_SIZE:20,URLSearchParams,
    document:{activeElement:null,querySelector:()=>({hidden:false})}, console:{error(){}},
    renderOutreachReplies(){renders++;},
    fetch:async url=>{
      if(url.includes('metadata')) return {ok:!metadataFail,json:async()=>({ok:!metadataFail,
        accounts,revision:'new',detail:'Metadata unavailable'})};
      pages++;
      if(switchDuringFetch) state.outreachReplySelectedAccountId='outreach_account_07';
      return {ok:!fail,json:async()=>({ok:!fail,detail:'Conversation API unavailable',
        replies:[{id:'r1',assigned_account_id:'outreach_account_05'}],has_more:false})};
    }};
  vm.createContext(ctx);
  vm.runInContext(source.slice(start,end),ctx);
  return {state,els,run:()=>ctx.refreshOutreachRepliesAfterScan(),get pages(){return pages;},get renders(){return renders;}};
}

test('metadata recovery selects an account with replies and loads its conversations',async()=>{
  const h=harness(); await h.run();
  assert.equal(h.state.outreachReplySelectedAccountId,'outreach_account_05');
  assert.equal(h.state.outreachReplies.length,1);
  assert.equal(h.pages,1);
  assert.equal(h.state.outreachReplyRefreshing,false);
});
test('removed account falls back to a valid account',async()=>{
  const h=harness({selected:'removed'}); await h.run();
  assert.equal(h.state.outreachReplySelectedAccountId,'outreach_account_05');
  assert.equal(h.pages,1);
});
test('explicit valid selection is retained even when another account has replies',async()=>{
  const h=harness({selected:'outreach_account_01'}); await h.run();
  assert.equal(h.state.outreachReplySelectedAccountId,'outreach_account_01');
  assert.equal(h.pages,0);
});
test('page API failure is visible and preserves previous conversations',async()=>{
  const h=harness({selected:'outreach_account_05',fail:true});
  h.state.outreachReplies=[{id:'old'}]; await h.run();
  assert.equal(h.els.outreachReplyError.hidden,false);
  assert.match(h.els.outreachReplyError.textContent,/Conversation API unavailable/);
  assert.equal(h.state.outreachReplies[0].id,'old');
  assert.equal(h.state.outreachReplyRevision,undefined);
});
test('metadata errors are visible',async()=>{
  const h=harness({metadataFail:true}); await h.run();
  assert.equal(h.els.outreachReplyError.hidden,false);
  assert.match(h.els.outreachReplyError.textContent,/Metadata unavailable/);
});
test('successful retry clears the previous visible error',async()=>{
  const h=harness(); h.els.outreachReplyError={hidden:false,textContent:'old error'}; await h.run();
  assert.equal(h.els.outreachReplyError.hidden,true);
  assert.equal(h.els.outreachReplyError.textContent,'');
});
test('account changes during fetch cannot overwrite newer selection or its data',async()=>{
  const h=harness({selected:'outreach_account_05',switchDuringFetch:true}); await h.run();
  assert.equal(h.state.outreachReplySelectedAccountId,'outreach_account_07');
  assert.equal(h.renders,0);
  assert.equal(h.state.outreachReplies.length,0);
});
