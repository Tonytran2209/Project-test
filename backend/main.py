import json
import logging
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Request
from supabase import create_client
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.outreach_campaign_identity import campaign_id_for_name, connect_batch_label
from app.outreach_connect_input import prepare_connect_entries
from app.outreach_job_store import (
    MAX_CONNECT_URLS,
    OutreachJobStoreError,
    create_connect_job,
    list_connect_campaigns,
)
from app.outreach_dashboard_store import (
    OutreachDashboardStoreError,
    get_outreach_dashboard,
    get_outreach_profiles,
    get_outreach_rate_limits,
)

from app.outreach_acceptance_store import (
    OutreachAcceptanceStoreError,
    delete_connect_job_data,
    list_acceptance_check_history,
    queue_acceptance_check_run,
)

from app.outreach_acceptance_insights_store import (
    OutreachAcceptanceInsightsStoreError,
    get_acceptance_insights,
)

from app.outreach_accepted_pool_store import (
    OutreachAcceptedPoolStoreError,
    get_accepted_pool,
)

from app.outreach_message_preparation_store import (
    OutreachMessagePreparationStoreError,
    get_campaign_message_template_for_batch,
    get_message_preparation_candidates,
    get_prepared_message_batch,
    list_prepared_message_batches,
    prepare_all_unsent_accepted,
    prepare_selected_unsent_accepted,
    save_campaign_message_template_for_batch,
)

from app.outreach_campaign_performance_store import get_campaign_performance

from app.outreach_message_queue_store import (
    OutreachMessageQueueStoreError,
    queue_message_batch,
)

from app.outreach_session_status import (
    OutreachSessionStatusError,
    list_outreach_session_statuses,
    queue_outreach_session_checks,
)

from app.outreach_reply_store import (
    OutreachReplyStoreError,
    get_outreach_reply_revision,
    list_outreach_reply_accounts,
    list_outreach_reply_page,
    list_recent_outreach_replies,
)
from app.outreach_reply_check_requests import (
    get_latest_completed_reply_check,
    get_reply_check_request,
    request_reply_check,
)
from app.outreach_reply_send_store import (
    OutreachReplySendStoreError,
    list_reply_send_jobs,
    prepare_and_queue_reply_send,
    prepare_reply_send,
    queue_prepared_reply_send,
)
from app.outreach_worker_activity import get_outreach_worker_activity



# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(
    "linkedin-daily-scanner-api"
)


# =========================================================
# ENVIRONMENT VARIABLES
# =========================================================

LARK_APP_ID = os.getenv(
    "LARK_APP_ID",
    "",
).strip()

LARK_APP_SECRET = os.getenv(
    "LARK_APP_SECRET",
    "",
).strip()

LARK_VERIFICATION_TOKEN = os.getenv(
    "LARK_VERIFICATION_TOKEN",
    "",
).strip()

LARK_ENCRYPT_KEY = os.getenv(
    "LARK_ENCRYPT_KEY",
    "",
).strip()

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    "",
).strip()

SUPABASE_SECRET_KEY = os.getenv(
    "SUPABASE_SECRET_KEY",
    "",
).strip()


WORKER_COMMAND_TABLE = "linkedin_worker_commands"
ALLOWED_WORKER_COMMANDS = {
    "kill_current",
    "stop_scan",
    "resume_scan",
}


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="LinkedIn and YouTube Scanner API",
    description=(
        "Railway backend for LinkedIn scanning, "
        "YouTube research jobs, dashboard controls, "
        "and Lark commands."
    ),
    version="0.7.0",
)



# =========================================================
# FRONTEND DASHBOARD
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

if FRONTEND_DIR.exists():
    app.mount(
        "/dashboard",
        StaticFiles(
            directory=str(FRONTEND_DIR),
            html=True,
        ),
        name="dashboard",
    )
else:
    logger.warning(
        "Frontend directory not found: %s",
        FRONTEND_DIR,
    )


# =========================================================
# BASIC ROUTES
# =========================================================

@app.get("/")
def root() -> RedirectResponse:
    """
    Open the dashboard from the Railway root domain.
    """
    return RedirectResponse(
        url="/dashboard/",
        status_code=307,
    )


@app.get("/health")
def health_check() -> dict[str, Any]:
    """
    Basic Railway API health endpoint.

    This route only checks whether the API is running and
    whether the required environment variables are present.

    The full LinkedIn scanner health check is triggered from
    Lark with the command: health check
    """
    return {
        "status": "ok",
        "timestamp": (
            datetime
            .now(timezone.utc)
            .isoformat()
        ),
        "config": {
            "lark_app_id": bool(LARK_APP_ID),
            "lark_app_secret": bool(
                LARK_APP_SECRET
            ),
            "lark_verification_token": bool(
                LARK_VERIFICATION_TOKEN
            ),
            "lark_encrypt_key": bool(
                LARK_ENCRYPT_KEY
            ),
            "supabase_url": bool(
                SUPABASE_URL
            ),
            "supabase_secret_key": bool(
                SUPABASE_SECRET_KEY
            ),
        },
    }



# =========================================================
# WORKER CONTROL API
# =========================================================

@app.post("/api/worker/commands")
async def create_worker_command(
    request: Request,
) -> JSONResponse:
    """
    Queue a control command for the Mac worker.

    The browser cannot be controlled directly from Railway.
    Railway writes a command to Supabase; the local worker
    reads and acknowledges it.
    """
    return JSONResponse(
        status_code=410,
        content={
            "ok": False,
            "error": "LinkedIn Scanner has been removed",
        },
    )

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "Request body must be valid JSON",
            },
        )

    command = str(
        body.get("command") or ""
    ).strip()

    worker_id = str(
        body.get("worker_id") or ""
    ).strip()

    if command not in ALLOWED_WORKER_COMMANDS:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "Unsupported worker command",
                "allowed_commands": sorted(
                    ALLOWED_WORKER_COMMANDS
                ),
            },
        )

    if not worker_id:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "worker_id is required",
            },
        )

    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "error": "Supabase backend is not configured",
            },
        )

    try:
        client = create_client(
            SUPABASE_URL,
            SUPABASE_SECRET_KEY,
        )

        response = (
            client
            .table(WORKER_COMMAND_TABLE)
            .insert(
                {
                    "worker_id": worker_id,
                    "command": command,
                    "status": "pending",
                    "requested_at": (
                        datetime
                        .now(timezone.utc)
                        .isoformat()
                    ),
                }
            )
            .execute()
        )

        rows = list(response.data or [])

        if not rows:
            raise RuntimeError(
                "Supabase returned no command row"
            )

        command_row = rows[0]

    except Exception as exc:
        logger.exception(
            "Could not queue worker command"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "Could not queue worker command",
                "detail": str(exc),
            },
        )

    logger.warning(
        "WORKER COMMAND QUEUED | worker_id=%s | command=%s | command_id=%s",
        worker_id,
        command,
        command_row.get("id"),
    )

    return JSONResponse(
        status_code=202,
        content={
            "ok": True,
            "command": command_row,
        },
    )


