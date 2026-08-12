-- ============================================================
-- sql/analysis_queries.sql
-- ============================================================
-- Purpose:
--   25 analytical SQL queries for the youtube_engagement table.
--   All queries are SQLite-compatible.
--   Where MySQL syntax differs, an alternative is noted.
--
-- How to run in Python:
--   from src.database import query_database
--   df = query_database("SELECT ...")
-- ============================================================


-- ════════════════════════════════════════════════════════════
-- SECTION 1 — BASIC SUMMARY STATISTICS
-- ════════════════════════════════════════════════════════════

-- Query 1: Total number of videos in the dataset
SELECT COUNT(*) AS total_videos
FROM youtube_engagement;


-- Query 2: Total views across all videos
SELECT SUM(view_count) AS total_views
FROM youtube_engagement;


-- Query 3: Total likes across all videos
SELECT SUM(like_count) AS total_likes
FROM youtube_engagement;


-- Query 4: Total comments across all videos
SELECT SUM(comment_count) AS total_comments
FROM youtube_engagement;


-- Query 5: Average engagement rate
SELECT
    ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate,
    -- SQLite does not have a native MEDIAN function.
    -- The subquery below approximates it.
    (
        SELECT engagement_rate
        FROM youtube_engagement
        ORDER BY engagement_rate
        LIMIT 1
        OFFSET (SELECT COUNT(*) FROM youtube_engagement) / 2
    ) AS approx_median_engagement_rate
FROM youtube_engagement;


-- ════════════════════════════════════════════════════════════
-- SECTION 2 — TOP VIDEO RANKINGS
-- ════════════════════════════════════════════════════════════

-- Query 6: Top 10 videos by total view count
SELECT
    title,
    channel_title,
    view_count,
    like_count,
    comment_count,
    ROUND(engagement_rate, 2) AS engagement_rate_pct
FROM youtube_engagement
ORDER BY view_count DESC
LIMIT 10;


-- Query 7: Top 10 videos by engagement rate
-- Filters out videos with fewer than 1000 views to remove
-- low-view videos that have artificially high engagement rates
SELECT
    title,
    channel_title,
    view_count,
    ROUND(engagement_rate, 2) AS engagement_rate_pct,
    performance_category
FROM youtube_engagement
WHERE view_count >= 1000
ORDER BY engagement_rate DESC
LIMIT 10;


-- ════════════════════════════════════════════════════════════
-- SECTION 3 — CHANNEL PERFORMANCE
-- ════════════════════════════════════════════════════════════

-- Query 8: Top channels by total views
SELECT
    channel_title,
    COUNT(*)                      AS video_count,
    SUM(view_count)               AS total_views,
    ROUND(AVG(view_count), 0)     AS avg_views_per_video,
    ROUND(AVG(engagement_rate),2) AS avg_engagement_rate
FROM youtube_engagement
GROUP BY channel_title
ORDER BY total_views DESC
LIMIT 10;


-- Query 9: Top channels by average engagement rate
-- Only include channels with at least 5 videos (MIN_SAMPLE_SIZE)
SELECT
    channel_title,
    COUNT(*)                       AS video_count,
    ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate,
    ROUND(MIN(engagement_rate), 4) AS min_engagement,
    ROUND(MAX(engagement_rate), 4) AS max_engagement
FROM youtube_engagement
GROUP BY channel_title
HAVING video_count >= 5
ORDER BY avg_engagement_rate DESC
LIMIT 10;


-- ════════════════════════════════════════════════════════════
-- SECTION 4 — POSTING-TIME ANALYSIS
-- ════════════════════════════════════════════════════════════

-- Query 10: Average engagement by publication day of week
SELECT
    publication_day_name,
    COUNT(*)                        AS video_count,
    ROUND(AVG(view_count), 0)       AS avg_views,
    ROUND(AVG(engagement_rate), 4)  AS avg_engagement_rate
FROM youtube_engagement
GROUP BY publication_day_name
ORDER BY avg_engagement_rate DESC;


-- Query 11: Average views by publication hour
SELECT
    publication_hour,
    COUNT(*)                        AS video_count,
    ROUND(AVG(view_count), 0)       AS avg_views,
    ROUND(AVG(engagement_rate), 4)  AS avg_engagement_rate
FROM youtube_engagement
GROUP BY publication_hour
ORDER BY publication_hour;


-- Query 12: Best posting-time group by average engagement
-- Only groups with at least 5 videos are considered
SELECT
    posting_time_group,
    COUNT(*)                       AS video_count,
    ROUND(AVG(view_count), 0)      AS avg_views,
    ROUND(AVG(engagement_rate),4)  AS avg_engagement_rate,
    SUM(total_interactions)        AS total_interactions
