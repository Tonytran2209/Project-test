const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const {test} = require('node:test');

test('Settings entry, modal, handlers and dedicated styles are removed', () => {
  for (const file of ['index.html', 'app.js', 'styles.css', 'sidebar.css', 'outreach-stripe.css']) {
    const source = readFileSync(join(__dirname, 'frontend', file), 'utf8');
    assert.doesNotMatch(source, /settingsButton|settingsModal|settings-row|settings-dialog|settings-body|UiSettings|SETTINGS_STORAGE_KEY|data-settings-close/);
  }
});

test('Other system actions and section restoration remain available', () => {
  const html = readFileSync(join(__dirname, 'frontend/index.html'), 'utf8');
  const js = readFileSync(join(__dirname, 'frontend/app.js'), 'utf8');
  assert.match(html, /id="sessionStatusButton"/);
  assert.match(html, /id="usageGuideButton"/);
  assert.match(js, /localStorage\.setItem\(LAST_TAB_STORAGE_KEY, tabName\)/);
  assert.match(js, /const savedTab = localStorage\.getItem\(/);
});
