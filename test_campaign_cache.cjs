const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
function setup(storage=new Map()) {
  let now=100000, calls=[];
  const ctx={window:{},sessionStorage:{getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,value)},
    Date:{now:()=>now},fetch:async url=>{calls.push(url);return {ok:true,json:async()=>({ok:true,campaigns:[{campaign_id:url}]})};}};
  vm.createContext(ctx);vm.runInContext(fs.readFileSync('frontend/campaign-cache.js','utf8'),ctx);
  return {ctx,cache:ctx.window.outreachCampaignCache,calls,storage,advance:ms=>{now+=ms;}};
}
test('warm view loads immediately without another request',async()=>{
  const s=setup();await s.cache.load('all');await s.cache.load('all');
  assert.equal(s.calls.length,1);assert.equal(s.cache.read('all').data.length,1);
});
test('timeframes are isolated and Refresh bypasses both caches',async()=>{
  const s=setup();await s.cache.load('all');await s.cache.load('7d');await s.cache.load('all',{force:true});
  assert.equal(s.calls.length,3);assert.match(s.calls.at(-1),/&refresh=true$/);
});
test('session cache restores after reload and expires after five minutes',async()=>{
  const first=setup();await first.cache.load('all');
  const next=setup(first.storage);assert.equal(next.cache.read('all').data.length,1);
  await next.cache.load('all');assert.equal(next.calls.length,0);
  next.advance(300001);assert.equal(next.cache.read('all'),null);
});
test('old cache is shown but revalidated in background',async()=>{
  const s=setup();await s.cache.load('all');s.advance(16000);
  assert.ok(s.cache.read('all'));await s.cache.load('all');assert.equal(s.calls.length,2);
});
test('concurrent requests share one fetch',async()=>{
  const s=setup();await Promise.all([s.cache.load('all'),s.cache.load('all')]);assert.equal(s.calls.length,1);
});
test('failed responses are not cached and can be retried',async()=>{
  const s=setup();s.ctx.fetch=async()=>({ok:false,json:async()=>({error:'Offline'})});
  await assert.rejects(s.cache.load('all'),/Offline/);assert.equal(s.cache.read('all'),null);
  s.ctx.fetch=async()=>({ok:true,json:async()=>({ok:true,campaigns:[]})});
  await s.cache.load('all');assert.equal(s.cache.read('all').data.length,0);
});
test('storage failure does not break loading',async()=>{
  const s=setup();s.ctx.sessionStorage={getItem(){throw Error('Blocked');},setItem(){throw Error('Quota');}};
  await s.cache.load('all');assert.ok(s.cache.read('all'));
});
test('refresh during a normal pending request forces a second fresh fetch',async()=>{
  const s=setup();let resolve;const urls=[];
  s.ctx.fetch=url=>{urls.push(url);return urls.length===1?new Promise(done=>resolve=done):Promise.resolve({ok:true,json:async()=>({ok:true,campaigns:[]})});};
  const normal=s.cache.load('all'),refresh=s.cache.load('all',{force:true});
  resolve({ok:true,json:async()=>({ok:true,campaigns:[]})});await Promise.all([normal,refresh]);
  assert.equal(urls.length,2);assert.match(urls[1],/&refresh=true$/);
});

test('switching timeframe during fetch cannot overwrite newer metrics',async()=>{
  const code=fs.readFileSync('frontend/app.js','utf8');let finishOld;
  const ctx={window:{outreachCampaignCache:{read:()=>null,load:window=>window==='all'?new Promise(done=>finishOld=done):Promise.resolve([{campaign_id:'new'}])}},
    state:{campaignPerformanceWindow:'all',campaignPerformanceRequestId:0},renderCampaignPerformance(){},renderCampaignPerformanceFilter(){}};
  vm.createContext(ctx);
  vm.runInContext(code.slice(code.indexOf('async function loadCampaignPerformance('),code.indexOf('document.querySelectorAll("[data-campaign-window]").forEach((button) => {',code.indexOf('async function loadCampaignPerformance('))),ctx);
  const old=ctx.loadCampaignPerformance();ctx.state.campaignPerformanceWindow='7d';await ctx.loadCampaignPerformance();
  finishOld([{campaign_id:'old'}]);await old;
  assert.equal(ctx.state.campaignPerformance[0].campaign_id,'new');
  assert.equal(ctx.state.campaignPerformanceLoadedWindow,'7d');
});

test('background loading and errors keep same-window cached rows visible',()=>{
  const code=fs.readFileSync('frontend/app.js','utf8');
  const elements={campaignsStatus:{classList:{remove(){},add(){}}},campaignsTable:{hidden:true},campaignsRows:{}};
  const ctx={document:{querySelector:selector=>elements[selector.slice(1)],querySelectorAll:()=>[]},escapeHtml:String,
    state:{campaignPerformanceLoading:true,campaignPerformanceLoadedWindow:'all',campaignPerformanceWindow:'all',
      campaignPerformanceFilter:'all',campaignPerformance:[{campaign_id:'video',campaign_name:'Video',batches:[],accounts:[]}],campaignPerformanceError:''}};
  vm.createContext(ctx);
  vm.runInContext(code.slice(code.indexOf('function renderCampaignPerformance()'),code.indexOf('async function loadCampaignPerformance(')),ctx);
  ctx.renderCampaignPerformance();assert.equal(elements.campaignsTable.hidden,false);
  ctx.state.campaignPerformanceLoading=false;ctx.state.campaignPerformanceError='Offline';
  ctx.renderCampaignPerformance();assert.equal(elements.campaignsTable.hidden,false);
  assert.match(elements.campaignsStatus.innerHTML,/Offline/);
});
