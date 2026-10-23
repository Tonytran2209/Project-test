const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('frontend/app.js', 'utf8');
const start = source.indexOf('function renderOutreachReplyInbox()');
const boundary = /\n(?:async )?function /g;
boundary.lastIndex = start + 1;
const end = boundary.exec(source).index;
const names = ['Minh Anh', 'Trang Liu', 'Minh Ánh', 'Linh Giang', 'Huyền Linh', 'Frank Nguyen', 'Phoebe'];
const accounts = names.map((display_name, index) => ({account_id: `outreach_account_0${index + 1}`, display_name}));

function tabsFor(configured, replies) {
  const buttons = [];
  const context = {
    state: {outreachReplies: replies, outreachReplyAccounts: configured},
    els: {outreachReplyAccountTabs: {replaceChildren() {buttons.length = 0;}, appendChild(button) {buttons.push(button);}}},
    document: {createElement() {return {classList: {toggle() {}}, setAttribute() {}, addEventListener() {}};}},
    escapeHtml: String,
    getOutreachAccountDisplayName: id => accounts.find(account => account.account_id === id)?.display_name || id,
  };
  vm.runInNewContext(source.slice(start, end) + '\nrenderOutreachReplyInbox();', context);
  return buttons;
}
test('reply inbox renders seven account tabs including Frank Nguyen and Phoebe', () => {
  const buttons = tabsFor(accounts, []);
  assert.equal(buttons.length, 7);
  assert.match(buttons[5].innerHTML, /Frank Nguyen/);
  assert.match(buttons[6].innerHTML, /Phoebe/);
});
test('reply rows beyond the old five-account limit remain visible', () => {
  const buttons = tabsFor(accounts.slice(0, 5), accounts.slice(5).map(account => ({assigned_account_id: account.account_id})));
  assert.equal(buttons.length, 7);
  assert.match(buttons[6].innerHTML, /Phoebe/);
});
