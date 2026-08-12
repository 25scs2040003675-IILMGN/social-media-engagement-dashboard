# ============================================================
# src/feature_engineering.py
# ============================================================
# Purpose:
#   Adds all calculated/derived columns to the cleaned dataset.
#   These columns power the SQL queries and Power BI dashboard.
#
# Called by: main.py (as part of the clean → engineer pipeline)
# ============================================================

import pandas as pd
import numpy as np
import pytz
from pathlib import Path

from src.config import settings
from src.utils import (
    get_logger,
    get_posting_time_group,
    get_duration_category,
)

logger = get_logger(__name__)


def engineer_features(df: pd.DataFrame, timezone: str = None) -> pd.DataFrame:
    """
    Run all feature-engineering steps and return an enriched DataFrame.

    Parameters
    ----------
    df       : pd.DataFrame — cleaned video data
    timezone : str          — reporting timezone (default: from settings)

    Returns
    -------
    pd.DataFrame — with all new columns added
    """
    tz = timezone or settings["REPORTING_TIMEZONE"]

    logger.info("=" * 60)
    logger.info("STARTING FEATURE ENGINEERING")
    logger.info(f"  Reporting timezone: {tz}")
    logger.info("=" * 60)

    df = add_date_features(df, tz)
    df = add_duration_features(df)
    df = add_engagement_metrics(df)
    df = add_velocity_metrics(df)
    df = add_performance_category(df)

    logger.info(f"  Features added. Final shape: {df.shape}")
    return df


# ── Feature groups ───────────────────────────────────────────

def add_date_features(df: pd.DataFrame, timezone: str) -> pd.DataFrame:
    """
    Extract publication date/time components.

    NOTE: YouTube API returns timestamps in UTC.
    We convert to the reporting timezone before extracting
    day and hour, so that "posted at 8 PM" reflects 8 PM
    in the analyst's local timezone (e.g. Asia/Kolkata),
    not UTC.
    """
    if "published_at" not in df.columns:
        logger.warning("published_at column not found — skipping date features")
        return df

    # Ensure datetime with UTC timezone
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)

    # Convert to reporting timezone
    try:
        tz = pytz.timezone(timezone)
        df["published_local"] = df["published_at"].dt.tz_convert(tz)
    except Exception:
        logger.warning(f"Invalid timezone '{timezone}' — falling back to UTC")
        df["published_local"] = df["published_at"]

    local = df["published_local"]

    df["publication_date"]       = local.dt.date
    df["publication_year"]       = local.dt.year
    df["publication_month"]      = local.dt.month
    df["publication_month_name"] = local.dt.strftime("%B")    # "January"
    df["publication_day"]        = local.dt.day               # 1–31
    df["publication_day_name"]   = local.dt.strftime("%A")    # "Monday"
    df["publication_hour"]       = local.dt.hour              # 0–23
    df["posting_time_group"]     = df["publication_hour"].apply(get_posting_time_group)

    # Drop helper column (not needed in final CSV)
    df = df.drop(columns=["published_local"], errors="ignore")

    logger.info("  ✓ Date features added")
    return df


def add_duration_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create human-readable duration columns from duration_seconds.
    """
    if "duration_seconds" not in df.columns:
        df["duration_seconds"] = 0

    df["video_duration_seconds"] = df["duration_seconds"].fillna(0).astype(int)
    df["video_duration_minutes"] = (df["video_duration_seconds"] / 60).round(2)
    df["duration_category"]      = df["video_duration_seconds"].apply(
        get_duration_category
    )

    logger.info("  ✓ Duration features added")
    return df


def add_engagement_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate engagement KPIs.

    Formulas
    --------
    total_interactions = like_count + comment_count

    engagement_rate (%) = (like_count + comment_count) / view_count × 100
    like_rate       (%) = like_count / view_count × 100
    comment_rate    (%) = comment_count / view_count × 100

    Division-by-zero handling:
    - When view_count == 0, all rate columns are set to 0.
    - This is a deliberate design choice: a video with 0 views
      has not been seen yet, so its "engagement rate" is
      meaningfully 0 rather than undefined.
    """
    for col in ["like_count", "comment_count", "view_count"]:
        if col not in df.columns:
            df[col] = 0

    df["total_interactions"] = df["like_count"] + df["comment_count"]

    # np.where(condition, value_when_true, value_when_false)
    # avoids ZeroDivisionError for every row at once
    views = df["view_count"]

    df["engagement_rate"] = np.where(
        views > 0,
        (df["total_interactions"] / views * 100).round(4),
        0.0
    )

    df["like_rate"] = np.where(
        views > 0,
        (df["like_count"] / views * 100).round(4),
        0.0
    )

    df["comment_rate"] = np.where(
        views > 0,
        (df["comment_count"] / views * 100).round(4),
        0.0
    )

    logger.info("  ✓ Engagement metrics added")
    return df


def add_velocity_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate per-day velocity metrics.

    video_age_days   = days since publication
    views_per_day    = view_count / video_age_days
    likes_per_day    = like_count / video_age_days
    comments_per_day = comment_count / video_age_days

    Older videos have had more time to accumulate views.
    Per-day metrics make newer and older videos more comparable.
    """
    if "published_at" not in df.columns:
        return df

    now = pd.Timestamp.now("UTC").replace(tzinfo=None)
    pub_utc = pd.to_datetime(df["published_at"], utc=True)
    pub = pub_utc.dt.tz_convert("UTC").dt.tz_localize(None)
    df["video_age_days"] = (now - pub).dt.days.clip(lower=1)  # min 1 to avoid /0

    df["views_per_day"]    = (df["view_count"]    / df["video_age_days"]).round(2)
    df["likes_per_day"]    = (df["like_count"]    / df["video_age_days"]).round(2)
    df["comments_per_day"] = (df["comment_count"] / df["video_age_days"]).round(2)

    logger.info("  ✓ Velocity metrics added")
    return df


def add_performance_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify each video into a performance category based on
    its engagement_rate relative to the rest of the dataset.

    Categories use quartile thresholds:
        Low     : below the 25th percentile (Q1)
        Average : Q1 to Q3
        High    : Q3 to 95th percentile
        Viral   : above the 95th percentile

    IMPORTANT: These labels are RELATIVE to the collected
    dataset.  A video labelled 'Viral' here may not be
    considered viral on a global scale.
    """
    if "engagement_rate" not in df.columns:
        return df

    q1  = df["engagement_rate"].quantile(0.25)
    q3  = df["engagement_rate"].quantile(0.75)
    p95 = df["engagement_rate"].quantile(0.95)

    conditions = [
        df["engagement_rate"] < q1,
        (df["engagement_rate"] >= q1) & (df["engagement_rate"] < q3),
        (df["engagement_rate"] >= q3) & (df["engagement_rate"] < p95),
        df["engagement_rate"] >= p95,
    ]
    categories = ["Low", "Average", "High", "Viral"]
    df["performance_category"] = np.select(conditions, categories, default="Average")

    logger.info(
        f"  ✓ Performance categories — "
        f"Q1={q1:.2f}% | Q3={q3:.2f}% | P95={p95:.2f}%"
    )
    return df


if __name__ == "__main__":
    from src.clean_data import clean_data
    cleaned = clean_data()
    enriched = engineer_features(cleaned)
    print(enriched[["title", "engagement_rate", "performance_category"]].head(10))
