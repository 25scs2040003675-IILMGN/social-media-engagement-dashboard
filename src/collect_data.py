# ============================================================
# src/collect_data.py
# ============================================================
# Purpose:
#   Orchestrates data collection.  Calls YouTubeAPI and saves
#   the raw results to data/raw/youtube_raw_data.csv.
#
# This module is called by main.py when the user runs:
#   python main.py collect --query "data analytics" --max-results 100
# ============================================================

import pandas as pd
from pathlib import Path

from src.youtube_api import YouTubeAPI
from src.config import settings, validate_api_key
from src.utils import get_logger, ensure_directory

logger = get_logger(__name__)


def collect_by_query(query: str, max_results: int = 50) -> pd.DataFrame:
    """
    Search YouTube by keyword and return a DataFrame of results.

    Parameters
    ----------
    query       : str  — search term
    max_results : int  — number of videos to collect

    Returns
    -------
    pd.DataFrame  — raw video data (one row per video)
    """
    if not validate_api_key():
        logger.error(
            "No valid YouTube API key found.\n"
            "  1. Copy .env.example to .env\n"
            "  2. Add your API key\n"
            "  3. Or run:  python main.py generate-sample"
        )
        return pd.DataFrame()

    api = YouTubeAPI(api_key=settings["YOUTUBE_API_KEY"])
    videos = api.search_videos(query=query, max_results=max_results)
    return _to_dataframe(videos)


def collect_by_channel(channel_id: str, max_results: int = 50) -> pd.DataFrame:
    """
    Collect videos from a specific YouTube channel.

    Parameters
    ----------
    channel_id  : str  — YouTube channel ID (starts with "UC")
    max_results : int

    Returns
    -------
    pd.DataFrame
    """
    if not validate_api_key():
        logger.error("No valid API key. Run: python main.py generate-sample")
        return pd.DataFrame()

    api = YouTubeAPI(api_key=settings["YOUTUBE_API_KEY"])
    videos = api.get_channel_videos(channel_id=channel_id, max_results=max_results)
    return _to_dataframe(videos)


def collect_by_video_ids(video_ids: list[str]) -> pd.DataFrame:
    """
    Retrieve details for a pre-defined list of video IDs.

    Parameters
    ----------
    video_ids : list[str]

    Returns
    -------
    pd.DataFrame
    """
    if not validate_api_key():
        logger.error("No valid API key. Run: python main.py generate-sample")
        return pd.DataFrame()

    api = YouTubeAPI(api_key=settings["YOUTUBE_API_KEY"])
    videos = api.get_videos_by_ids(video_ids)
    return _to_dataframe(videos)


def save_raw_data(df: pd.DataFrame, path=None) -> Path:
    """
    Save the raw DataFrame to CSV.

    Parameters
    ----------
    df   : pd.DataFrame
    path : str | Path | None  (defaults to settings["RAW_DATA_PATH"])

    Returns
    -------
    Path  — where the file was saved
    """
    if df.empty:
        logger.warning("DataFrame is empty — nothing saved.")
        return None

    out_path = Path(path or settings["RAW_DATA_PATH"])
    ensure_directory(out_path.parent)
    df.to_csv(out_path, index=False, encoding="utf-8")
    logger.info(f"Raw data saved: {out_path}  ({len(df)} rows)")
    return out_path


# ── Internal helpers ─────────────────────────────────────────

def _to_dataframe(videos: list[dict]) -> pd.DataFrame:
    """Convert a list of video dicts to a Pandas DataFrame."""
    if not videos:
        return pd.DataFrame()
    df = pd.DataFrame(videos)
    logger.info(f"Created DataFrame: {df.shape[0]} rows × {df.shape[1]} columns")
    return df
