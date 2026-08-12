# Interview Questions & Answers
## Social Media Engagement Analytics Dashboard

> **Tip:** Read through these before your interview.
> For each answer, relate it back to *your specific project* —
> mention the exact file, column name, or formula you used.

---

## Project Overview

**Q1. Can you explain what this project does in simple terms?**

This project collects YouTube video data using the YouTube Data API v3,
cleans and analyses it with Python and Pandas, stores it in a SQLite database,
and visualises the results in a Power BI dashboard. The goal is to find
the best time to post videos and which types of content perform best,
based on data rather than guesswork.

---

**Q2. Why did you choose YouTube as your data source?**

YouTube has a free, official public API (YouTube Data API v3) that provides
real engagement metrics — views, likes, comments — without web scraping.
Scraping would violate YouTube's terms of service. The API is free for up to
10,000 quota units per day, which is sufficient for a portfolio project.

---

**Q3. What is the main business question this project answers?**

Two main questions:
1. *When* should a creator publish to maximise engagement?
2. *What type* of content (duration, category, style) performs best?

---

## API & Data Collection

**Q4. How do you authenticate with the YouTube API?**

Using an API key stored in a `.env` file. The `python-dotenv` library loads
the key at runtime: `os.getenv("YOUTUBE_API_KEY")`. The key is never
hard-coded in any Python file and is excluded from Git via `.gitignore`.

---

**Q5. What is API pagination and how did you handle it?**

The YouTube API returns at most 50 results per call. For more results,
the API includes a `nextPageToken` in the response. My `YouTubeAPI._search_video_ids()`
method checks for this token in a while loop and makes additional requests
until all required results are collected or no more pages exist.

---

**Q6. What is the YouTube API quota and how did you manage it?**

Each project gets 10,000 quota units per day.
- `search.list` costs 100 units per call
- `videos.list` costs 1 unit per call (handles up to 50 IDs)

I minimised quota by using `search.list` only to collect video IDs, then
batching all IDs into `videos.list` calls (50 IDs per call = 1 unit each).
I also added `time.sleep()` between requests to avoid rate-limiting.

---

**Q7. How did you handle missing API data?**

I used `.get()` with default values throughout `youtube_api.py`:
- Missing statistics (hidden likes, disabled comments) → `safe_int()` returns 0
- Missing titles → filled with "[Title Unavailable]" in `clean_data.py`
- Missing view counts → rows are dropped (you cannot analyse a video with no views)

---

**Q8. What happens if a video is deleted or unavailable?**

The `videos.list` endpoint simply omits unavailable videos from the response.
My `_get_video_details()` loop processes only what is returned, so deleted
videos are silently skipped with no error.

---

## Data Cleaning

**Q9. What cleaning steps did you perform?**

1. Removed exact duplicate rows
2. Removed duplicate video IDs (keeping the first occurrence)
3. Standardised column names to snake_case
4. Converted counts to integers; filled missing engagement counts with 0
5. Dropped rows with missing view counts
6. Removed rows with negative metric values
7. Parsed `published_at` to UTC datetime; removed invalid dates
8. Stripped whitespace from text columns
9. Filled missing titles with placeholder text
10. Converted ISO 8601 durations to seconds
11. Flagged extreme outliers (did not delete them)

---

**Q10. Why did you fill missing like_count with 0 but drop missing view_count rows?**

Missing like_count usually means the creator has hidden their like counter,
OR the count is genuinely 0. Either way, 0 is a reasonable and safe default.

Missing view_count makes the row unanalysable — you cannot calculate
engagement rate, views per day, or any other metric. Those rows are removed.

---

**Q11. Why did you flag outliers instead of removing them?**

A video with 50 million views may genuinely be viral — removing it would
delete real, valuable data. By flagging with `is_outlier = True`, analysts
can choose to include or exclude viral videos depending on their question.
This is the industry-standard approach.

---

## Feature Engineering

**Q12. How did you calculate engagement rate?**

```
engagement_rate = (like_count + comment_count) / view_count × 100
```

