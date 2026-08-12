# ============================================================
# src/insights.py
# ============================================================
# Purpose:
#   Reads the processed dataset and dynamically generates
#   evidence-based business recommendations.
#   Saves results to reports/business_insights.md
#
# Called by:  python main.py analyze
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

from src.config import settings
from src.utils import get_logger, ensure_directory

logger = get_logger(__name__)


def generate_insights(csv_path=None, output_path=None) -> str:
    """
    Generate a business-insights report from processed data.

    Parameters
    ----------
    csv_path    : path to processed CSV
    output_path : path for the output .md file

    Returns
    -------
    str — the generated markdown report text
    """
    in_path  = Path(csv_path  or settings["PROCESSED_DATA_PATH"])
    out_path = Path(output_path or (settings["REPORTS_DIR"] / "business_insights.md"))

    if not in_path.exists():
        raise FileNotFoundError(f"Processed data not found: {in_path}")

    df = pd.read_csv(in_path, low_memory=False)
    logger.info(f"Generating insights from {len(df)} videos...")

    # ── Compute all insight values dynamically ───────────────
    total_videos   = len(df)
    total_views    = df["view_count"].sum()
    total_likes    = df["like_count"].sum() if "like_count" in df.columns else 0
    total_comments = df["comment_count"].sum() if "comment_count" in df.columns else 0
    avg_engagement = df["engagement_rate"].mean() if "engagement_rate" in df.columns else 0
    median_engagement = df["engagement_rate"].median() if "engagement_rate" in df.columns else 0

    # Best-performing channel
    if "channel_title" in df.columns and "engagement_rate" in df.columns:
        ch_eng = df.groupby("channel_title")["engagement_rate"].median()
        best_channel     = ch_eng.idxmax()
        best_channel_eng = ch_eng.max()
    else:
        best_channel, best_channel_eng = "N/A", 0

    # Highest-viewed video
    if "view_count" in df.columns:
        top_view_idx    = df["view_count"].idxmax()
        top_view_title  = df.loc[top_view_idx, "title"]
        top_view_count  = df.loc[top_view_idx, "view_count"]
    else:
        top_view_title, top_view_count = "N/A", 0

    # Highest-engagement video
    if "engagement_rate" in df.columns:
        top_eng_idx   = df["engagement_rate"].idxmax()
        top_eng_title = df.loc[top_eng_idx, "title"]
        top_eng_rate  = df.loc[top_eng_idx, "engagement_rate"]
    else:
        top_eng_title, top_eng_rate = "N/A", 0

    # Best posting day
    if "publication_day_name" in df.columns and "engagement_rate" in df.columns:
        min_sample = settings["MIN_SAMPLE_SIZE"]
        day_stats = df.groupby("publication_day_name").agg(
            video_count=("video_id", "count"),
            median_engagement=("engagement_rate", "median"),
        )
        day_stats = day_stats[day_stats["video_count"] >= min_sample]
        if not day_stats.empty:
            best_day     = day_stats["median_engagement"].idxmax()
            best_day_eng = day_stats["median_engagement"].max()
            best_day_n   = day_stats.loc[best_day, "video_count"]
        else:
            best_day, best_day_eng, best_day_n = "N/A", 0, 0
    else:
        best_day, best_day_eng, best_day_n = "N/A", 0, 0

    # Best posting hour
    if "publication_hour" in df.columns and "engagement_rate" in df.columns:
        hour_stats = df.groupby("publication_hour").agg(
            video_count=("video_id", "count"),
            median_engagement=("engagement_rate", "median"),
        )
        hour_stats = hour_stats[hour_stats["video_count"] >= settings["MIN_SAMPLE_SIZE"]]
        if not hour_stats.empty:
            best_hour     = hour_stats["median_engagement"].idxmax()
            best_hour_eng = hour_stats["median_engagement"].max()
            best_hour_n   = hour_stats.loc[best_hour, "video_count"]
        else:
            best_hour, best_hour_eng, best_hour_n = "N/A", 0, 0
    else:
        best_hour, best_hour_eng, best_hour_n = "N/A", 0, 0

    # Best posting-time group
    if "posting_time_group" in df.columns and "engagement_rate" in df.columns:
        group_stats = df.groupby("posting_time_group").agg(
            video_count=("video_id", "count"),
            median_engagement=("engagement_rate", "median"),
        )
        group_stats = group_stats[group_stats["video_count"] >= settings["MIN_SAMPLE_SIZE"]]
        if not group_stats.empty:
            best_group     = group_stats["median_engagement"].idxmax()
            best_group_eng = group_stats["median_engagement"].max()
        else:
            best_group, best_group_eng = "N/A", 0
    else:
        best_group, best_group_eng = "N/A", 0

    # Best duration category
    if "duration_category" in df.columns and "engagement_rate" in df.columns:
        dur_stats = df.groupby("duration_category")["engagement_rate"].median()
        best_duration     = dur_stats.idxmax()
        best_duration_eng = dur_stats.max()
    else:
        best_duration, best_duration_eng = "N/A", 0

    # Most engaging category
    if "category_id" in df.columns and "engagement_rate" in df.columns:
        cat_stats = df.groupby("category_id")["engagement_rate"].median()
        best_category     = cat_stats.idxmax()
        best_category_eng = cat_stats.max()
    else:
        best_category, best_category_eng = "N/A", 0

    # High-view, low-engagement (opportunity for CTAs)
    if "engagement_rate" in df.columns and "view_count" in df.columns:
        eng_median  = df["engagement_rate"].median()
        view_median = df["view_count"].median()
        high_low = df[
            (df["view_count"] > view_median) &
            (df["engagement_rate"] < eng_median)
        ]
        high_low_count = len(high_low)
    else:
        high_low_count = 0

    # ── Build markdown report ────────────────────────────────
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tz_label = settings["REPORTING_TIMEZONE"]

    report = f"""# Business Insights Report
## Social Media Engagement Analytics Dashboard

> **Generated:** {generated_at}
> **Data source:** {in_path.name}
> **Reporting timezone:** {tz_label}
> ⚠️ All insights are derived from the analysed dataset only.
> They do not represent universal YouTube trends.

---

## 📊 Dataset Summary

| Metric | Value |
|--------|-------|
| Total Videos Analysed | {total_videos:,} |
| Total Views | {total_views:,.0f} |
| Total Likes | {total_likes:,.0f} |
| Total Comments | {total_comments:,.0f} |
| Average Engagement Rate | {avg_engagement:.2f}% |
| Median Engagement Rate | {median_engagement:.2f}% |

---

## 🏆 Top Performers

### Highest-Viewed Video
- **Title:** {top_view_title}
- **Views:** {top_view_count:,}

### Highest-Engagement Video
- **Title:** {top_eng_title}
- **Engagement Rate:** {top_eng_rate:.2f}%

### Best-Performing Channel
- **Channel:** {best_channel}
- **Median Engagement Rate:** {best_channel_eng:.2f}%

---

## ⏰ Posting-Time Recommendations

> **NOTE:** Publication time recorded by YouTube is in UTC.
> Times below are converted to **{tz_label}**.
> Posting time does not *cause* performance — it correlates with it
> in this specific dataset.

### Best Publication Day
- **Day:** {best_day}
- **Median Engagement Rate:** {best_day_eng:.2f}%
- **Sample size:** {best_day_n} videos
- **Recommendation:** Based on this dataset, {best_day} shows the strongest
  median engagement. Prioritise publishing on {best_day} as a starting point,
  then monitor your own channel's analytics to confirm.

### Best Publication Hour ({tz_label})
- **Hour:** {best_hour}:00
- **Median Engagement Rate:** {best_hour_eng:.2f}%
- **Sample size:** {best_hour_n} videos
- **Recommendation:** Hour {best_hour}:00 produced the highest median engagement
  in this dataset. Test publishing around this hour and compare to other slots
  using your YouTube Studio data.

### Best Posting-Time Group
- **Group:** {best_group}
- **Median Engagement Rate:** {best_group_eng:.2f}%
- **Recommendation:** Videos published during the **{best_group}** period achieved
  a median engagement rate of **{best_group_eng:.2f}%**, compared with the overall
  median of **{median_engagement:.2f}%**. Based on this dataset, {best_group} is
  the strongest tested posting period.

---

## 🎬 Content Strategy Recommendations

### Best Video Duration
- **Duration Category:** {best_duration}
- **Median Engagement Rate:** {best_duration_eng:.2f}%
- **Recommendation:** {best_duration} videos show the highest median engagement.
  Focus on producing more content in this length range while testing other
  formats to find what works for your specific audience.

### Most Engaging Content Category
- **Category ID:** {best_category}
- **Median Engagement Rate:** {best_category_eng:.2f}%
- **Recommendation:** Content in category {best_category} generates the highest
  engagement per view. Consider producing more content in this category.

### High-View, Low-Engagement Opportunities
- **Videos identified:** {high_low_count}
- **What this means:** These videos attract viewers but do not convert them
  into likes or comments. They represent an opportunity to add stronger calls
  to action (CTAs), improve end screens, or engage with the comment section
  to encourage interaction.

---

## ⚠️ Limitations

1. **YouTube API public data only** — impressions, watch time, click-through rate,
   and subscriber conversions are not available through the public API.
2. **Some creators hide likes** — like_count may be 0 even for popular videos.
3. **Sample bias** — results depend on the channels and search queries used.
4. **Older videos accumulate more views** — age-adjusted metrics (views_per_day)
   provide a fairer comparison.
5. **Viral videos distort averages** — median is used instead of mean
   for posting-time recommendations.
6. **No causal claims** — posting time correlates with engagement; it does
   not cause it. Many other factors affect video performance.

---

## 🚀 Future Improvements

- Connect to YouTube Analytics API for authenticated owner metrics
- Implement scheduled, incremental data collection
- Add NLP sentiment analysis of comment text
- Perform thumbnail analysis using computer vision
- Deploy a real-time Streamlit dashboard
- Expand to Instagram and TikTok for cross-platform comparison

---

*Report generated automatically by `src/insights.py`*
*Replace sample data with real YouTube API data for production insights.*
"""

    ensure_directory(out_path.parent)
    out_path.write_text(report, encoding="utf-8")
    logger.info(f"Business insights saved: {out_path}")

    return report


if __name__ == "__main__":
    print(generate_insights())
