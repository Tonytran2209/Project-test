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

function optionsFor(configured, replies, selected = null) {
  const select = {options: [], value: '', replaceChildren(...options) {this.options = options;}};
  const context = {
    state: {outreachReplies: replies, outreachReplyAccounts: configured, outreachReplySelectedAccountId: selected},
    els: {outreachReplyAccountSelect: select},
    Option: function(textContent, value) {Object.assign(this, {textContent, value, dataset: {}});},
    replyAccountDropdown: {},
    renderConnectDropdown() {},
    escapeHtml: String,
    getOutreachAccountDisplayName: id => accounts.find(account => account.account_id === id)?.display_name || id,
  };
  vm.runInNewContext(source.slice(start, end) + '\nrenderOutreachReplyInbox();', context);
  return select;
}
test('reply dropdown includes all seven account names and reply counts', () => {
  const select = optionsFor(accounts.map((account, index) => ({...account, reply_count: index})), []);
  assert.equal(select.options.length, 7);
  assert.equal(select.options[5].textContent, 'Frank Nguyen');
  assert.equal(select.options[6].textContent, 'Phoebe');
  assert.equal(select.options[6].dataset.count, '6');
});
test('reply rows beyond the old five-account limit remain visible', () => {
  const select = optionsFor(accounts.slice(0, 5), accounts.slice(5).map(account => ({assigned_account_id: account.account_id})));
  assert.equal(select.options.length, 7);
  assert.equal(select.options[6].textContent, 'Phoebe');
  assert.equal(select.options[6].dataset.count, '1');
});
test('refreshing replies preserves the selected seventh account', () => {
  assert.equal(optionsFor(accounts, [], 'outreach_account_07').value, 'outreach_account_07');
});