# =========================================================
# YOUTUBE RESEARCH JOB API
# =========================================================

YOUTUBE_JOB_TABLE = "youtube_scan_jobs"


@app.post("/api/youtube/jobs", include_in_schema=False)
async def create_youtube_job(
    request: Request,
) -> JSONResponse:
    """
    Create one pending YouTube research job.

    The Railway backend only creates the queue row.
    The Mac YouTube worker claims and processes the job.
    """

    return JSONResponse(
        status_code=410,
        content={
            "ok": False,
            "error": "YouTube Research has been removed",
        },
    )

    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "error": "Supabase backend is not configured",
            },
        )

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "Request body must be valid JSON",
            },
        )

    keyword = str(
        body.get("keyword") or ""
    ).strip()

    try:
        max_results = int(
            body.get("max_results") or 40
        )
    except (
        TypeError,
        ValueError,
    ):
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "max_results must be an integer",
            },
        )

    filters = body.get("filters")

    if not isinstance(
        filters,
        dict,
    ):
        filters = {}

    if not keyword:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "keyword is required",
            },
        )

    max_results = max(
        1,
        min(
            max_results,
            40,
        ),
    )

    now = (
        datetime
        .now(timezone.utc)
        .isoformat()
    )

    try:
        client = create_client(
            SUPABASE_URL,
            SUPABASE_SECRET_KEY,
        )

        response = (
            client
            .table(YOUTUBE_JOB_TABLE)
            .insert(
                {
                    "keyword": keyword,
                    "status": "pending",
                    "current_stage": "queued",
                    "progress_percent": 0,
                    "max_results": max_results,
                    "filters": filters,
                    "retry_count": 0,
                    "result_count": 0,
                    "last_error": None,
                    "created_at": now,
                    "updated_at": now,
                }
            )
            .execute()
        )

        rows = list(
            response.data or []
        )

        if not rows:
            raise RuntimeError(
                "Supabase returned no YouTube job row"
            )

        job = rows[0]

    except Exception as exc:
        logger.exception(
            "Could not create YouTube research job"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "Could not create YouTube job",
                "detail": str(exc),
            },
        )

    logger.info(
        (
            "YOUTUBE JOB CREATED | "
            "job_id=%s | keyword=%s | max_results=%s"
        ),
        job.get("id"),
        keyword,
        max_results,
    )

    return JSONResponse(
        status_code=201,
        content={
            "ok": True,
            "job": job,
        },
    )

# =========================================================
# OUTREACH CONNECT JOB API
# =========================================================


@app.get("/api/outreach/connect/campaigns")
def get_outreach_connect_campaigns() -> JSONResponse:
    try:
        campaigns = list_connect_campaigns()
        return JSONResponse(content={
            "ok": True,
            "campaigns": campaigns,
            "campaign_records": [
                {"id": campaign_id_for_name(name), "name": name}
                for name in campaigns
            ],
        })
    except Exception:
        logger.exception("Could not list Connect campaigns")
        return JSONResponse(status_code=500, content={
            "ok": False,
            "error": "Could not load Connect campaigns",
        })


@app.post("/api/outreach/connect/jobs")
async def create_outreach_connect_job(
    request: Request,
) -> JSONResponse:
    """
    Create one LinkedIn Outreach Connect job.

    Flow:

    Website
    -> Railway API
    -> Outreach Supabase
    -> Mac Outreach worker

    Railway chỉ tạo job.
    Railway không chạy LinkedIn browser.
    """

    # -----------------------------------------------------
    # 1. READ JSON
    # -----------------------------------------------------

    try:
        body = await request.json()

    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": (
                    "Request body must be valid JSON"
                ),
            },
        )

    # -----------------------------------------------------
    # 2. READ URL LIST
    # -----------------------------------------------------

    urls = body.get(
        "urls"
    )

    if not isinstance(
        urls,
        list,
    ):
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": (
                    "urls must be a JSON array"
                ),
            },
        )

    company_names = body.get("company_names")
    try:
        entries = prepare_connect_entries(urls, company_names)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})
    cleaned_urls = [url for url, _ in entries]
    if company_names is not None:
        company_names = [name for _, name in entries]

    if not cleaned_urls:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": (
                    "At least one LinkedIn URL "
                    "is required"
                ),
            },
        )

    if len(cleaned_urls) > MAX_CONNECT_URLS:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": (
                    f"Maximum {MAX_CONNECT_URLS} LinkedIn profile URLs "
                    "per Connect job."
                ),
            },
        )

    # -----------------------------------------------------
    # 3. CREATE CONNECT JOB
    # -----------------------------------------------------

    display_name = body.get("campaign_name", body.get("display_name", ""))
    if not isinstance(display_name, str) or len(display_name.strip()) > 80:
        return JSONResponse(status_code=400, content={
            "ok": False,
            "error": "Campaign name must be text of at most 80 characters",
        })
    display_name = display_name.strip()
    if "campaign_name" in body and not display_name:
        return JSONResponse(status_code=400, content={
            "ok": False,
            "error": "Choose or create a Campaign before starting Connect",
        })

    batch_name = body.get("batch_name", "")
    if not isinstance(batch_name, str) or len(batch_name.strip()) > 80:
        return JSONResponse(status_code=400, content={
            "ok": False,
            "error": "Batch name must be text of at most 80 characters",
        })
    batch_name = batch_name.strip()

    try:
        result = create_connect_job(
            cleaned_urls,
            display_name=display_name,
            batch_name=batch_name,
            company_names=company_names,
        )

    except OutreachJobStoreError as exc:
        logger.exception(
            "Could not create Outreach Connect job"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Could not create "
                    "Outreach Connect job"
                ),
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Outreach Connect "
            "job error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Unexpected error while "
                    "creating Outreach Connect job"
                ),
                "detail": str(exc),
            },
        )

    # -----------------------------------------------------
    # 4. LOG
    # -----------------------------------------------------

    logger.info(
    (
        "OUTREACH CONNECT JOB CREATED | "
        "job_id=%s | "
        "job_code=%s | "
        "input=%s | "
        "targets=%s | "
        "duplicates=%s | "
        "invalid=%s"
    ),
    result.job_id,
    result.job_code,
    result.input_count,
    result.target_count,
    result.duplicate_count,
    result.invalid_count,
    )

    # -----------------------------------------------------
    # 5. RESPONSE
    # -----------------------------------------------------

    return JSONResponse(
        status_code=201,
        content={
            "ok": True,
            "job": {
                "job_id": result.job_id,
                "job_code": result.job_code,
                "batch_name": result.batch_name,
                "batch_label": connect_batch_label(result.batch_name, display_name, None),
                "display_name": display_name,
                "campaign_id": campaign_id_for_name(display_name),
                "connect_batch_id": result.job_id,
                "input_count": (
                    result.input_count
                ),
                "target_count": (
                    result.target_count
                ),
                "duplicate_count": (
                    result.duplicate_count
                ),
                "invalid_count": (
                    result.invalid_count
                ),
                "status": "pending",
            },
        },
    )