This measures what percentage of viewers actively interacted with the video.
It is stored as a percentage value in the `engagement_rate` column.

---

**Q13. How did you prevent division by zero?**

I used `numpy.where()`:
```python
df["engagement_rate"] = np.where(
    views > 0,
    (df["total_interactions"] / views * 100).round(4),
    0.0
)
```
When `view_count == 0`, the rate is set to 0.0 rather than raising an error
or producing NaN/Infinity. I documented this design choice in the code comments.

---

**Q14. Why did you convert YouTube's UTC timestamps to the Asia/Kolkata timezone?**

YouTube returns `published_at` in UTC. If I extracted "hour 18" from UTC, that
means 11:30 PM in India. The posting-time analysis would be meaningless.
Converting to `Asia/Kolkata` (IST, UTC+5:30) means that when I say
"the best hour is 18:00", it refers to 6 PM IST — the time that actually
matters to an Indian creator or analyst.

---

**Q15. What are the performance categories and how are they defined?**

Each video is classified based on its engagement_rate compared to the
rest of the dataset:
- **Low**: below the 25th percentile
- **Average**: 25th to 75th percentile
- **High**: 75th to 95th percentile
- **Viral**: above the 95th percentile

These are *relative* labels — a "Viral" video in a small dataset may
not be truly viral on YouTube. I noted this limitation in the README.

---

## Database

**Q16. Why did you use SQLite as the default database?**

SQLite requires no server installation, runs on any computer, stores data
in a single file, and is fully supported by Python's standard library and
SQLAlchemy. It is the perfect choice for a portable portfolio project.

---

**Q17. How did you design the database schema?**

I created a single flat table `youtube_engagement` with `video_id` as the
primary key. Indexes were added on `channel_title`, `published_at`,
`publication_day_name`, and `engagement_rate` — the columns most frequently
used in GROUP BY and WHERE clauses — to improve query performance.

---

**Q18. Why did you use SQLAlchemy instead of raw SQL?**

SQLAlchemy provides a single interface that works with both SQLite and MySQL.
By changing one environment variable (`DATABASE_TYPE=mysql`), the same Python
code connects to a MySQL server. This makes the project scalable without
rewriting the database layer.

---

## SQL Analysis

**Q19. What is a window function? Give an example from your project.**

A window function performs a calculation across a set of rows that are
related to the current row, without collapsing rows like GROUP BY does.

Example from `analysis_queries.sql` (Query 19):
```sql
RANK() OVER (PARTITION BY channel_title ORDER BY view_count DESC) AS view_rank
```
This ranks every video within its own channel without needing a subquery.

---

**Q20. What is a CTE and why is it useful?**

A CTE (Common Table Expression) is a named temporary result set defined
with `WITH`. It makes complex queries readable by breaking them into steps.

Example (Query 25):
```sql
WITH channel_summary AS (
    SELECT channel_title, AVG(engagement_rate) AS avg_eng
    FROM youtube_engagement GROUP BY channel_title
)
SELECT * FROM channel_summary ORDER BY avg_eng DESC;
```

---

**Q21. How did you find the best posting hour without being misled by popular channels?**

Instead of using total views per hour (which is biased by channels that post
more frequently), I used **median engagement rate** per hour. Median is
resistant to outliers. I also required a minimum of 5 videos per hour
before declaring any hour as "best".

---

## Power BI & DAX

**Q22. What is a star schema and did you use one?**

A star schema has a central fact table connected to smaller dimension tables.
In my project:
- **Fact**: `FactYouTubeEngagement` (the flat CSV)
- **Dimensions**: `DimDate`, `DimChannel`, `DimCategory`, `DimPostingTime`

For a beginner project, I used a flat CSV (single table) in Power BI,
which is acceptable. I documented the star schema in the Power BI guide
as a recommended upgrade.

---

**Q23. What is DIVIDE() in DAX and why use it instead of the / operator?**

