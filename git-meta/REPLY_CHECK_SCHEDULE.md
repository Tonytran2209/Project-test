# Scheduled LinkedIn reply checks (Mac worker)

The reply-check worker scans the configured Outreach accounts (seven by default) sequentially at
**12:00 and 18:00 Asia/Ho_Chi_Minh** every day. It records every Unread
conversation that matches a successfully sent target for the same account and
restores LinkedIn's unread state; it does not send messages.
The Replies inbox reads those saved conversations and checks for new scan data
every 30 seconds while the tab is open, updating the selected chat when it changes.
The worker retains the original sent target, campaign and batch context.
Other Unread conversations are skipped before opening or reading their history;
they are not scan failures. A member URL on the list row is preferred; otherwise
a normalized recipient-name or compact full-name slug permits opening for
identity verification (not saving by name alone). Previously saved target/thread
links can also be reused, only for the same account and matching profile URL.
Recipient-named profile links in the active conversation take precedence over
own-author links, so a thread containing both participants' URLs is not rejected
merely for having multiple URLs. A captured row member URL is trusted only when
its captured thread URL matches the opened thread. No exact message-text match is
required when URL/thread identity is verified. An eligible thread whose identity
is still unresolved fails conservatively, preserving the previous snapshot
instead of silently dropping the conversation. Message-role rules are unchanged.
If no candidate identity exists, the entry is skipped rather than fuzzy-matched.

Before each click, the worker reacquires the live Unread surface. Transient
rerenders are retried; persistent missing filters reopen Messaging and select
Unread again. History is read from the page that actually owns the opened thread.
The dashboard reloads a valid account after metadata recovery and displays API
refresh errors without discarding the previous conversations.
It reads overlapping history windows from newest to oldest, classifies each
message as own, incoming, or unknown, and never treats shared message text as
sender proof. If the Unread list or an eligible conversation's history cannot be
read completely, the scan fails without pruning stored replies. Historical
unlinked threads are no longer refreshed and fall out of the live inbox after a
successful full scan; the existing pruning rules still protect linked send jobs.

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