# =========================================================
# OUTREACH ACCEPTANCE CHECK API
# =========================================================


@app.delete(
    "/api/outreach/connect/jobs/{job_id}"
)
async def delete_outreach_connect_job_api(
    job_id: str,
) -> JSONResponse:
    """
    Permanently delete one completed Connect Job and its dependent data.
    """
    cleaned_job_id = str(
        job_id
        or ""
    ).strip()

    if not cleaned_job_id:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "job_id is required",
            },
        )

    try:
        deleted = delete_connect_job_data(
            source_job_id=cleaned_job_id,
        )

    except OutreachAcceptanceStoreError as exc:
        detail = str(exc)

        conflict = (
            "cannot be deleted" in detail
            or "active Acceptance Check" in detail
        )

        return JSONResponse(
            status_code=409 if conflict else 500,
            content={
                "ok": False,
                "error": "Could not delete Outreach Connect Job",
                "detail": detail,
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Outreach Connect Job delete error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Unexpected error while deleting "
                    "Outreach Connect Job"
                ),
                "detail": str(exc),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "deleted": deleted,
        },
    )


@app.get(
    "/api/outreach/connect/jobs/{job_id}/acceptance-checks"
)
async def get_outreach_acceptance_check_history_api(
    job_id: str,
) -> JSONResponse:
    """
    Return every Acceptance Check run for one Connect Job.

    Read-only endpoint used by the Acceptance tab history expander.
    """
    cleaned_job_id = str(
        job_id
        or ""
    ).strip()

    if not cleaned_job_id:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "job_id is required",
            },
        )

    try:
        runs = list_acceptance_check_history(
            source_job_id=cleaned_job_id,
        )

    except OutreachAcceptanceStoreError as exc:
        logger.exception(
            "Could not load Acceptance Check history"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Could not load Acceptance Check history"
                ),
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Acceptance Check history error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Unexpected error while loading "
                    "Acceptance Check history"
                ),
                "detail": str(exc),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "job_id": cleaned_job_id,
            "count": len(runs),
            "runs": runs,
        },
    )


@app.post(
    "/api/outreach/connect/jobs/{job_id}/check-acceptance"
)
async def create_outreach_acceptance_check(
    job_id: str,
) -> JSONResponse:
    """
    Queue one manual Acceptance Check for one Connect Job.

    Flow:

    Dashboard button
    -> Railway API
    -> outreach_acceptance_checks(status='pending')
    -> Mac Acceptance Worker claims the run
    -> LinkedIn browser checks the profiles

    Railway NEVER opens LinkedIn.
    """
    cleaned_job_id = str(
        job_id
        or ""
    ).strip()

    if not cleaned_job_id:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "job_id is required",
            },
        )

    try:
        check_run = (
            queue_acceptance_check_run(
                source_job_id=cleaned_job_id
            )
        )

    except OutreachAcceptanceStoreError as exc:
        logger.exception(
            "Could not queue Outreach Acceptance Check"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Could not queue "
                    "Outreach Acceptance Check"
                ),
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Outreach Acceptance Check error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Unexpected error while queueing "
                    "Outreach Acceptance Check"
                ),
                "detail": str(exc),
            },
        )

    logger.info(
        (
            "OUTREACH ACCEPTANCE CHECK QUEUED | "
            "source_job_id=%s | "
            "check_id=%s | "
            "run_number=%s | "
            "total_to_check=%s"
        ),
        cleaned_job_id,
        check_run.get("id"),
        check_run.get("run_number"),
        check_run.get("total_to_check"),
    )

    return JSONResponse(
        status_code=202,
        content={
            "ok": True,
            "acceptance_check": check_run,
        },
    )



# =========================================================
# OUTREACH ACCEPTED POOL API
# =========================================================