FROM youtube_engagement
GROUP BY posting_time_group
HAVING video_count >= 5
ORDER BY avg_engagement_rate DESC;


-- ════════════════════════════════════════════════════════════
-- SECTION 5 — TREND ANALYSIS
-- ════════════════════════════════════════════════════════════

-- Query 13: Monthly publication trend (video count by month)
SELECT
    publication_year,
    publication_month,
    publication_month_name,
    COUNT(*) AS video_count
FROM youtube_engagement
GROUP BY publication_year, publication_month, publication_month_name
ORDER BY publication_year, publication_month;


-- Query 14: Monthly engagement trend (average engagement by month)
SELECT
    publication_year,
    publication_month,
    publication_month_name,
    COUNT(*)                       AS video_count,
    ROUND(AVG(engagement_rate),4)  AS avg_engagement_rate,
    ROUND(AVG(view_count), 0)      AS avg_views
FROM youtube_engagement
GROUP BY publication_year, publication_month, publication_month_name
ORDER BY publication_year, publication_month;


-- ════════════════════════════════════════════════════════════
-- SECTION 6 — CONTENT ANALYSIS
-- ════════════════════════════════════════════════════════════

-- Query 15: Performance by video duration category
SELECT
    duration_category,
    COUNT(*)                       AS video_count,
    ROUND(AVG(view_count), 0)      AS avg_views,
    ROUND(AVG(engagement_rate),4)  AS avg_engagement_rate,
    ROUND(AVG(like_rate), 4)       AS avg_like_rate,
    ROUND(AVG(comment_rate), 4)    AS avg_comment_rate
FROM youtube_engagement
GROUP BY duration_category
ORDER BY avg_engagement_rate DESC;


-- Query 16: Content category performance
SELECT
    category_id,
    COUNT(*)                       AS video_count,
    ROUND(AVG(view_count), 0)      AS avg_views,
    ROUND(AVG(engagement_rate),4)  AS avg_engagement_rate
FROM youtube_engagement
GROUP BY category_id
ORDER BY avg_engagement_rate DESC;


-- ════════════════════════════════════════════════════════════
-- SECTION 7 — OPPORTUNITY IDENTIFICATION
-- ════════════════════════════════════════════════════════════

-- Query 17: High views, low engagement (CTA improvement opportunity)
-- View count above median, engagement below median
SELECT
    title,
    channel_title,
    view_count,
    ROUND(engagement_rate, 2) AS engagement_rate_pct,
    duration_category
FROM youtube_engagement
WHERE
    view_count     > (SELECT AVG(view_count)     FROM youtube_engagement)
    AND engagement_rate < (SELECT AVG(engagement_rate) FROM youtube_engagement)
ORDER BY view_count DESC
LIMIT 20;


-- Query 18: Low views, high engagement (hidden gems)
-- These videos convert well but have not been widely promoted
SELECT
    title,
    channel_title,
    view_count,
    ROUND(engagement_rate, 2) AS engagement_rate_pct,
    duration_category
FROM youtube_engagement
WHERE
    view_count     < (SELECT AVG(view_count)     FROM youtube_engagement)
    AND engagement_rate > (SELECT AVG(engagement_rate) FROM youtube_engagement)
ORDER BY engagement_rate DESC
LIMIT 20;


-- ════════════════════════════════════════════════════════════
-- SECTION 8 — WINDOW FUNCTIONS
-- ════════════════════════════════════════════════════════════

-- Query 19: Rank videos within each channel by views
-- RANK() leaves gaps for ties; DENSE_RANK() does not
SELECT
    channel_title,
    title,
    view_count,
    RANK()       OVER (PARTITION BY channel_title ORDER BY view_count DESC)
        AS view_rank_in_channel,
    DENSE_RANK() OVER (PARTITION BY channel_title ORDER BY engagement_rate DESC)
        AS engagement_rank_in_channel
FROM youtube_engagement
ORDER BY channel_title, view_rank_in_channel;


-- Query 20: Month-over-month engagement comparison using LAG()
WITH monthly AS (
    SELECT
        publication_year,
        publication_month,
        ROUND(AVG(engagement_rate), 4) AS avg_engagement
    FROM youtube_engagement
    GROUP BY publication_year, publication_month
),
with_prev AS (
    SELECT
        publication_year,
        publication_month,
        avg_engagement,
        LAG(avg_engagement, 1) OVER (
            ORDER BY publication_year, publication_month
        ) AS prev_month_engagement
    FROM monthly
)
SELECT
    publication_year,
    publication_month,
    avg_engagement,
    prev_month_engagement,
    ROUND(
        (avg_engagement - prev_month_engagement) / prev_month_engagement * 100,
        2
    ) AS mom_change_pct
