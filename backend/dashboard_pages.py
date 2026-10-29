"""Explicit workspace URLs, sharing only the dashboard presentation shell."""
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, RedirectResponse

router = APIRouter()
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
WORKSPACES = ("connect", "acceptance", "messages", "replies", "campaigns")


def workspace_shell() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")


def dashboard_home() -> RedirectResponse:
    return RedirectResponse("/dashboard/connect", status_code=307)


# Register exact routes before StaticFiles; never capture asset names as pages.
router.add_api_route("/dashboard/", dashboard_home, methods=["GET"], include_in_schema=False)
for workspace in WORKSPACES:
    for suffix in ("", "/"):
        router.add_api_route(f"/dashboard/{workspace}{suffix}", workspace_shell,
                             methods=["GET"], include_in_schema=False)