@app.get("/api/outreach/accepted-pool")
async def get_outreach_accepted_pool_api() -> JSONResponse:
    """
    Return the live Accepted Pool.

    The pool is derived directly from current Outreach data:
    - only acceptance_status == accepted;
    - deduplicated by prospect_id;
    - normalized_url is the fallback identity;
    - includes message status so frontend can separate:
        not sent / sent.

    No Accepted Pool rows are copied into a second table.
    Therefore every Acceptance Check becomes visible here on
    the next API read.
    """
    try:
        pool = (
            get_accepted_pool()
        )

    except OutreachAcceptedPoolStoreError as exc:
        logger.exception(
            "Could not load Outreach Accepted Pool"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Could not load "
                    "Outreach Accepted Pool"
                ),
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Outreach Accepted Pool error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Unexpected error while loading "
                    "Outreach Accepted Pool"
                ),
                "detail": str(exc),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "accepted_pool": pool,
        },
    )



# =========================================================
# OUTREACH MESSAGE PREPARATION API
# =========================================================


@app.get("/api/outreach/messages/preparation")
async def get_outreach_message_preparation_api() -> JSONResponse:
    """
    Preview the exact recipients that are currently eligible
    for a future message batch.

    IMPORTANT:
    This endpoint is READ-ONLY.

    It does not:
    - create a batch;
    - send a message;
    - start a worker;
    - change message_status.
    """
    try:
        result = (
            get_message_preparation_candidates()
        )

    except OutreachMessagePreparationStoreError as exc:
        logger.exception(
            "Could not load Outreach message preparation candidates"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Could not load Outreach "
                    "message preparation candidates"
                ),
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Outreach message preparation preview error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Unexpected error while loading "
                    "message preparation candidates"
                ),
                "detail": str(exc),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "preparation": result,
        },
    )



@app.get("/api/outreach/messages/batches")
async def list_outreach_message_batches_api() -> JSONResponse:
    """
    Read-only list of prepared message batches.
    """
    try:
        batches = (
            list_prepared_message_batches()
        )

    except OutreachMessagePreparationStoreError as exc:
        logger.exception(
            "Could not load Outreach message batches"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Could not load Outreach "
                    "message batches"
                ),
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Outreach message batch list error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Unexpected error while loading "
                    "Outreach message batches"
                ),
                "detail": str(exc),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "batches": batches,
        },
    )


@app.get("/api/outreach/messages/batches/{batch_id}")
async def get_outreach_message_batch_api(
    batch_id: str,
) -> JSONResponse:
    """
    Read-only detail view for one frozen recipient snapshot.
    """
    try:
        batch = (
            get_prepared_message_batch(
                batch_id
            )
        )

    except OutreachMessagePreparationStoreError as exc:
        logger.exception(
            "Could not load Outreach message batch"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Could not load Outreach "
                    "message batch"
                ),
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Outreach message batch detail error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Unexpected error while loading "
                    "Outreach message batch"
                ),
                "detail": str(exc),
            },
        )

    if batch is None:
        return JSONResponse(
            status_code=404,
            content={
                "ok": False,
                "error": (
                    "Message batch not found"
                ),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "batch": batch,
        },
    )



@app.get("/api/outreach/messages/batches/{batch_id}/template")
async def get_outreach_campaign_message_template_api(batch_id: str) -> JSONResponse:
    try:
        template = get_campaign_message_template_for_batch(batch_id)
    except OutreachMessagePreparationStoreError as exc:
        return JSONResponse(status_code=404, content={"ok": False, "detail": str(exc)})
    except Exception as exc:
        logger.exception("Could not load campaign message template")
        return JSONResponse(status_code=500, content={"ok": False, "detail": str(exc)})
    return JSONResponse(status_code=200, content={"ok": True, "template": template})


@app.post("/api/outreach/messages/batches/{batch_id}/template")
async def save_outreach_campaign_message_template_api(
    batch_id: str, request: Request
) -> JSONResponse:
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    message_template = (
        str(payload.get("message_template") or "")
        if isinstance(payload, dict) else ""
    )
    if not message_template.strip():
        return JSONResponse(
            status_code=400,
            content={"ok": False, "detail": "Message template cannot be empty."},
        )
    try:
        template = save_campaign_message_template_for_batch(
            batch_id, message_template
        )
    except OutreachMessagePreparationStoreError as exc:
        return JSONResponse(status_code=409, content={"ok": False, "detail": str(exc)})
    except Exception as exc:
        logger.exception("Could not save campaign message template")
        return JSONResponse(status_code=500, content={"ok": False, "detail": str(exc)})
    return JSONResponse(status_code=200, content={"ok": True, "template": template})


@app.post(
    "/api/outreach/messages/batches/{batch_id}/queue"
)
async def queue_outreach_message_batch_api(
    batch_id: str,
    request: Request,
) -> JSONResponse:
    """
    Queue one prepared message batch for the Mac Message Worker.

    Railway only writes:
        prepared -> queued

    Railway NEVER opens LinkedIn and NEVER sends the message itself.
    """

    cleaned_batch_id = str(
        batch_id
        or ""
    ).strip()

    if not cleaned_batch_id:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "batch_id is required",
            },
        )

    try:
        payload = await request.json()

    except Exception:
        payload = {}

    message_template = str(
        (
            payload
            if isinstance(
                payload,
                dict,
            )
            else {}
        ).get(
            "message_template",
            "",
        )
        or ""
    ).strip()

    if not message_template:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "message_template is required",
            },
        )

    try:
        queued_batch = queue_message_batch(
            batch_id=cleaned_batch_id,
            message_template=message_template,
        )

    except OutreachMessageQueueStoreError as exc:
        logger.exception(
            "Could not queue Outreach message batch"
        )

        return JSONResponse(
            status_code=409,
            content={
                "ok": False,
                "error": (
                    "Could not queue Outreach message batch"
                ),
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Outreach message queue error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Unexpected error while queueing "
                    "Outreach message batch"
                ),
                "detail": str(exc),
            },
        )

    logger.info(
        (
            "OUTREACH MESSAGE BATCH QUEUED | "
            "batch_id=%s | "
            "batch_code=%s | "
            "targets=%s"
        ),
        cleaned_batch_id,
        queued_batch.get(
            "batch_code"
        ),
        queued_batch.get(
            "prepared_target_count"
        ),
    )

    return JSONResponse(
        status_code=202,
        content={
            "ok": True,
            "batch": queued_batch,
        },
    )