FROM with_prev
ORDER BY publication_year, publication_month;


-- Query 21: Each channel's contribution to total views (percentage)
SELECT
    channel_title,
    SUM(view_count) AS channel_views,
    ROUND(
        SUM(view_count) * 100.0 / SUM(SUM(view_count)) OVER (),
        2
    ) AS pct_of_total_views
FROM youtube_engagement
GROUP BY channel_title
ORDER BY channel_views DESC;


-- ════════════════════════════════════════════════════════════
-- SECTION 9 — ADVANCED ANALYSIS
-- ════════════════════════════════════════════════════════════

-- Query 22: Videos performing above their channel average
WITH channel_avg AS (
    SELECT
        channel_title,
        AVG(engagement_rate) AS channel_avg_engagement
    FROM youtube_engagement
    GROUP BY channel_title
)
SELECT
    y.title,
    y.channel_title,
    y.view_count,
    ROUND(y.engagement_rate, 2)       AS video_engagement_rate,
    ROUND(c.channel_avg_engagement,2) AS channel_avg_engagement,
    ROUND(y.engagement_rate - c.channel_avg_engagement, 2) AS delta
FROM youtube_engagement y
JOIN channel_avg c ON y.channel_title = c.channel_title
WHERE y.engagement_rate > c.channel_avg_engagement
ORDER BY delta DESC
LIMIT 20;


-- Query 23: Most consistent channels (lowest engagement variation)
SELECT
    channel_title,
    COUNT(*)                                   AS video_count,
    ROUND(AVG(engagement_rate), 4)             AS avg_engagement,
    -- SQLite does not have STDDEV; we compute variance manually
    ROUND(
        SUM((engagement_rate - (
                SELECT AVG(engagement_rate)
                FROM youtube_engagement e2
                WHERE e2.channel_title = youtube_engagement.channel_title
            )) * (engagement_rate - (
                SELECT AVG(engagement_rate)
                FROM youtube_engagement e3
                WHERE e3.channel_title = youtube_engagement.channel_title
            ))) / COUNT(*),
        4
    ) AS engagement_variance
FROM youtube_engagement
GROUP BY channel_title
HAVING video_count >= 5
ORDER BY engagement_variance ASC   -- lower = more consistent
LIMIT 10;

-- MySQL alternative for Query 23:
-- REPLACE the variance calculation with: ROUND(STDDEV(engagement_rate), 4) AS stddev_engagement


-- Query 24: Median-like engagement analysis
-- SQLite median approximation using offset trick
WITH ranked AS (
    SELECT
        engagement_rate,
        ROW_NUMBER() OVER (ORDER BY engagement_rate) AS rn,
        COUNT(*) OVER () AS total_count
    FROM youtube_engagement
)
SELECT
    ROUND(AVG(engagement_rate), 4) AS median_engagement_rate
FROM ranked
WHERE rn IN (
    (total_count + 1) / 2,
    (total_count + 2) / 2
);

-- MySQL alternative for Query 24 (requires MySQL 8.0+):
-- SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY engagement_rate) AS median_engagement
-- FROM youtube_engagement;


-- Query 25: Reusable channel performance summary CTE
-- Use this CTE as a starting point for custom channel dashboards
WITH channel_summary AS (
    SELECT
        channel_title,
        COUNT(*)                         AS total_videos,
        SUM(view_count)                  AS total_views,
        SUM(like_count)                  AS total_likes,
        SUM(comment_count)               AS total_comments,
        ROUND(AVG(view_count), 0)        AS avg_views,
        ROUND(AVG(engagement_rate), 4)   AS avg_engagement_rate,
        ROUND(MAX(engagement_rate), 4)   AS max_engagement_rate,
        SUM(CASE WHEN performance_category = 'Viral' THEN 1 ELSE 0 END) AS viral_videos,
        SUM(CASE WHEN performance_category = 'High'  THEN 1 ELSE 0 END) AS high_videos,
        SUM(CASE WHEN performance_category = 'Low'   THEN 1 ELSE 0 END) AS low_videos
    FROM youtube_engagement
    GROUP BY channel_title
)
SELECT *
FROM channel_summary
ORDER BY avg_engagement_rate DESC;
