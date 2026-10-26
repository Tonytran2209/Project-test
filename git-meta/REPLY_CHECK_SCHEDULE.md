# Scheduled LinkedIn reply checks (Mac worker)

The reply-check worker scans the configured Outreach accounts (seven by default) sequentially at
**12:00 and 18:00 Asia/Ho_Chi_Minh** every day. It records every Unread
conversation that matches a successfully sent target for the same account and
restores LinkedIn's unread state; it does not send messages.
The Replies inbox reads those saved conversations and checks for new scan data
every 30 seconds while the tab is open, updating the selected chat when it changes.
The worker retains the original sent target, campaign and batch context.
Membership is URL-only: display names (including abbreviations like Stan M.) and
message text are never used to decide whether a thread belongs to a sent target.
An account without any sent targets skips all its Unread entries. Otherwise a
thread can be opened for URL inspection, but its history is not read or saved
until the member URL matches a successfully sent target of that same account.
The recipient's structural header URL takes precedence over message author links.
Sidebar rows, navigation, message-body links and outgoing-author links are excluded.
The active-thread menu locates header scopes when message-list classes differ.
An ambiguous header/author URL is an error, not a name-based guess.

A captured row URL is used only if the captured and opened thread URLs agree.
Previously verified target/thread links can be reused if live profile links are
missing. Direct URL comparison strips tracking/trailing slashes and normalizes
member slugs. On a mismatch, authenticated HTTP redirects and member-page
canonical URLs are checked; results are cached within that account scan. This
can add profile requests on the first unmatched URL. Blocked/failed lookups fail
conservatively instead of treating an unverified person as outside the list.
If the HTTP lookup fails (including connection resets), the worker opens a
temporary profile tab in the same authenticated browser context and checks its
redirect/canonical URL without navigating away from the chat. The temporary tab
is closed on success or failure. Login/checkpoint pages, blocked responses and
conflicting canonical URLs remain unverified; neither names nor message URLs
are used as identity substitutes. Opaque member IDs retain their original case
when accessed. Request exception text is not logged because it can contain
session cookies. `REPLY URL CHECK` records the account, chat name and observed
profile URL before lookup, including when lookup subsequently fails.
Matched rows retain their original sent target and stored profile URL, preserving
campaign/batch identity. Outsiders (including company conversations) are skipped
without reading full history; opened threads have their unread state restored.
No exact message-text match is required to identify a thread. Message-role rules
remain unchanged. Missing recipient URLs preserve the previous snapshot.

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