@app.post("/api/outreach/messages/prepare-selected")
async def prepare_selected_outreach_messages_api(
    request: Request,
) -> JSONResponse:
    """
    Snapshot only selected currently eligible accepted users
    into prepared message batches grouped by source Connect batch.

    This endpoint does NOT send LinkedIn messages.
    """

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    prospect_ids = (
        payload.get("prospect_ids", [])
        if isinstance(payload, dict)
        else []
    )

    if not isinstance(prospect_ids, list):
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "prospect_ids must be a list",
            },
        )

    try:
        result = prepare_selected_unsent_accepted(
            prospect_ids=prospect_ids
        )

    except OutreachMessagePreparationStoreError as exc:
        logger.exception(
            "Could not prepare selected Outreach message recipients"
        )

        return JSONResponse(
            status_code=409,
            content={
                "ok": False,
                "error": "Could not prepare selected recipients",
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected selected message preparation error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Unexpected error while preparing "
                    "selected recipients"
                ),
                "detail": str(exc),
            },
        )

    batch = result.get("batch") or {}

    logger.info(
        (
            "OUTREACH SELECTED MESSAGE BATCH PREPARED | "
            "batch_id=%s | "
            "batch_code=%s | "
            "target_count=%s"
        ),
        batch.get("id"),
        batch.get("batch_code"),
        result.get("target_count", 0),
    )

    return JSONResponse(
        status_code=201,
        content={
            "ok": True,
            "created": bool(result.get("created")),
            "batch": batch,
            "batches": result.get("batches", []),
            "target_count": result.get("target_count", 0),
        },
    )


@app.post("/api/outreach/messages/prepare-all")
async def prepare_all_outreach_messages_api() -> JSONResponse:
    """
    Snapshot ALL currently eligible accepted + not-sent users
    into separate prepared message batches per source Connect batch.

    IMPORTANT:
    This endpoint still does NOT send any LinkedIn message.

    It only creates:
    - outreach_message_batches
    - outreach_message_targets
    """
    try:
        result = (
            prepare_all_unsent_accepted()
        )

    except OutreachMessagePreparationStoreError as exc:
        logger.exception(
            "Could not prepare Outreach message batch"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Could not prepare "
                    "Outreach message batch"
                ),
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Outreach message preparation error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Unexpected error while preparing "
                    "Outreach message batch"
                ),
                "detail": str(exc),
            },
        )

    if not result.get(
        "created"
    ):
        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "created": False,
                "reason": (
                    result.get(
                        "reason"
                    )
                ),
                "batch": None,
                "batches": [],
                "target_count": 0,
            },
        )

    batch = (
        result.get(
            "batch"
        )
        or {}
    )

    logger.info(
        (
            "OUTREACH MESSAGE BATCH PREPARED | "
            "batch_id=%s | "
            "batch_code=%s | "
            "target_count=%s"
        ),
        batch.get(
            "id"
        ),
        batch.get(
            "batch_code"
        ),
        result.get(
            "target_count"
        ),
    )

    return JSONResponse(
        status_code=201,
        content={
            "ok": True,
            "created": True,
            "batch": batch,
            "batches": result.get("batches", []),
            "target_count": (
                result.get(
                    "target_count",
                    0,
                )
            ),
        },
    )





# =========================================================
# OUTREACH LINKEDIN SESSION STATUS API
# =========================================================


@app.get("/api/outreach/sessions")
async def get_outreach_sessions_api() -> JSONResponse:
    try:
        accounts = list_outreach_session_statuses()
    except OutreachSessionStatusError as exc:
        logger.exception("Could not load Outreach session statuses")
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "Could not load Outreach session statuses",
                "detail": str(exc),
            },
        )
    except Exception as exc:
        logger.exception("Unexpected Outreach session status error")
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "Unexpected Outreach session status error",
                "detail": str(exc),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "count": len(accounts),
            "accounts": accounts,
        },
    )


@app.post("/api/outreach/sessions/check")
async def queue_outreach_sessions_check_api(
    request: Request,
) -> JSONResponse:
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    raw_account_ids = payload.get("account_ids")
    account_ids = None

    if raw_account_ids is not None:
        if not isinstance(raw_account_ids, list):
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": "account_ids must be an array.",
                },
            )

        account_ids = [
            str(value or "").strip()
            for value in raw_account_ids
        ]

    try:
        accounts = queue_outreach_session_checks(
            account_ids=account_ids
        )
    except OutreachSessionStatusError as exc:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": "Could not queue Outreach session checks",
                "detail": str(exc),
            },
        )
    except Exception as exc:
        logger.exception("Unexpected Outreach session queue error")
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "Unexpected Outreach session queue error",
                "detail": str(exc),
            },
        )

    return JSONResponse(
        status_code=202,
        content={
            "ok": True,
            "queued": True,
            "accounts": accounts,
        },
    )


# =========================================================
# OUTREACH PROFILES API
# =========================================================


@app.get("/api/outreach/profiles")
async def get_outreach_profiles_api() -> JSONResponse:
    """
    Load sent Outreach profiles on demand.

    This endpoint is intentionally separate from /api/outreach/dashboard
    to avoid transferring profile rows on every dashboard polling cycle.
    """
    try:
        profiles = get_outreach_profiles()

    except OutreachDashboardStoreError as exc:
        logger.exception(
            "Could not load Outreach Profiles"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "Could not load Outreach Profiles",
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Outreach Profiles error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "Unexpected Outreach Profiles error",
                "detail": str(exc),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "count": len(profiles),
            "profiles": profiles,
        },
    )


# =========================================================
# OUTREACH RATE LIMITS API
# =========================================================


@app.get("/api/outreach/rate-limits")
async def get_outreach_rate_limits_api() -> JSONResponse:
    """
    Load detailed Rate Limits only when the drawer is opened.
    """
    try:
        rate_limits = get_outreach_rate_limits()

    except OutreachDashboardStoreError as exc:
        logger.exception(
            "Could not load Outreach Rate Limits"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "Could not load Outreach Rate Limits",
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Outreach Rate Limits error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "Unexpected Outreach Rate Limits error",
                "detail": str(exc),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "rate_limits": rate_limits,
        },
    )


