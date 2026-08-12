# ============================================================
# src/clean_data.py
# ============================================================
# Purpose:
#   A complete, reproducible data-cleaning pipeline.
#   Reads raw CSV → applies cleaning steps → saves processed CSV.
#
# Called by:  python main.py clean
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path

from src.config import settings
from src.utils import get_logger, ensure_directory, parse_iso8601_duration

logger = get_logger(__name__)


# ── Main pipeline ────────────────────────────────────────────

def clean_data(input_path=None, output_path=None) -> pd.DataFrame:
    """
    Run the full data-cleaning pipeline.

    Parameters
    ----------
    input_path  : path to raw CSV  (default: settings["RAW_DATA_PATH"])
    output_path : path for cleaned CSV (default: settings["PROCESSED_DATA_PATH"])

    Returns
    -------
    pd.DataFrame — cleaned DataFrame
    """
    in_path  = Path(input_path  or settings["RAW_DATA_PATH"])
    out_path = Path(output_path or settings["PROCESSED_DATA_PATH"])

    if not in_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {in_path}\n"
            "Run: python main.py generate-sample   (or collect)"
        )

    logger.info("=" * 60)
    logger.info("STARTING DATA CLEANING PIPELINE")
    logger.info("=" * 60)

    df = pd.read_csv(in_path, low_memory=False)
    initial_rows = len(df)
    logger.info(f"  Loaded raw data: {initial_rows} rows × {df.shape[1]} columns")

    df = standardise_column_names(df)
    df = remove_exact_duplicates(df)
    df = remove_duplicate_video_ids(df)
    df = convert_numeric_columns(df)
    df = remove_negative_values(df)
    df = parse_published_at(df)
    df = clean_text_columns(df)
    df = handle_missing_titles(df)
    df = parse_duration_column(df)
    df = flag_outliers(df)

    final_rows = len(df)
    removed    = initial_rows - final_rows

    logger.info("-" * 60)
    logger.info("CLEANING SUMMARY")
    logger.info(f"  Initial rows  : {initial_rows}")
    logger.info(f"  Removed rows  : {removed}")
    logger.info(f"  Final rows    : {final_rows}")
    logger.info(f"  Missing values: {df.isnull().sum().sum()} cells")
    logger.info("-" * 60)

    ensure_directory(out_path.parent)
    df.to_csv(out_path, index=False, encoding="utf-8")
    logger.info(f"  Cleaned data saved: {out_path}")

    return df


# ── Cleaning steps (each is a pure function) ─────────────────

def standardise_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert all column names to lowercase snake_case.
    E.g.: 'VideoID' → 'video_id', 'ViewCount' → 'view_count'
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[\s\-]+", "_", regex=True)
        .str.replace(r"[^\w]", "", regex=True)
    )
    return df


def remove_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows where every column value is identical."""
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    if removed:
        logger.info(f"  Removed {removed} exact duplicate rows")
    return df


def remove_duplicate_video_ids(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only the first occurrence of each video_id.
    A video appearing twice is a data-collection artefact,
    not a real second video.
    """
    if "video_id" not in df.columns:
        return df
    before = len(df)
    df = df.drop_duplicates(subset=["video_id"], keep="first")
    removed = before - len(df)
    if removed:
        logger.info(f"  Removed {removed} duplicate video_id rows")
    return df


def convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert view_count, like_count, comment_count, and
    favorite_count to numeric (integer) types.

    Missing values for engagement counts are set to 0 because:
    - A missing count means the API did not return the field,
      which typically means the creator has hidden the metric
      OR the count is genuinely 0.
    - For views we keep NaN (dropping those rows later)
      so we don't silently inflate the dataset.
    """
    count_cols = ["like_count", "comment_count", "favorite_count"]
    for col in count_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    if "view_count" in df.columns:
        df["view_count"] = pd.to_numeric(df["view_count"], errors="coerce")
        # Drop rows with no view count — they cannot be analysed
        before = len(df)
        df = df.dropna(subset=["view_count"])
        df["view_count"] = df["view_count"].astype(int)
        removed = before - len(df)
        if removed:
            logger.info(f"  Dropped {removed} rows with missing view_count")

    return df


def remove_negative_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows where engagement counts are negative.
    Negative counts are impossible and indicate data corruption.
    """
    metric_cols = ["view_count", "like_count", "comment_count"]
    before = len(df)
    for col in metric_cols:
        if col in df.columns:
            df = df[df[col] >= 0]
    removed = before - len(df)
    if removed:
        logger.info(f"  Removed {removed} rows with negative metric values")
    return df


def parse_published_at(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the published_at column to a timezone-aware
    pandas datetime.  Rows that cannot be parsed are removed.
    """
    if "published_at" not in df.columns:
        return df

    before = len(df)
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)
    df = df.dropna(subset=["published_at"])
    removed = before - len(df)
    if removed:
        logger.info(f"  Removed {removed} rows with invalid published_at")
    return df


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip leading/trailing whitespace from all string columns.
    """
    # Include both 'object' (pandas 2.x) and 'str' (pandas 3.x StringDtype)
    str_cols = df.select_dtypes(include=["object", "str"]).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        # Replace literal "nan" strings (from CSV reading) with proper NaN
        df[col] = df[col].replace("nan", np.nan)
    return df


def handle_missing_titles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace missing titles with a placeholder.
    A video with no title is likely unavailable but was included
    in an API response — we keep it with a clear label.
    """
    if "title" in df.columns:
        df["title"] = df["title"].fillna("[Title Unavailable]")
    if "channel_title" in df.columns:
        df["channel_title"] = df["channel_title"].fillna("[Unknown Channel]")
    return df


def parse_duration_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the ISO 8601 'duration' column (e.g. "PT4M13S") to
    an integer column 'duration_seconds'.

    The raw 'duration' string column is kept for reference.
    """
    if "duration" in df.columns:
        df["duration_seconds"] = df["duration"].apply(parse_iso8601_duration)
    else:
        df["duration_seconds"] = 0
    return df


def flag_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify extreme outliers in view_count using the IQR method
    and add an 'is_outlier' boolean flag.

    WHY flag rather than remove?
    A video with 50 million views may genuinely be viral.
    Silently deleting it would remove valuable real data.
    The flag lets analysts decide whether to include or exclude
    viral videos for a given analysis.
    """
    if "view_count" not in df.columns:
        return df

    Q1 = df["view_count"].quantile(0.25)
    Q3 = df["view_count"].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 3 * IQR   # using 3×IQR (less aggressive than 1.5×)
    upper = Q3 + 3 * IQR

    df["is_outlier"] = (df["view_count"] < lower) | (df["view_count"] > upper)
    outlier_count = df["is_outlier"].sum()
    if outlier_count:
        logger.info(
            f"  Flagged {outlier_count} outlier rows "
            f"(view_count outside [{lower:.0f}, {upper:.0f}]) — NOT removed"
        )
    return df


if __name__ == "__main__":
    clean_data()
