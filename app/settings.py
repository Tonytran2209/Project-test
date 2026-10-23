from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=False,
)


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_secret_key: str

    outreach_supabase_url: str
    outreach_supabase_secret_key: str


def get_required_env(name: str) -> str:
    value = os.getenv(
        name,
        "",
    ).strip()

    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


def load_settings() -> Settings:
    return Settings(
        supabase_url=get_required_env(
            "SUPABASE_URL"
        ),

        supabase_secret_key=get_required_env(
            "SUPABASE_SECRET_KEY"
        ),

        outreach_supabase_url=get_required_env(
            "OUTREACH_SUPABASE_URL"
        ),

        outreach_supabase_secret_key=get_required_env(
            "OUTREACH_SUPABASE_SECRET_KEY"
        ),

    )