# =========================================================
# OUTREACH ACCEPTANCE INSIGHTS API
# =========================================================


@app.get("/api/outreach/acceptance-insights")
async def get_outreach_acceptance_insights_api(
    job_id: str | None = None,
    week_start: str | None = None,
) -> JSONResponse:
    """
    Read-only aggregate of Connect -> Acceptance performance.

    Query:
        no job_id
            -> All-time

        ?job_id=<outreach_jobs.id>
            -> one Connect Job

        ?week_start=YYYY-MM-DD
            -> one Monday-Sunday week

    Railway only reads Outreach Supabase.
    It never opens LinkedIn or runs a worker here.
    """
    cleaned_job_id = str(
        job_id
        or ""
    ).strip()

    cleaned_week_start = str(
        week_start
        or ""
    ).strip()

    if (
        cleaned_job_id
        and cleaned_week_start
    ):
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": (
                    "Use either job_id or week_start, "
                    "not both."
                ),
            },
        )

    try:
        insights = (
            get_acceptance_insights(
                job_id=(
                    cleaned_job_id
                    or None
                ),
                week_start=(
                    cleaned_week_start
                    or None
                ),
            )
        )

    except OutreachAcceptanceInsightsStoreError as exc:
        logger.exception(
            "Could not load Outreach Acceptance Insights"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Could not load Outreach "
                    "Acceptance Insights"
                ),
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Outreach Acceptance Insights error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Unexpected error while loading "
                    "Outreach Acceptance Insights"
                ),
                "detail": str(exc),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "insights": insights,
        },
    )


# =========================================================
# OUTREACH REPLIES API
# =========================================================


@app.get("/api/outreach/replies")
async def list_outreach_replies_api(
    limit: int = 50,
    account_id: str | None = None,
    offset: int = 0,
    metadata: bool = False,
    revision_only: bool = False,
) -> JSONResponse:
    """Read account metadata or one scrollable page of conversations."""

    try:
        latest_scan = (
            get_latest_completed_reply_check()
            if revision_only or metadata or account_id else None
        )
        active_since = str((latest_scan or {}).get("started_at") or "") or None
        scan_id = str((latest_scan or {}).get("id") or "")
        if revision_only:
            reply_revision = get_outreach_reply_revision(active_since=active_since)
            return JSONResponse(content={
                "ok": True,
                "revision": f"{scan_id}:{reply_revision or ''}",
            })
        if metadata:
            replies = []
            accounts = list_outreach_reply_accounts(
                include_counts=True, active_since=active_since,
            )
            reply_revision = get_outreach_reply_revision(active_since=active_since)
            revision = f"{scan_id}:{reply_revision or ''}"
            page = None
        elif account_id:
            page = list_outreach_reply_page(
                account_id=account_id, offset=offset, limit=limit,
                active_since=active_since,
            )
            replies = page["replies"]
            accounts = []
            revision = None
        else:
            # Preserve the original response for older dashboard clients.
            replies = list_recent_outreach_replies(limit=limit)
            accounts = list_outreach_reply_accounts()
            revision = None
            page = None
        send_jobs = list_reply_send_jobs(
            [str(reply.get("id") or "") for reply in replies]
        )
        for reply in replies:
            reply["send_job"] = send_jobs.get(str(reply.get("id") or ""))
    except OutreachReplyStoreError as exc:
        logger.exception("Could not load Outreach replies")
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "Could not load Outreach replies",
                "detail": str(exc),
            },
        )
    except Exception as exc:
        logger.exception("Unexpected Outreach replies error")
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "Unexpected error while loading Outreach replies",
                "detail": str(exc),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "count": len(replies),
            "replies": replies,
            "accounts": accounts,
            "revision": revision,
            "has_more": page["has_more"] if page else False,
            "next_offset": page["next_offset"] if page else None,
        },
    )


@app.post("/api/outreach/reply-check")
async def request_outreach_reply_check_api() -> JSONResponse:
    try:
        request = request_reply_check()
    except Exception as exc:
        logger.exception("Could not queue a manual Outreach reply check")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(exc)},
        )
    return JSONResponse(
        status_code=202,
        content={"ok": True, "request": request},
    )


@app.get("/api/outreach/reply-check/latest")
async def get_latest_outreach_reply_check_api() -> JSONResponse:
    try:
        last_scan = get_latest_completed_reply_check()
    except Exception:
        logger.exception("Could not load last reply-check time")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": "Could not load last reply-check time"},
        )
    return JSONResponse(content={"ok": True, "last_scan": last_scan})


@app.get("/api/outreach/reply-check/{request_id}")
async def get_outreach_reply_check_request_api(request_id: str) -> JSONResponse:
    try:
        request = get_reply_check_request(request_id)
    except Exception as exc:
        logger.exception("Could not load manual reply-check status")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(exc)},
        )
    if not request:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Request not found"})
    return JSONResponse(content={"ok": True, "request": request})


@app.put("/api/outreach/replies/{reply_id}/prepare-send")
async def prepare_outreach_reply_send_api(
    reply_id: str,
    request: Request,
) -> JSONResponse:
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    message_text = str(
        (payload if isinstance(payload, dict) else {}).get("message_text") or ""
    ).strip()
    if not message_text:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "message_text is required"},
        )

    try:
        job = prepare_reply_send(
            reply_id=reply_id,
            message_text=message_text,
        )
    except OutreachReplySendStoreError as exc:
        return JSONResponse(
            status_code=409,
            content={"ok": False, "error": str(exc)},
        )
    except Exception as exc:
        logger.exception("Could not prepare Outreach reply send")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(exc)},
        )

    return JSONResponse(content={"ok": True, "job": job})


@app.post("/api/outreach/replies/{reply_id}/queue-send")
async def queue_outreach_reply_send_api(reply_id: str) -> JSONResponse:
    try:
        job = queue_prepared_reply_send(reply_id=reply_id)
    except OutreachReplySendStoreError as exc:
        return JSONResponse(
            status_code=409,
            content={"ok": False, "error": str(exc)},
        )
    except Exception as exc:
        logger.exception("Could not queue Outreach reply send")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(exc)},
        )

    return JSONResponse(content={"ok": True, "job": job})


