"""Adapt a scheduled Connect week to the existing, unchanged Acceptance checker."""
from __future__ import annotations

from datetime import datetime, timedelta

from app.outreach_acceptance_schedule import VIETNAM
from app.outreach_acceptance_store import (
    ACCEPTANCE_CHECK_TABLE, JOB_TABLE, create_acceptance_check_run,
    load_acceptance_targets,
)

BATCH_GAP_SECONDS = 20 * 60


def _vietnam_boundary(value: str) -> str:
    return datetime.fromisoformat(value).replace(tzinfo=VIETNAM).isoformat()


# @feature acceptance
def scan_connect_week(worker, week: dict, checkpoint) -> bool | None:
    """Read batches by original created_at, then invoke the manual check path.

    Per-batch checkpoints survive restarts; no Connect/message action is invoked.
    Failed batches retain their place for a later slot. Existing manual runs are
    allowed to finish instead of creating another check for the same batch.
    Return None while waiting for the persisted 20-minute inter-batch deadline.
    """
    client = worker.client
    progress = week["progress"]
    if "jobs" not in progress:
        jobs, offset = [], 0
        while True:
            rows = (client.table(JOB_TABLE).select("id,created_at")
                    .gte("created_at", _vietnam_boundary(week["start"]))
                    .lt("created_at", _vietnam_boundary(week["end"]))
                    .order("created_at").order("id").range(offset, offset + 499).execute().data or [])
            jobs.extend(str(row["id"]) for row in rows)
            if len(rows) < 500:
                break
            offset += 500
        progress.update(jobs=jobs, done=[], run=None)
        checkpoint()

    for job_id in progress["jobs"]:
        if worker._stop_requested:
            return False
        if job_id in progress["done"]:
            continue
        next_batch_at = progress.get('next_batch_at')
        if next_batch_at and datetime.now(VIETNAM) < datetime.fromisoformat(next_batch_at):
            return None
        saved = progress.get("run")
        if saved and saved["job_id"] == job_id:
            rows = (client.table(ACCEPTANCE_CHECK_TABLE).select("id,status,failed_count")
                    .eq("id", saved["id"]).execute().data or [])
            if rows and rows[0]["status"] == "completed" and not rows[0].get("failed_count"):
                progress["done"].append(job_id)
                progress["run"] = None
                progress.setdefault('next_batch_at', (datetime.now(VIETNAM) + timedelta(seconds=BATCH_GAP_SECONDS)).isoformat())
                checkpoint()
                continue
            if rows and rows[0]["status"] == "running":
                # Only this locked process owns scheduled runs; this is a crash recovery.
                client.table(ACCEPTANCE_CHECK_TABLE).update({
                    "status": "failed",
                }).eq("id", saved["id"]).execute()
            progress["run"] = None
            checkpoint()

        existing = (client.table(ACCEPTANCE_CHECK_TABLE).select("id,status")
                    .eq("source_job_id", job_id).in_("status", ["pending", "running"])
                    .limit(1).execute().data or [])
        if existing:
            print(f"ACCEPTANCE SCHEDULE | deferred existing run | batch={job_id}", flush=True)
            return False
        targets = load_acceptance_targets(source_job_id=job_id, client=client)
        if targets:
            run = create_acceptance_check_run(source_job_id=job_id,
                                             total_to_check=len(targets), status="running", client=client)
            progress["run"] = {"id": str(run["id"]), "job_id": job_id}
            progress.pop('next_batch_at', None)
            checkpoint()
            try:
                worker._process_check_run(run)
            finally:
                progress['next_batch_at'] = (datetime.now(VIETNAM) + timedelta(seconds=BATCH_GAP_SECONDS)).isoformat()
                checkpoint()
                print(f"ACCEPTANCE SCHEDULE | batch={job_id} | next_batch_at={progress['next_batch_at']} | gap_minutes=20", flush=True)
            rows = (client.table(ACCEPTANCE_CHECK_TABLE).select("status,failed_count")
                    .eq("id", run["id"]).execute().data or [])
            if not rows or rows[0]["status"] != "completed" or rows[0].get("failed_count"):
                return False
        progress["done"].append(job_id)
        progress["run"] = None
        checkpoint()
    return True
