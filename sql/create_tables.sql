-- ============================================================
-- sql/create_tables.sql
-- ============================================================
-- Purpose:
--   DDL to create the youtube_engagement table and all indexes.
--   This file documents the schema — the actual table is also
--   created automatically by src/database.py using SQLAlchemy.
--
-- To run manually (SQLite):
--   sqlite3 data/social_media.db < sql/create_tables.sql
-- ============================================================


-- Drop the table if it already exists (clean slate)
DROP TABLE IF EXISTS youtube_engagement;


-- ── Main fact table ──────────────────────────────────────────
CREATE TABLE youtube_engagement (

    -- Identifiers
    video_id               TEXT    PRIMARY KEY,   -- unique YouTube video ID
    title                  TEXT    NOT NULL,
    description            TEXT,
    channel_id             TEXT,
    channel_title          TEXT,

    -- Publication details
    published_at           TEXT,                  -- stored as ISO 8601 string
    publication_date       TEXT,                  -- YYYY-MM-DD (local timezone)
    publication_year       INTEGER,
    publication_month      INTEGER,               -- 1–12
    publication_month_name TEXT,                  -- "January"
    publication_day        INTEGER,               -- 1–31
    publication_day_name   TEXT,                  -- "Monday"
    publication_hour       INTEGER,               -- 0–23 (local timezone)
    posting_time_group     TEXT,                  -- "Morning", "Evening", etc.

    -- Content details
    category_id            TEXT,
    duration               TEXT,                  -- original ISO 8601 string
    duration_seconds       INTEGER DEFAULT 0,
    video_duration_seconds INTEGER DEFAULT 0,
    video_duration_minutes REAL    DEFAULT 0,
    duration_category      TEXT,                  -- "Short", "Medium", "Long"
    definition             TEXT,                  -- "hd" or "sd"
    caption_status         TEXT,
    live_broadcast_content TEXT,
    tags                   TEXT,
    data_source            TEXT,                  -- "API" or "SYNTHETIC_SAMPLE"

    -- Raw engagement counts
    view_count             INTEGER DEFAULT 0,
    like_count             INTEGER DEFAULT 0,
    comment_count          INTEGER DEFAULT 0,
    favorite_count         INTEGER DEFAULT 0,

    -- Calculated engagement metrics
    total_interactions     INTEGER DEFAULT 0,
    engagement_rate        REAL    DEFAULT 0,     -- percentage
    like_rate              REAL    DEFAULT 0,
    comment_rate           REAL    DEFAULT 0,

    -- Velocity metrics (per-day averages)
    video_age_days         INTEGER DEFAULT 0,
    views_per_day          REAL    DEFAULT 0,
    likes_per_day          REAL    DEFAULT 0,
    comments_per_day       REAL    DEFAULT 0,

    -- Classification
    performance_category   TEXT,                  -- "Low", "Average", "High", "Viral"
    is_outlier             INTEGER DEFAULT 0      -- 0 = False, 1 = True (SQLite has no BOOL)
);


-- ── Indexes ──────────────────────────────────────────────────
-- Indexes speed up filtering, grouping, and sorting in queries.
-- They are especially important for the Power BI direct query mode.

CREATE INDEX IF NOT EXISTS idx_channel_title
    ON youtube_engagement (channel_title);

CREATE INDEX IF NOT EXISTS idx_published_at
    ON youtube_engagement (published_at);

CREATE INDEX IF NOT EXISTS idx_publication_day_name
    ON youtube_engagement (publication_day_name);

CREATE INDEX IF NOT EXISTS idx_engagement_rate
    ON youtube_engagement (engagement_rate);

CREATE INDEX IF NOT EXISTS idx_performance_category
    ON youtube_engagement (performance_category);

CREATE INDEX IF NOT EXISTS idx_duration_category
    ON youtube_engagement (duration_category);

CREATE INDEX IF NOT EXISTS idx_publication_hour
    ON youtube_engagement (publication_hour);

CREATE INDEX IF NOT EXISTS idx_posting_time_group
    ON youtube_engagement (posting_time_group);
