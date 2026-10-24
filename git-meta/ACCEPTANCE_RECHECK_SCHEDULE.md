# Scheduled Acceptance rechecks (Mac)

The existing Acceptance worker handles both manual requests and scheduled checks.
The LinkedIn checker, eligibility rules and original Connect batch attribution are unchanged.
No new Supabase tables or migrations are needed.

## Calendar and two independent cursors

- Vietnam time (`Asia/Ho_Chi_Minh`), Monday–Sunday calendar weeks.
- Every Monday starts a new main cycle. Its range is frozen from the first day
  of the previous month through the end of the preceding week. A partial first
  week is clipped to the first day of that month.
- At 00:00 each day, process one week of the main cycle, oldest first.
- After that cycle is at least seven days old, any unfinished weeks become
  backlog. At 06:00 process one backlog week, oldest unfinished cycle first.
  Continue Tuesday, Wednesday and subsequent days until no backlog remains.
- A new Monday cycle never overwrites an old cycle. Crossing a month boundary
  mid-cycle does not change the old cycle's frozen range.
- A week without eligible targets completes without opening LinkedIn. A failed
  batch holds the cursor; completed batches within that week are checkpointed.
- An already queued/running manual check is deferred, not duplicated. The
  worker continues servicing the manual queue between scheduled weeks.
- Slots have a 15-minute start grace window. Missed offline slots are not replayed.
  An interrupted scheduled week resumes from its saved batch progress on restart.
- If the live Acceptance worker is still processing a manual or scheduled run at
  the next slot, that slot is queued and processed serially when it becomes free.
- Accepted results remain on the original `outreach_job_targets` row. Recheck
  dates do not become the batch's Connect week.

## Install after pulling the updated repo

Stop the old Acceptance Python process with Ctrl+C in its terminal first. Do not
leave a second copy running. Then, from the worker repo:

```sh
git pull origin main
zsh git-meta/acceptance_schedule_service.sh install
zsh git-meta/acceptance_schedule_service.sh status
tail -f logs/acceptance.err.log logs/acceptance.out.log
```

This installs one user LaunchAgent running `.venv/bin/python3 -u
outreach_acceptance_worker.py --schedule`. It restarts at login and keeps the
Mac from idle sleeping while the process is alive; it cannot run while the Mac
is shut down or the user is logged out. Do not use sudo.

Persistent progress: `output/acceptance-schedule.json`. Do not delete this file
on deploy/restart or while the worker is running. It is local to this Mac;
moving to another worker requires stopping this worker and copying the state.
Updated manual and scheduled worker modes share `output/acceptance-worker.lock`.
This lock prevents duplicate Acceptance processes on the same Mac, not other
Connect/Message/Reply workers using those browser profiles.

To stop the service without deleting its progress:

```sh
zsh git-meta/acceptance_schedule_service.sh uninstall
```

For manual foreground operation without the timetable:

```sh
.venv/bin/python3 -u outreach_acceptance_worker.py
```

Do not run the foreground command while the LaunchAgent is active.
