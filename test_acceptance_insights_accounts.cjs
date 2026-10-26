const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('frontend/app.js','utf8');
const names = source.match(/const OUTREACH_ACCOUNT_DISPLAY_NAMES = \{[\s\S]*?\n\};/)[0];
const helper = source.slice(source.indexOf('function getAcceptanceInsightAccountRows('), source.indexOf('function renderAcceptanceInsights('));
const context = vm.createContext({});
vm.runInContext(names + '\n' + helper, context);
const rows = insights => context.getAcceptanceInsightAccountRows(insights);
test('Insights includes Frank and Phoebe even with no Connect activity', () => {
  const result = rows({accounts: Array.from({length:5},(_,i)=>({account_id:`outreach_account_0${i+1}`,connected:10,accepted:1}))});
  assert.equal(result.length,7);
  assert.equal(result[5].account_id,'outreach_account_06');
  assert.equal(result[6].account_id,'outreach_account_07');
  assert.equal(result[5].connected,0);
  assert.equal(result[6].accepted,0);
});
test('existing order and real new-account metrics are preserved without duplicates', () => {
  const input={accounts:[{account_id:'outreach_account_07',connected:20,accepted:8,acceptance_rate:0.4}]};
  const result=rows(input);
  assert.equal(result.length,7);
  assert.equal(result[0].accepted,8);
  assert.equal(result.filter(row=>row.account_id==='outreach_account_07').length,1);
  assert.equal(input.accounts.length,1);
});
test('empty loaded scope shows seven zero rows but loading retains empty state', () => {
  assert.equal(rows({accounts:[]}).length,7);
  assert.equal(rows(null).length,0);
});
test('drawer is wider while retaining mobile viewport bounds', () => {
  const css=fs.readFileSync('frontend/acceptance-insights.css','utf8');
  assert.match(css,/width: min\(820px, calc\(100vw - 48px\)\)/);
  assert.match(css,/@media \(max-width: 600px\)/);
  assert.match(css,/width: calc\(100vw - 24px\)/);
});
