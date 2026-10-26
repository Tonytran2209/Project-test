/* @layer presentation @feature messages: persistent Ready inbox, no send action. */
(() => {
  const byId = id => document.getElementById(id);
  const button = byId('readyNotificationsButton');
  const popover = byId('readyNotificationsPopover');
  if (!button || !popover) return;
  const list = byId('readyNotificationsList');
  const badge = byId('readyNotificationsBadge');
  const selectAll = byId('readyNotificationsSelectAll');
  const deleteButton = byId('readyNotificationsDelete');
  const errorBox = byId('readyNotificationsError');
  const dialog = byId('readyDeleteDialog');
  const confirmButton = byId('readyDeleteConfirm');
  const cancelButton = byId('readyDeleteCancel');
  const dialogError = byId('readyDeleteError');
  let items = [], selected = new Set(), loading = false, deleting = false, signature = '';
  let pendingIds = [];
  let mutation = 0;

  async function api(path, options = {}) {
    const response = await fetch('/api/outreach/messages/' + path, {
      cache: 'no-store', ...options,
      headers: {'Accept':'application/json', 'Content-Type':'application/json'},
    });
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.error || 'Could not update Ready batches.');
    return result;
  }
  function showError(element, error) {
    element.textContent = error ? error.message || String(error) : '';
    element.hidden = !error;
  }
  function selectionState() {
    deleteButton.disabled = deleting || selected.size === 0;
    selectAll.disabled = deleting || items.length === 0;
    selectAll.checked = items.length > 0 && selected.size === items.length;
    selectAll.indeterminate = selected.size > 0 && selected.size < items.length;
  }
  function setOpen(open) {
    popover.hidden = !open;
    button.setAttribute('aria-expanded', String(open));
    if (open) { void refresh(); byId('readyNotificationsClose').focus(); }
    else button.focus();
  }
  function render() {
    badge.hidden = !items.some(item => !item.seen_at);
    selected = new Set([...selected].filter(id => items.some(item => item.batch_id === id)));
    list.replaceChildren();
    if (!items.length) {
      const empty = document.createElement('p');
      empty.className = 'ready-notifications-empty'; empty.textContent = 'No Ready batches'; list.append(empty);
    }
    items.forEach(item => {
      const row = document.createElement('div');
      row.className = 'ready-notification-row' + (item.seen_at ? '' : ' is-unread');
      const label = document.createElement('label');
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox'; checkbox.checked = selected.has(item.batch_id); checkbox.disabled = deleting;
      checkbox.setAttribute('aria-label', 'Select ' + item.label);
      checkbox.addEventListener('change', () => {
        if (checkbox.checked) selected.add(item.batch_id); else selected.delete(item.batch_id);
        selectionState();
      });
      label.append(checkbox);
      const open = document.createElement('button'); open.type = 'button';
      const title = document.createElement('strong'); title.textContent = item.label;
      const meta = document.createElement('small');
      meta.textContent = `${item.recipient_count} ready · ${new Date(item.created_at).toLocaleString()}`;
      open.append(title, meta);
      open.addEventListener('click', async () => {
        try {
          await window.outreachReadyNavigation(item.batch_id);
          await api(`ready-notifications/${encodeURIComponent(item.batch_id)}/seen`, {method:'POST'});
          mutation += 1;
          item.seen_at = new Date().toISOString(); render(); setOpen(false);
        } catch (error) { showError(errorBox, error); }
      });
      row.append(label, open); list.append(row);
    });
    selectionState();
  }
  async function refresh() {
    if (loading || deleting) return;
    loading = true;
    const currentMutation = mutation;
    try {
      const result = await api('ready-notifications');
      if (deleting || currentMutation !== mutation) return;
      const next = Array.isArray(result.items) ? result.items : [];
      const nextSignature = JSON.stringify(next);
      if (nextSignature !== signature) {
        items = next; signature = nextSignature; render();
        window.dispatchEvent(new Event('outreach-ready-updated'));
      }
      showError(errorBox, null); button.title = '';
    } catch (error) {
      showError(errorBox, error); button.title = error.message;
    } finally { loading = false; }
  }
  button.addEventListener('click', () => setOpen(popover.hidden));
  byId('readyNotificationsClose').addEventListener('click', () => setOpen(false));
  selectAll.addEventListener('change', () => {
    selected = selectAll.checked ? new Set(items.map(item => item.batch_id)) : new Set(); render();
  });
  deleteButton.addEventListener('click', () => {
    pendingIds = [...selected];
    if (!pendingIds.length) return;
    byId('readyDeleteTitle').textContent = `Delete ${pendingIds.length} batch${pendingIds.length === 1 ? '' : 'es'}?`;
    showError(dialogError, null); dialog.showModal(); cancelButton.focus();
  });
  cancelButton.addEventListener('click', () => { if (!deleting) dialog.close(); });
  dialog.addEventListener('cancel', event => { if (deleting) event.preventDefault(); });
  dialog.addEventListener('close', () => deleteButton.focus());
  confirmButton.addEventListener('click', async () => {
    if (deleting || !pendingIds.length) return;
    deleting = true; mutation += 1; confirmButton.disabled = true; cancelButton.disabled = true; render();
    try {
      await api('ready-batches/delete', {method:'POST', body:JSON.stringify({batch_ids:pendingIds})});
      items = items.filter(item => !pendingIds.includes(item.batch_id));
      selected.clear(); pendingIds = []; signature = ''; render(); dialog.close();
      window.dispatchEvent(new Event('outreach-ready-updated'));
    } catch (error) { showError(dialogError, error); }
    finally { deleting = false; confirmButton.disabled = false; cancelButton.disabled = false; render(); }
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !popover.hidden && !dialog.open) setOpen(false);
  });
  document.addEventListener('click', event => {
    if (!popover.hidden && !dialog.open && !dialog.contains(event.target) && !popover.contains(event.target) && !button.contains(event.target)) {
      popover.hidden = true; button.setAttribute('aria-expanded', 'false');
    }
  });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) void refresh(); });
  render(); void refresh();
  window.setInterval(() => { if (!document.hidden) void refresh(); }, 15000);
})();
