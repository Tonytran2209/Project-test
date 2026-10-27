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

Create an accepted-recipient snapshot even when name/template/company is not yet
available. Use the campaign template and verified personalization to render a
preview when possible; otherwise keep `message_text` null, never guess content.
The sending worker reads the actual first name from LinkedIn, and queue validation
still checks the template and required company before any send. Existing drafts, queued work,
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
silently recreate deleted drafts. The deletion is permanent for those draft snapshots; recovery requires
a database backup. Preparation of other newly accepted recipients is unaffected.

## Diagnostics

```sh
grep -E 'MESSAGES READY|Auto prepare' logs/acceptance.out.log logs/acceptance.err.log | tail -n 40
```

Missing SQL/schema permissions produce visible notification API errors and worker
preparation errors with retry. Acceptance results are still saved. This migration
must be applied before using the new UI; it is not applied automatically by git.

## Unified Messages workspace

Recipients is no longer a separate tab. Messages has one list; Ready,
Queued, Sending, Completed and Failed are status badges on its rows, not tabs.
Accepted recipients awaiting a snapshot also have Send messages: this action
creates the snapshot and opens the send modal, without queueing or sending until
the user confirms. There are no manual Prepare buttons or recipient
selection controls. Preparation still runs after each Acceptance check batch and
retries during idle periods. A legacy `recipients` navigation request opens the
merged workspace. The bell opens the matching batch's drawer in that same list.
This presentation merge requires no additional SQL beyond the migration above.

## Connect-week attribution correction

Message row dates, week filters, week totals and bell navigation use the original
source Connect job's `created_at`, never `accepted_at` or message-batch creation.
The API now includes this timestamp in `source_connect_ids`. Default selection
chooses the latest populated Connect week, including after initial empty loading;
explicit user-selected weeks remain unchanged. No stored timestamps are rewritten.

Reapply the updated `outreach_ready_batches.sql` to replace the preparation RPC's
old mandatory-name/template restrictions, then restart Acceptance after pulling.
The migration is idempotent. Previously accepted recipients without a captured
name will be snapshotted automatically during the next idle retry.