The `/` operator in DAX throws an error when the denominator is 0.
`DIVIDE(numerator, denominator, 0)` returns the third argument (0 in my case)
when the denominator is 0 or blank. This prevents divide-by-zero errors
and keeps the dashboard stable even when no data matches a filter.

---

**Q24. How did you create the month-over-month comparison?**

Using DAX time intelligence:
```dax
Previous Month Views = CALCULATE([Total Views], PREVIOUSMONTH(DimDate[Date]))
MoM Growth = DIVIDE([Total Views] - [Previous Month Views], [Previous Month Views], 0) * 100
```
This requires a DimDate table with a continuous date range and a relationship
to the publication_date column.

---

## Correlation & Statistics

**Q25. Did you find any correlations? What do they mean?**

In the EDA notebook, I found a strong positive correlation between
view_count and like_count (expected). The correlation between view_count
and engagement_rate was weak — meaning more views does not guarantee
higher engagement.

**Important:** Correlation measures statistical association, not causation.
Just because two numbers move together does not mean one causes the other.

---

## Project Limitations

**Q26. What data is NOT available through the public YouTube API?**

- Impressions and click-through rate (CTR)
- Watch time and audience retention
- Subscriber conversions
- Shares and saves
- Revenue and monetisation data
- Detailed audience demographics

These are only available through the YouTube Analytics API, which requires
OAuth 2.0 authentication and access to the creator's own channel.

---

**Q27. What are the limitations of your posting-time analysis?**

1. YouTube timestamps are in UTC — timezone conversion is an assumption
2. Publication time correlates with engagement but does not cause it
3. Sample size per hour may be small — I require at least 5 videos
4. Results depend on the specific channels and search queries collected
5. Older videos have had more time to accumulate views

---

**Q28. How would you improve this project in the future?**

1. Use YouTube Analytics API for watch time and CTR (authenticated access)
2. Implement scheduled daily collection with incremental database updates
3. Add NLP sentiment analysis of comment text
4. Build a real-time Streamlit or Dash web app
5. Analyse thumbnail images using computer vision
6. Expand to Instagram and TikTok for cross-platform comparison

---

**Q29. Why did you use sample data? Isn't that fake?**

The sample data is clearly labelled as `SYNTHETIC_SAMPLE` with a
`data_source` column. I created it so the project can be demonstrated
and tested without an API key — which is important for portfolio reviewers
who may not have a YouTube API key. All files, pipelines, and analyses
work identically with real API data. Replacing sample data takes one command:
`python main.py collect --query "your topic" --max-results 100`.

---

**Q30. How would you explain this project to a non-technical interviewer?**

"I built a system that automatically collects data about YouTube videos,
analyses which types of content get the most audience engagement, and
presents the findings in an interactive dashboard. A content creator could
use it to answer questions like: Should I post on Tuesday or Friday?
Should my videos be 5 minutes or 15 minutes? What topics get the most
comments? The project uses Python for data collection and analysis, SQL
for querying the data, and Power BI for the visual dashboard."

---

## Two-Minute Project Explanation (Interview Script)

> Practice saying this out loud until it flows naturally.

"I built a Social Media Engagement Analytics Dashboard as an end-to-end
portfolio project. The project collects YouTube video data using the
official YouTube Data API v3. I wrote a Python module that handles API
authentication, pagination, quota management, and error handling.

The collected data goes through a cleaning pipeline that removes duplicates,
converts data types, handles missing values, and parses ISO 8601 video
durations into seconds. I then add engineered features — engagement rate,
like rate, comment rate, views per day, publication hour and day in the
India Standard Time timezone, and duration categories.

The cleaned, enriched data is stored in a SQLite database using SQLAlchemy.
I wrote 25 SQL queries — including CTEs, window functions like RANK and LAG,
and a month-over-month trend analysis.

Finally, I export the processed CSV to Power BI where I built a four-page
interactive dashboard. The key analytical finding is which day, hour, and
content category produce the highest median engagement, supported by the
calculated DAX measures in the dashboard.

The project is fully tested with pytest, documented for GitHub, and
structured so a real API key can be plugged in with one .env change."
