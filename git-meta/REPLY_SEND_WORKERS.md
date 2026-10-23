# Always-on reply-send workers (Mac)

The reply-send service runs one Supabase Realtime listener for each of the five
Outreach accounts. A listener opens its account's persistent LinkedIn browser
profile only when the dashboard queues a reply for that account.

After pulling the latest code on the worker Mac:

```bash
cd /path/to/linkedin-daily-scanner
zsh git-meta/reply_send_workers_service.sh install
zsh git-meta/reply_send_workers_service.sh status
```

The five LaunchAgents start at login and restart automatically after an
unexpected exit. Terminal does not need to remain open. Logs are written to
`logs/reply-send-outreach_account_*.out.log` and
`logs/reply-send-outreach_account_*.err.log`.

To reinstall after changing the service or worker code:

```bash
zsh git-meta/reply_send_workers_service.sh restart
```

To stop all five reply-send workers:

```bash
zsh git-meta/reply_send_workers_service.sh uninstall
```

Do not run another worker against the same persistent LinkedIn browser profile
while a reply-send job is using it.