@app.post("/api/outreach/replies/{reply_id}/send")
async def send_outreach_reply_api(
    reply_id: str,
    request: Request,
) -> JSONResponse:
    """Save one customized reply and immediately queue it for its account worker."""

    try:
        payload = await request.json()
    except Exception:
        payload = {}
    message_text = str(
        (payload if isinstance(payload, dict) else {}).get("message_text") or ""
    ).strip()
    if not message_text:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "message_text is required"},
        )

    try:
        job = prepare_and_queue_reply_send(
            reply_id=reply_id,
            message_text=message_text,
        )
    except OutreachReplySendStoreError as exc:
        return JSONResponse(
            status_code=409,
            content={"ok": False, "error": str(exc)},
        )
    except Exception as exc:
        logger.exception("Could not queue customized Outreach reply")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(exc)},
        )

    return JSONResponse(content={"ok": True, "job": job})


# =========================================================
# OUTREACH DASHBOARD API
# =========================================================


@app.get("/api/outreach/campaigns/performance")
async def get_outreach_campaign_performance_api(window: str = "all") -> JSONResponse:
    if window not in ("1d", "7d", "30d", "all"):
        return JSONResponse(status_code=400, content={"ok": False, "error": "Invalid timeframe"})
    try:
        campaigns = get_campaign_performance(window)
    except Exception:
        logger.exception("Could not load campaign performance")
        return JSONResponse(status_code=500, content={"ok": False, "error": "Could not load campaign performance"})
    return JSONResponse(content={"ok": True, "window": window, "campaigns": campaigns})


@app.get("/api/outreach/worker-activity")
async def get_outreach_worker_activity_api() -> JSONResponse:
    try:
        activity = get_outreach_worker_activity()
    except Exception:
        logger.exception("Could not load Outreach worker activity")
        return JSONResponse(status_code=500, content={"ok": False, "error": "Could not load worker activity"})
    return JSONResponse(content={"ok": True, "activity": activity})


@app.get("/api/outreach/dashboard")
async def get_outreach_dashboard_api() -> JSONResponse:
    """
    Dashboard data cho LinkedIn Outreach.

    Frontend dùng endpoint này để đọc:

    - current Connect job
    - progress
    - counters
    - scheduler/account quota
    - Outreach accounts
    - recent jobs
    """

    try:
        dashboard = (
            get_outreach_dashboard()
        )

    except OutreachDashboardStoreError as exc:
        logger.exception(
            "Could not load Outreach dashboard"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Could not load "
                    "Outreach dashboard"
                ),
                "detail": str(exc),
            },
        )

    except Exception as exc:
        logger.exception(
            "Unexpected Outreach dashboard error"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Unexpected error while "
                    "loading Outreach dashboard"
                ),
                "detail": str(exc),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "dashboard": dashboard,
        },
    )
# =========================================================
# LARK WEBHOOK
# =========================================================

