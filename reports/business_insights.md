# Business Insights Report
## Social Media Engagement Analytics Dashboard

> **Generated:** 2026-08-12 22:39:43
> **Data source:** youtube_cleaned_data.csv
> **Reporting timezone:** Asia/Kolkata
> ⚠️ All insights are derived from the analysed dataset only.
> They do not represent universal YouTube trends.

---

## 📊 Dataset Summary

| Metric | Value |
|--------|-------|
| Total Videos Analysed | 200 |
| Total Views | 9,777,246 |
| Total Likes | 398,274 |
| Total Comments | 89,334 |
| Average Engagement Rate | 5.37% |
| Median Engagement Rate | 5.49% |

---

## 🏆 Top Performers

### Highest-Viewed Video
- **Title:** SQL Project Ideas for Your Resume
- **Views:** 1,307,962

### Highest-Engagement Video
- **Title:** Statistics Tutorial for Beginners
- **Engagement Rate:** 9.20%

### Best-Performing Channel
- **Channel:** TechInsights
- **Median Engagement Rate:** 5.95%

---

## ⏰ Posting-Time Recommendations

> **NOTE:** Publication time recorded by YouTube is in UTC.
> Times below are converted to **Asia/Kolkata**.
> Posting time does not *cause* performance — it correlates with it
> in this specific dataset.

### Best Publication Day
- **Day:** Saturday
- **Median Engagement Rate:** 6.24%
- **Sample size:** 26 videos
- **Recommendation:** Based on this dataset, Saturday shows the strongest
  median engagement. Prioritise publishing on Saturday as a starting point,
  then monitor your own channel's analytics to confirm.

### Best Publication Hour (Asia/Kolkata)
- **Hour:** 0:00
- **Median Engagement Rate:** 7.43%
- **Sample size:** 10 videos
- **Recommendation:** Hour 0:00 produced the highest median engagement
  in this dataset. Test publishing around this hour and compare to other slots
  using your YouTube Studio data.

### Best Posting-Time Group
- **Group:** Evening
- **Median Engagement Rate:** 5.84%
- **Recommendation:** Videos published during the **Evening** period achieved
  a median engagement rate of **5.84%**, compared with the overall
  median of **5.49%**. Based on this dataset, Evening is
  the strongest tested posting period.

---

## 🎬 Content Strategy Recommendations

### Best Video Duration
- **Duration Category:** Medium
- **Median Engagement Rate:** 5.77%
- **Recommendation:** Medium videos show the highest median engagement.
  Focus on producing more content in this length range while testing other
  formats to find what works for your specific audience.

### Most Engaging Content Category
- **Category ID:** 28
- **Median Engagement Rate:** 5.89%
- **Recommendation:** Content in category 28 generates the highest
  engagement per view. Consider producing more content in this category.

### High-View, Low-Engagement Opportunities
- **Videos identified:** 57
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
