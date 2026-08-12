# ============================================================
# src/config.py
# ============================================================
# Purpose:
#   Loads all project settings from the .env file using the
#   python-dotenv library.  Every other module imports from
#   here, so API keys and paths are never hard-coded.
#
# Usage:
#   from src.config import settings
#   api_key = settings["YOUTUBE_API_KEY"]
# ============================================================

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Locate the project root (one level above this file) ─────
ROOT_DIR = Path(__file__).resolve().parent.parent

# ── Load .env file from the project root ────────────────────
# If .env doesn't exist the script still works; env vars
# already set in the shell will be used instead.
load_dotenv(ROOT_DIR / ".env")


def get_settings() -> dict:
    """
    Read all relevant environment variables and return them
    as a plain dictionary.

    Returns
    -------
    dict
        A dictionary with all project-level configuration values.
    """
    return {
        # YouTube API
        "YOUTUBE_API_KEY": os.getenv("YOUTUBE_API_KEY", ""),

        # Database
        "DATABASE_TYPE": os.getenv("DATABASE_TYPE", "sqlite").lower(),
        "SQLITE_DATABASE_PATH": ROOT_DIR / os.getenv(
            "SQLITE_DATABASE_PATH", "data/social_media.db"
        ),
        "MYSQL_HOST": os.getenv("MYSQL_HOST", "localhost"),
        "MYSQL_PORT": int(os.getenv("MYSQL_PORT", "3306")),
        "MYSQL_USER": os.getenv("MYSQL_USER", "root"),
        "MYSQL_PASSWORD": os.getenv("MYSQL_PASSWORD", ""),
        "MYSQL_DATABASE": os.getenv("MYSQL_DATABASE", "social_media_analytics"),

        # Paths
        "ROOT_DIR": ROOT_DIR,
        "RAW_DATA_PATH": ROOT_DIR / "data" / "raw" / "youtube_raw_data.csv",
        "PROCESSED_DATA_PATH": ROOT_DIR / "data" / "processed" / "youtube_cleaned_data.csv",
        "SAMPLE_DATA_PATH": ROOT_DIR / "data" / "sample" / "sample_youtube_data.csv",
        "REPORTS_DIR": ROOT_DIR / "reports",

        # Analysis
        "REPORTING_TIMEZONE": os.getenv("REPORTING_TIMEZONE", "Asia/Kolkata"),
        "MIN_SAMPLE_SIZE": int(os.getenv("MIN_SAMPLE_SIZE", "5")),
    }


# Module-level settings dictionary — import this directly
settings = get_settings()


def validate_api_key() -> bool:
    """
    Check whether a real YouTube API key has been configured.

    Returns True  → a non-placeholder key is present
    Returns False → key is missing or still set to the example value
    """
    key = settings["YOUTUBE_API_KEY"]
    placeholder_values = {"", "your_api_key_here"}
    return key not in placeholder_values


if __name__ == "__main__":
    # Quick sanity-check: run this file directly to see current settings
    import pprint
    cfg = get_settings()
    # Mask the API key before printing
    cfg["YOUTUBE_API_KEY"] = "***" if cfg["YOUTUBE_API_KEY"] else "(not set)"
    cfg["MYSQL_PASSWORD"] = "***" if cfg["MYSQL_PASSWORD"] else "(not set)"
    pprint.pprint(cfg)
