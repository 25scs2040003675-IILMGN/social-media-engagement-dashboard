# ============================================================
# src/generate_sample.py
# ============================================================
# Purpose:
#   Generate a realistic synthetic dataset of 200 YouTube
#   video records so the project can be fully demonstrated
#   WITHOUT a real YouTube API key.
#
# ⚠️  IMPORTANT DISCLAIMER ⚠️
#   All data in this file is SYNTHETIC / FABRICATED.
#   Channel names, video titles, view counts, and all other
#   values are randomly generated.
#   They do NOT represent real YouTube videos, real channels,
#   or real creator performance.
#
# Called by:  python main.py generate-sample
# ============================================================

import random
import string
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta, timezone

from src.config import settings
from src.utils import get_logger, ensure_directory

logger = get_logger(__name__)

# ── Seed for reproducibility ─────────────────────────────────
# Using the same seed means everyone who runs this script gets
# the same "random" dataset — important for reproducibility.
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ── Synthetic data pools ─────────────────────────────────────

CHANNELS = [
    ("TechInsights",    "UC_TECH001"),
    ("DataDriven",      "UC_DATA002"),
    ("CodeMaster",      "UC_CODE003"),
    ("LearnWithAI",     "UC_LEAI004"),
    ("AnalyticsHub",    "UC_ANAL005"),
    ("PythonPro",       "UC_PYTH006"),
    ("BizAnalyst",      "UC_BIZA007"),
    ("SQLExpert",       "UC_SQLE008"),
]

CATEGORY_IDS = {
    "28": "Science & Technology",
    "27": "Education",
    "22": "People & Blogs",
    "24": "Entertainment",
    "25": "News & Politics",
}

TITLE_TEMPLATES = [
    "{keyword} Tutorial for Beginners",
    "How to Master {keyword} in 2024",
    "Complete {keyword} Course — Zero to Hero",
    "Top 10 {keyword} Tips and Tricks",
    "{keyword} Explained in 10 Minutes",
    "Why {keyword} is the Future of Tech",
    "{keyword} Full Project Walkthrough",
    "Build a {keyword} Dashboard from Scratch",
    "{keyword} vs Everything — Which is Best?",
    "I Tried {keyword} for 30 Days — Here's What Happened",
    "The Ultimate {keyword} Guide",
    "{keyword} Interview Questions and Answers",
    "Learn {keyword} the Right Way",
    "{keyword} Project Ideas for Your Resume",
    "Advanced {keyword} Techniques",
]

KEYWORDS = [
    "Python", "Data Analytics", "SQL", "Power BI", "Machine Learning",
    "Excel", "Tableau", "Pandas", "NumPy", "Data Science",
    "Business Intelligence", "Statistics", "AI", "Deep Learning",
    "Data Engineering", "ETL", "Dashboard", "Visualization",
]

DURATION_POOLS = {
    "Short":  (60,  299),   # 1–4 min 59 sec
    "Medium": (300, 900),   # 5–15 min
    "Long":   (901, 3600),  # 15–60 min
}


def _random_video_id() -> str:
    """Generate a random 11-character YouTube-style video ID."""
    chars = string.ascii_letters + string.digits + "_-"
    return "".join(random.choices(chars, k=11))


def _random_duration_iso(seconds: int) -> str:
    """Convert integer seconds to ISO 8601 duration string."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    parts = "PT"
    if h:
        parts += f"{h}H"
    if m:
        parts += f"{m}M"
    if s or (not h and not m):
        parts += f"{s}S"
    return parts


def _random_published_at(start_year: int = 2022, end_year: int = 2024) -> str:
    """Generate a random UTC timestamp between start_year and end_year."""
    start = datetime(start_year, 1, 1, tzinfo=timezone.utc)
    end   = datetime(end_year, 12, 31, tzinfo=timezone.utc)
    delta = end - start
    rand_seconds = random.randint(0, int(delta.total_seconds()))
    dt = start + timedelta(seconds=rand_seconds)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _generate_view_count(channel_name: str) -> int:
    """
    Generate realistic view counts.
    Larger channels get more views; uses a log-normal distribution
    which mirrors real YouTube view distributions.
    """
    # Base view count varies by channel to simulate size differences
    channel_base = {
        "TechInsights": 50000,
        "DataDriven":   30000,
        "CodeMaster":   20000,
        "LearnWithAI":  45000,
        "AnalyticsHub": 15000,
        "PythonPro":    25000,
        "BizAnalyst":   18000,
        "SQLExpert":    12000,
    }
    base = channel_base.get(channel_name, 20000)
    # Log-normal distribution for realistic skew
    return max(100, int(np.random.lognormal(np.log(base), 1.2)))


def generate_sample_data(n: int = 200, output_path=None) -> pd.DataFrame:
    """
    Create a synthetic YouTube dataset with n rows.

    Parameters
    ----------
    n           : int   — number of synthetic video records
    output_path : path  — where to save the CSV

    Returns
    -------
    pd.DataFrame
    """
    logger.info(f"Generating {n} synthetic YouTube video records...")

    records = []
    for i in range(n):
        channel_name, channel_id = random.choice(CHANNELS)
        category_id = random.choice(list(CATEGORY_IDS.keys()))
        keyword      = random.choice(KEYWORDS)
        title_tmpl   = random.choice(TITLE_TEMPLATES)
        title        = title_tmpl.format(keyword=keyword)

        # Duration: 60% Medium, 25% Long, 15% Short
        dur_type = random.choices(
            ["Short", "Medium", "Long"], weights=[15, 60, 25]
        )[0]
        dur_seconds = random.randint(*DURATION_POOLS[dur_type])

        view_count    = _generate_view_count(channel_name)
        # Like rate between 1% and 8%
        like_rate     = random.uniform(0.01, 0.08)
        like_count    = int(view_count * like_rate)
        # Comment rate between 0.05% and 1.5%
        comment_rate  = random.uniform(0.0005, 0.015)
        comment_count = int(view_count * comment_rate)

        records.append({
            "video_id":               _random_video_id(),
            "title":                  title,
            "description":            f"[SYNTHETIC] {title} — sample description for demo purposes.",
            "channel_id":             channel_id,
            "channel_title":          channel_name,
            "published_at":           _random_published_at(),
            "category_id":            category_id,
            "duration":               _random_duration_iso(dur_seconds),
            "definition":             random.choice(["hd", "sd"]),
            "caption_status":         random.choice(["true", "false"]),
            "live_broadcast_content": "none",
            "tags":                   "|".join(random.sample(KEYWORDS, k=random.randint(2, 5))),
            "view_count":             view_count,
            "like_count":             like_count,
            "comment_count":          comment_count,
            "favorite_count":         0,
            "data_source":            "SYNTHETIC_SAMPLE",  # clear label
        })

    df = pd.DataFrame(records)

    out_path = Path(output_path or settings["SAMPLE_DATA_PATH"])
    ensure_directory(out_path.parent)
    df.to_csv(out_path, index=False, encoding="utf-8")

    logger.info(f"  Sample dataset saved: {out_path}")
    logger.info(f"  Rows: {len(df)} | Columns: {df.shape[1]}")
    logger.info("  [NOTE] This is SYNTHETIC data -- not real YouTube results")

    return df


if __name__ == "__main__":
    generate_sample_data()
