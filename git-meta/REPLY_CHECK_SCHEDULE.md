# Scheduled LinkedIn reply checks (Mac worker)

The reply-check worker scans the configured Outreach accounts (seven by default) sequentially at
**12:00 and 18:00 Asia/Ho_Chi_Minh** every day. It records every Unread
conversation and restores LinkedIn's unread state; it does not send messages.
The Replies inbox reads those saved conversations and checks for new scan data
every 30 seconds while the tab is open, updating the selected chat when it changes.
When a conversation matches a sent target, the worker retains campaign and
batch context. Other Unread conversations remain visible without that context.
It reads overlapping history windows from newest to oldest, classifies each
message as own, incoming, or unknown, and never treats shared message text as
sender proof. A thread with no verified profile URL is visible but cannot be
sent to by the reply worker. If the Unread list or history cannot be read
completely, the scan fails without pruning stored replies.

On the worker Mac, after pulling this repo:

First apply `outreach_reply_pruning.sql` and `outreach_reply_all_unread.sql`
once in the Supabase SQL Editor, before pulling the new worker. The second
migration allows Unread threads with no sent target to be stored. The
database function removes replies absent from a successful all-account Unread
scan, while preserving replies linked to any Send via worker job. Those
preserved older replies are hidden from the live Replies inbox but remain in
the database with their jobs. The foreign key is changed from CASCADE to
RESTRICT so a concurrent send job cannot be deleted by cleanup. Without this
SQL migration, the scan will report a cleanup error instead of silently
claiming completion.

```bash
cd /path/to/linkedin-daily-scanner
.venv/bin/python3 -m playwright install chromium
zsh git-meta/reply_check_schedule_service.sh install
zsh git-meta/reply_check_schedule_service.sh status
```

The LaunchAgent starts at login, prevents idle system sleep while waiting, and restarts
if the scheduler exits unexpectedly. The Python scheduler uses Vietnam time
regardless of the Mac's system timezone. It does not run a missed slot after
the Mac has been off; the next scheduled slot runs normally.

Logs are in `logs/reply-check.out.log` and `logs/reply-check.err.log`. To stop
the scheduled service, run:

```bash
zsh git-meta/reply_check_schedule_service.sh uninstall
```

For a one-off scan of all configured accounts:

```bash
.venv/bin/python3 -u outreach_reply_check_worker.py --all-accounts
```

Do not run other workers against the same persistent LinkedIn browser profile
at the same time as a reply scan.