@app.post("/webhooks/lark/events")
async def receive_lark_event(
    request: Request,
) -> JSONResponse:
    """
    Nhận text message từ Lark.

    Flow:
    1. Nhận và validate webhook.
    2. Lấy text, chat ID và sender ID.
    3. Kiểm tra command health check.
    4. Nếu là command:
       - đọc trạng thái toàn hệ thống;
       - gửi báo cáo về đúng chat Lark;
       - dừng flow URL.
    5. Nếu không phải command:
       - tách LinkedIn URL;
       - áp dụng gateway tối đa 10 URL;
       - lưu URL vào Supabase;
       - Mac worker xử lý queue sau đó.

    Railway không trực tiếp chạy LinkedIn browser.
    """

    return JSONResponse(
        status_code=410,
        content={
            "ok": False,
            "error": "LinkedIn Scanner has been removed",
        },
    )

    # -----------------------------------------------------
    # 1. READ JSON PAYLOAD
    # -----------------------------------------------------

    try:
        payload: dict[str, Any] = (
            await request.json()
        )
    except Exception:
        logger.exception(
            "Cannot parse request body as JSON"
        )

        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": (
                    "Request body must be valid JSON"
                ),
            },
        )

    logger.info(
        "LARK EVENT RECEIVED:\n%s",
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
    )

    # -----------------------------------------------------
    # 2. LARK URL VERIFICATION
    # -----------------------------------------------------

    if payload.get("type") == "url_verification":
        challenge = payload.get("challenge")

        if not challenge:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": "Missing challenge",
                },
            )

        incoming_token = payload.get("token")

        if (
            LARK_VERIFICATION_TOKEN
            and incoming_token
            and incoming_token
            != LARK_VERIFICATION_TOKEN
        ):
            logger.warning(
                "Invalid Lark verification token"
            )

            return JSONResponse(
                status_code=401,
                content={
                    "ok": False,
                    "error": (
                        "Invalid verification token"
                    ),
                },
            )

        logger.info(
            "Lark URL verification successful"
        )

        return JSONResponse(
            status_code=200,
            content={
                "challenge": challenge,
            },
        )

    # -----------------------------------------------------
    # 3. CHECK EVENT TYPE
    # -----------------------------------------------------

    header = payload.get("header") or {}
    event_type = header.get("event_type")

    if event_type != "im.message.receive_v1":
        logger.info(
            "Ignored event type: %s",
            event_type,
        )

        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "ignored": True,
                "event_type": event_type,
            },
        )

    # -----------------------------------------------------
    # 4. EXTRACT MESSAGE DATA
    # -----------------------------------------------------

    event = payload.get("event") or {}
    sender = event.get("sender") or {}
    sender_id = sender.get("sender_id") or {}
    message = event.get("message") or {}

    sender_type = sender.get("sender_type")
    open_id = sender_id.get("open_id")

    message_id = message.get("message_id")
    chat_id = message.get("chat_id")
    chat_type = message.get("chat_type")
    message_type = message.get("message_type")

    # -----------------------------------------------------
    # 5. ONLY ACCEPT USER TEXT MESSAGES
    # -----------------------------------------------------

    if sender_type and sender_type != "user":
        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "ignored": True,
                "reason": "sender_is_not_user",
            },
        )

    if message_type != "text":
        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "ignored": True,
                "reason": (
                    "unsupported_message_type"
                ),
            },
        )

    # -----------------------------------------------------
    # 6. PARSE MESSAGE TEXT
    # -----------------------------------------------------

    raw_content = message.get("content") or "{}"
    text = ""

    try:
        parsed_content = json.loads(raw_content)
        text = str(
            parsed_content.get("text", "")
        ).strip()
    except json.JSONDecodeError:
        logger.warning(
            "Cannot parse Lark content: %s",
            raw_content,
        )

    logger.info(
        (
            "LARK TEXT MESSAGE | "
            "open_id=%s | "
            "message_id=%s | "
            "chat_id=%s | "
            "chat_type=%s | "
            "text=%s"
        ),
        open_id,
        message_id,
        chat_id,
        chat_type,
        text,
    )

    # -----------------------------------------------------
    # 7. CHECK LARK COMMANDS BEFORE URL PARSING
    # -----------------------------------------------------

    try:
        command_result = handle_lark_command(
            text=text,
            chat_id=chat_id,
        )

    except Exception as exc:
        logger.exception(
            (
                "Could not process Lark command | "
                "message_id=%s | "
                "chat_id=%s"
            ),
            message_id,
            chat_id,
        )

        # Return 200 so Lark does not repeatedly resend
        # the same event and create duplicate bot messages.
        return JSONResponse(
            status_code=200,
            content={
                "ok": False,
                "message_received": True,
                "command_handled": False,
                "reason": (
                    "lark_command_processing_failed"
                ),
                "message_id": message_id,
                "open_id": open_id,
                "error": str(exc),
            },
        )

    if command_result.handled:
        logger.info(
            (
                "LARK COMMAND COMPLETED | "
                "command=%s | "
                "message_id=%s | "
                "chat_id=%s | "
                "response_message_id=%s"
            ),
            command_result.command,
            message_id,
            chat_id,
            command_result.message_id,
        )

        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "message_received": True,
                "command_handled": True,
                "command": command_result.command,
                "message_id": message_id,
                "response_message_id": (
                    command_result.message_id
                ),
            },
        )

    # -----------------------------------------------------
    # 8. EXTRACT LINKEDIN URLS + APPLY GATEWAY
    # -----------------------------------------------------

    try:
        max_urls_per_request = (
            get_max_urls_per_request()
        )

        linkedin_urls = (
            extract_linkedin_urls_with_limit(
                text
            )
        )

    except LinkedInUrlLimitError as exc:
        logger.warning(
            (
                "LINKEDIN URL REQUEST REJECTED | "
                "open_id=%s | "
                "message_id=%s | "
                "found_count=%s | "
                "max_count=%s"
            ),
            open_id,
            message_id,
            exc.found_count,
            exc.max_count,
        )

        # HTTP 200 prevents Lark from retrying the event.
        # No URL is inserted before this gateway passes.
        return JSONResponse(
            status_code=200,
            content={
                "ok": False,
                "message_received": True,
                "urls_inserted": False,
                "reason": (
                    "linkedin_url_limit_exceeded"
                ),
                "message_id": message_id,
                "open_id": open_id,
                "found_count": exc.found_count,
                "max_count": exc.max_count,
                "error": (
                    "Too many LinkedIn URLs in "
                    "one message."
                ),
            },
        )

    except ValueError as exc:
        logger.exception(
            "Invalid LinkedIn URL gateway configuration"
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "message_received": True,
                "urls_inserted": False,
                "reason": (
                    "invalid_url_gateway_configuration"
                ),
                "error": str(exc),
            },
        )

    logger.info(
        (
            "LARK MESSAGE PARSED | "
            "open_id=%s | "
            "message_id=%s | "
            "chat_id=%s | "
            "chat_type=%s | "
            "url_count=%s | "
            "max_urls_per_request=%s | "
            "urls=%s"
        ),
        open_id,
        message_id,
        chat_id,
        chat_type,
        len(linkedin_urls),
        max_urls_per_request,
        json.dumps(
            linkedin_urls,
            ensure_ascii=False,
        ),
    )

    if not linkedin_urls:
        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "message_received": True,
                "urls_inserted": False,
                "reason": (
                    "no_linkedin_urls_found"
                ),
                "message_id": message_id,
                "open_id": open_id,
                "url_count": 0,
                "max_urls_per_request": (
                    max_urls_per_request
                ),
            },
        )

    # -----------------------------------------------------
    # 9. INSERT URLS INTO THE SHARED SUPABASE DATABASE
    # -----------------------------------------------------

    try:
        result = insert_new_linkedin_urls(
            linkedin_urls,
            chat_id=chat_id,
            message_id=message_id,
            sender_open_id=open_id,
        )

    except Exception as exc:
        logger.exception(
            (
                "Could not insert LinkedIn URLs "
                "into Supabase"
            )
        )

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": (
                    "Could not insert LinkedIn URLs"
                ),
                "detail": str(exc),
            },
        )

    inserted_urls = [
        row.get("linkedin_url")
        for row in result.inserted
        if row.get("linkedin_url")
    ]

    logger.info(
        (
            "LINKEDIN SOURCES UPDATED | "
            "message_id=%s | "
            "inserted_count=%s | "
            "existing_count=%s | "
            "inserted_urls=%s"
        ),
        message_id,
        result.inserted_count,
        result.existing_count,
        json.dumps(
            inserted_urls,
            ensure_ascii=False,
        ),
    )

    # -----------------------------------------------------
    # 10. RESPONSE TO LARK WEBHOOK
    # -----------------------------------------------------

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "message_received": True,
            "message_id": message_id,
            "open_id": open_id,
            "received_url_count": len(
                linkedin_urls
            ),
            "max_urls_per_request": (
                max_urls_per_request
            ),
            "inserted_count": (
                result.inserted_count
            ),
            "existing_count": (
                result.existing_count
            ),
            "inserted_urls": inserted_urls,
            "existing_urls": (
                result.existing_urls
            ),
        },
    )
