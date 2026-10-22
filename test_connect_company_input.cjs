const {test} = require('node:test');
const assert = require('node:assert/strict');
require('./frontend/connect-input.js');
const {parse} = globalThis.ConnectInput;
const a = 'https://linkedin.com/in/a';
const b = 'https://linkedin.com/in/b';

test('spreadsheet rows preserve order and punctuation in company names', () => {
  assert.deepEqual(parse(`${a}\r\n${b}\r\n`, 'A, Inc.\r\nB & Co\r\n'), {
    urls: [a, b], companyNames: ['A, Inc.', 'B & Co'], error: ''
  });
});
test('missing companies and internal empty rows block submission', () => {
  assert.ok(parse(`${a}\n${b}`, 'A').error);
  assert.ok(parse(`${a}\n\n${b}`, 'A\nB').error);
  assert.ok(parse(`${a}\n${a}\n${b}`, 'A\n\nB').error);
});
test('malformed or multiple URLs cannot silently shift matching', () => {
  assert.ok(parse(`not-a-url\n${b}`, 'A\nB').error);
  assert.ok(parse(`${a}, ${b}`, 'A\nB').error);
  assert.ok(parse(`${a}\n${b}`, 'A\tB\nC').error);
});
test('duplicates retain original company positions until backend processing', () => {
  const result = parse(`${a}\n${a}\n${b}`, 'First\nDuplicate\nLast');
  assert.equal(result.error, '');
  assert.deepEqual(result.companyNames, ['First', 'Duplicate', 'Last']);
  assert.deepEqual(result.urls, [a, a, b]);
});
test('URL-only workflow still accepts a comma-separated list', () => {
  assert.deepEqual(parse(`${a}, ${b}`, ''), {urls: [a, b], companyNames: null, error: ''});
});
