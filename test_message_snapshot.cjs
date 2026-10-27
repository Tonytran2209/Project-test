const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('frontend/app.js', 'utf8');
const html = fs.readFileSync('frontend/index.html', 'utf8');
function setup(fetch) {
  const dialog = {open: false, dataset: {}, showModal() { this.open = true; }};
  const els = {messageSnapshotDialog: dialog, messageSnapshotTitle: {}, messageSnapshotCount: {}, messageSnapshotContent: {}};
  const ctx = {els, fetch, getOutreachAccountDisplayName: id => id,
    escapeHtml: value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[char]))};
  vm.createContext(ctx);
  vm.runInContext(source.slice(source.indexOf('async function openPreparedMessageBatch('), source.indexOf('function openMessagePrepareConfirmModal(')), ctx);
  return ctx;
}
test('snapshot dialog exists and is bound, not the removed drawer', () => {
  for (const id of ['messageSnapshotDialog', 'messageSnapshotTitle', 'messageSnapshotCount', 'messageSnapshotContent']) {
    assert.ok(html.includes(`id="${id}"`));
    assert.ok(source.includes(`document.querySelector("#${id}")`));
  }
  assert.ok(html.includes('data-message-snapshot-close'));
});
test('persisted snapshot opens with company, name, profile and account in grid', async () => {
  const ctx = setup(async url => {
    assert.equal(url, '/api/outreach/messages/batches/batch-1');
    return {ok: true, json: async () => ({ok:true, batch:{batch_code:'October - Video', targets:[{
      first_name:'Alice', company_name:'Studio & Co', assigned_account_id:'outreach_account_06', linkedin_url:'https://linkedin.com/in/alice', message_text:'Hi Alice\nThanks!'
    }]}})};
  });
  assert.equal(await ctx.openPreparedMessageBatch('batch-1'), true);
  assert.equal(ctx.els.messageSnapshotDialog.open, true);
  assert.equal(ctx.els.messageSnapshotCount.textContent, '1 recipient');
  assert.match(ctx.els.messageSnapshotContent.innerHTML, /Studio &amp; Co/);
  assert.match(ctx.els.messageSnapshotContent.innerHTML, /Alice/);
  assert.match(ctx.els.messageSnapshotContent.innerHTML, /outreach_account_06/);
  assert.match(ctx.els.messageSnapshotContent.innerHTML, /message-snapshot-table/);
});
test('pending accepted snapshot renders company without preparing or queueing', async () => {
  const ctx = setup(() => { throw Error('Must not call API'); });
  assert.equal(await ctx.openPreparedMessageBatch('accepted:old', {pending_snapshot:true, targets:[{company_name:'Saved Company'}]}), true);
  assert.match(ctx.els.messageSnapshotContent.innerHTML, /Saved Company/);
});
test('failed fetch is visible inside an open dialog', async () => {
  const ctx = setup(async () => ({ok:false, json:async () => ({detail:'Batch unavailable'})}));
  assert.equal(await ctx.openPreparedMessageBatch('bad'), false);
  assert.equal(ctx.els.messageSnapshotDialog.open, true);
  assert.match(ctx.els.messageSnapshotContent.innerHTML, /role="alert">Batch unavailable/);
});
test('snapshot escapes content and never makes script URLs clickable', async () => {
  const ctx = setup();
  await ctx.openPreparedMessageBatch('local', {targets:[{company_name:'<script>alert(1)</script>', linkedin_url:'javascript:alert(1)'}]});
  const content = ctx.els.messageSnapshotContent.innerHTML;
  assert.ok(!content.includes('<script>'));
  assert.ok(!content.includes('href="javascript:'));
});
test('a stale request cannot replace a newer snapshot', async () => {
  let resolve;
  const ctx = setup(() => new Promise(done => { resolve = done; }));
  const first = ctx.openPreparedMessageBatch('first');
  await ctx.openPreparedMessageBatch('second', {batch_code:'Second', targets:[]});
  resolve({ok:true, json:async () => ({ok:true, batch:{batch_code:'First'}})});
  assert.equal(await first, false);
  assert.equal(ctx.els.messageSnapshotTitle.textContent, 'Second');
});
