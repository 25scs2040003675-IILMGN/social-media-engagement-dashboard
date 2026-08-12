# ============================================================
# src/utils.py
# ============================================================
# Purpose:
#   Shared helper functions used across the project.
#   Keeping these here avoids repeating the same code in
#   multiple files (DRY — Don't Repeat Yourself).
#
# Includes:
#   • parse_iso8601_duration  — convert "PT4M13S" → seconds
#   • get_logger              — consistent logging format
#   • ensure_directory        — create folder if it doesn't exist
#   • safe_int                — convert any value to int safely
# ============================================================

import re
import logging
import sys
from pathlib import Path


# ── Logger factory ──────────────────────────────────────────
def get_logger(name: str = "social_media") -> logging.Logger:
    """
    Create (or retrieve) a logger with a consistent format.

    Parameters
    ----------
    name : str
        Logger name (usually the calling module's __name__).

    Returns
    -------
    logging.Logger
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Only add a handler once — avoids duplicate messages
        # Use UTF-8 encoding explicitly to avoid cp1252 issues on Windows
        import io
        stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace') \
            if hasattr(sys.stdout, 'buffer') else sys.stdout
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.DEBUG)
        handler.stream = stream  # ensure the wrapper is used
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


# ── Directory helper ─────────────────────────────────────────
def ensure_directory(path) -> Path:
    """
    Create a directory (and all parent directories) if it
    doesn't already exist.

    Parameters
    ----------
    path : str | Path

    Returns
    -------
    Path  — the resolved directory path
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


# ── Safe numeric conversion ──────────────────────────────────
def safe_int(value, default: int = 0) -> int:
    """
    Convert a value to int without raising an exception.

    Useful when API fields contain empty strings or None.

    Parameters
    ----------
    value   : any
    default : int  (returned when conversion fails)
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default: float = 0.0) -> float:
    """Convert a value to float without raising an exception."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ── ISO 8601 duration parser ─────────────────────────────────
def parse_iso8601_duration(duration_str) -> int:
    """
    Convert an ISO 8601 duration string to total seconds.

    YouTube API returns duration in this format:
        "PT4M13S"   →  4 minutes 13 seconds  →  253 seconds
        "PT1H2M3S"  →  1 hour 2 minutes 3 seconds  →  3723 seconds
        "P0D"       →  live stream placeholder  →  0 seconds

    Parameters
    ----------
    duration_str : str | None
        ISO 8601 duration string from the YouTube API.

    Returns
    -------
    int — total seconds (0 when the string is missing or invalid)
    """
    if not duration_str or not isinstance(duration_str, str):
        return 0

    # Regular expression that captures hours, minutes, seconds
    pattern = re.compile(
        r"P"                # always starts with 'P'
        r"(?:(\d+)D)?"      # optional days
        r"(?:T"             # time section starts with 'T'
        r"(?:(\d+)H)?"      # optional hours
        r"(?:(\d+)M)?"      # optional minutes
        r"(?:(\d+)S)?"      # optional seconds
        r")?"
    )
    match = pattern.fullmatch(duration_str.strip())
    if not match:
        return 0

    days    = int(match.group(1) or 0)
    hours   = int(match.group(2) or 0)
    minutes = int(match.group(3) or 0)
    seconds = int(match.group(4) or 0)

    return days * 86400 + hours * 3600 + minutes * 60 + seconds


# ── Posting-time group assignment ────────────────────────────
def get_posting_time_group(hour: int) -> str:
    """
    Assign a descriptive posting-time group based on the hour
    of day (0–23) in the reporting timezone.

    Groups
    ------
    Late Night  : 00–05
    Morning     : 06–11
    Afternoon   : 12–16
    Evening     : 17–20
    Night       : 21–23
    """
    if 0 <= hour <= 5:
        return "Late Night"
    elif 6 <= hour <= 11:
        return "Morning"
    elif 12 <= hour <= 16:
        return "Afternoon"
    elif 17 <= hour <= 20:
        return "Evening"
    else:
        return "Night"


# ── Duration category ────────────────────────────────────────
def get_duration_category(seconds: int) -> str:
    """
    Classify a video as Short, Medium, or Long based on
    its duration in seconds.

    Short  : < 5 minutes  (< 300 s)
    Medium : 5–15 minutes (300–900 s)
    Long   : > 15 minutes (> 900 s)
    """
    if seconds < 300:
        return "Short"
    elif seconds <= 900:
        return "Medium"
    else:
        return "Long"


if __name__ == "__main__":
    # Quick tests
    assert parse_iso8601_duration("PT4M13S") == 253
    assert parse_iso8601_duration("PT1H2M3S") == 3723
    assert parse_iso8601_duration("P0D") == 0
    assert get_posting_time_group(3) == "Late Night"
    assert get_posting_time_group(9) == "Morning"
    assert get_posting_time_group(14) == "Afternoon"
    assert get_posting_time_group(18) == "Evening"
    assert get_posting_time_group(22) == "Night"
    print("All utils assertions passed ✓")
