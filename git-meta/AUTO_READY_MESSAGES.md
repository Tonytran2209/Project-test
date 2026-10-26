# Acceptance → Ready Messages

## Deploy order

1. Run the complete `outreach_ready_batches.sql` in Supabase SQL Editor. This
   adds name/suppression fields, the persistent notification table, and atomic
   prepare/delete functions. It does not delete existing batches or send messages.
2. Deploy the updated backend and frontend together.
3. On the worker Mac, pull the update and restart Acceptance:

```sh
git pull origin main
zsh git-meta/acceptance_schedule_service.sh install
zsh git-meta/acceptance_schedule_service.sh status
```

No new worker process or schedule is required. Both manual and scheduled
Acceptance checks use the same hook; the existing 00:00 and backlog 06:00
rotation and original Connect-week attribution are unchanged.

## Preparation

After recording an accepted result, read the first name from the profile already
open in Acceptance and save it on that exact Connect target. After each batch,
prepare eligible unsent recipients, grouped by original Connect batch and campaign.
The idle worker retries preparation once a minute, including after missing
company data or campaign templates are corrected. It does not open LinkedIn
profiles just to prepare messages.

Use the campaign's latest saved message template, verified prospect/company data,
and the captured first name to store a rendered draft in `message_text`. Missing
name, template, or required company leaves the recipient in Recipients. Already
accepted historical recipients without a captured name remain there for manual
preparation; no names are guessed from URL slugs. Existing drafts, queued work,
and sent messages are not overwritten. Atomic SQL prevents retry duplicates and
creates the batch and its notification together. Automatic preparation never
queues or sends anything; the existing Queue & Send action is still explicit.

The bell polls every 15 seconds while the page is visible. New Ready notifications
refresh Messages, persist across reloads/devices, and open the selected batch's
snapshot drawer with rendered drafts. Opening marks a notification seen; it does
not change the message batch's status.

## Checkbox deletion

Select individual Ready message batches or Select all in the bell, then Delete
and confirm. The server locks and rechecks the entire selection in one transaction.
Only notification-linked `prepared` batches whose targets are all `prepared` can
be deleted. Missing, queued, processing, sent or otherwise changed batches reject
the entire deletion. Draft targets, their message batch and its notification are
deleted; original Connect jobs, acceptance records, prospects, and campaign data
are retained. No notification-only dismissal is offered.

Source recipients are marked `auto_message_dismissed` so later scans do not
silently recreate deleted drafts. They can still be prepared manually from
Recipients. The deletion is permanent for those draft snapshots; recovery requires
a database backup. Preparation of other newly accepted recipients is unaffected.

## Diagnostics

```sh
grep -E 'MESSAGES READY|Auto prepare' logs/acceptance.out.log logs/acceptance.err.log | tail -n 40
```

Missing SQL/schema permissions produce visible notification API errors and worker
preparation errors with retry. Acceptance results are still saved. This migration
must be applied before using the new UI; it is not applied automatically by git.
