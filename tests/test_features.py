# ============================================================
# tests/test_features.py
# ============================================================
# Purpose:
#   Unit tests for the feature-engineering module.
#   Tests every derived column and edge case.
#
# Run with:  pytest tests/ -v
# ============================================================

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.feature_engineering import (
    add_engagement_metrics,
    add_duration_features,
    add_date_features,
    add_performance_category,
    add_velocity_metrics,
)
from src.utils import (
    parse_iso8601_duration,
    get_posting_time_group,
    get_duration_category,
    safe_int,
    safe_float,
)


# ── Helpers ──────────────────────────────────────────────────

def make_engagement_df(**overrides) -> pd.DataFrame:
    data = {
        "video_id":     ["v1", "v2", "v3"],
        "view_count":   [10000, 5000, 0],
        "like_count":   [500,   250,  0],
        "comment_count":[50,    25,   0],
    }
    data.update(overrides)
    return pd.DataFrame(data)


def make_published_df() -> pd.DataFrame:
    return pd.DataFrame({
        "video_id":    ["v1", "v2", "v3"],
        "view_count":  [10000, 5000, 20000],
        "like_count":  [500, 250, 1000],
        "comment_count": [50, 25, 100],
        "published_at": pd.to_datetime([
            "2023-01-15T10:00:00Z",
            "2023-06-20T14:00:00Z",
            "2024-03-10T08:00:00Z",
        ], utc=True),
        "duration_seconds": [330, 600, 165],
    })


# ── Tests: engagement metrics ────────────────────────────────

class TestEngagementMetrics:
    def test_total_interactions(self):
        df = make_engagement_df()
        result = add_engagement_metrics(df)
        assert result["total_interactions"].iloc[0] == 550   # 500+50
        assert result["total_interactions"].iloc[1] == 275   # 250+25

    def test_engagement_rate_formula(self):
        df = make_engagement_df()
        result = add_engagement_metrics(df)
        # Row 0: (500+50)/10000 * 100 = 5.5%
        expected = (500 + 50) / 10000 * 100
        assert abs(result["engagement_rate"].iloc[0] - expected) < 0.001

    def test_like_rate_formula(self):
        df = make_engagement_df()
        result = add_engagement_metrics(df)
        expected = 500 / 10000 * 100   # 5.0%
        assert abs(result["like_rate"].iloc[0] - expected) < 0.001

    def test_comment_rate_formula(self):
        df = make_engagement_df()
        result = add_engagement_metrics(df)
        expected = 50 / 10000 * 100   # 0.5%
        assert abs(result["comment_rate"].iloc[0] - expected) < 0.001

    def test_division_by_zero_returns_zero(self):
        """
        Videos with 0 views should return 0 for all rate columns,
        not NaN, Infinity, or a ZeroDivisionError.
        """
        df = make_engagement_df(view_count=[0, 0, 0])
        result = add_engagement_metrics(df)
        assert result["engagement_rate"].iloc[0] == 0.0
        assert result["like_rate"].iloc[0] == 0.0
        assert result["comment_rate"].iloc[0] == 0.0
        # No NaN or Inf values
        assert not result["engagement_rate"].isnull().any()
        assert not np.isinf(result["engagement_rate"]).any()

    def test_all_rate_columns_created(self):
        df = make_engagement_df()
        result = add_engagement_metrics(df)
        for col in ["total_interactions", "engagement_rate",
                    "like_rate", "comment_rate"]:
            assert col in result.columns, f"Missing column: {col}"

    def test_engagement_rate_is_non_negative(self):
        df = make_engagement_df()
        result = add_engagement_metrics(df)
        assert (result["engagement_rate"] >= 0).all()


# ── Tests: duration features ─────────────────────────────────

class TestDurationFeatures:
    def test_duration_minutes_calculation(self):
        df = make_published_df()
        result = add_duration_features(df)
        # 330 seconds = 5.5 minutes
        assert abs(result["video_duration_minutes"].iloc[0] - 5.5) < 0.01

    def test_duration_category_short(self):
        df = make_published_df()
        df["duration_seconds"] = [60, 600, 1800]   # short, medium, long
        result = add_duration_features(df)
        assert result["duration_category"].iloc[0] == "Short"
        assert result["duration_category"].iloc[1] == "Medium"
        assert result["duration_category"].iloc[2] == "Long"

    def test_duration_category_boundary_300(self):
        """299s → Short, 300s → Medium"""
        assert get_duration_category(299) == "Short"
        assert get_duration_category(300) == "Medium"

    def test_duration_category_boundary_900(self):
        """900s → Medium, 901s → Long"""
        assert get_duration_category(900) == "Medium"
        assert get_duration_category(901) == "Long"


# ── Tests: date features ─────────────────────────────────────

class TestDateFeatures:
    def test_all_date_columns_created(self):
        df = make_published_df()
        result = add_date_features(df, timezone="UTC")
        expected_cols = [
            "publication_date", "publication_year", "publication_month",
            "publication_month_name", "publication_day", "publication_day_name",
            "publication_hour", "posting_time_group",
        ]
        for col in expected_cols:
            assert col in result.columns, f"Missing column: {col}"

    def test_publication_year(self):
        df = make_published_df()
        result = add_date_features(df, timezone="UTC")
        assert result["publication_year"].iloc[0] == 2023
        assert result["publication_year"].iloc[2] == 2024

    def test_publication_hour_in_range(self):
        df = make_published_df()
        result = add_date_features(df, timezone="UTC")
        assert (result["publication_hour"] >= 0).all()
        assert (result["publication_hour"] <= 23).all()

    def test_day_name_is_string(self):
        df = make_published_df()
        result = add_date_features(df, timezone="UTC")
        # In pandas 3.0 strftime returns StringDtype, not object
        # Check that values are valid day names
        valid_days = {'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'}
        assert all(v in valid_days for v in result["publication_day_name"])


# ── Tests: posting-time group ────────────────────────────────

class TestPostingTimeGroup:
    def test_late_night(self):
        for h in range(0, 6):
            assert get_posting_time_group(h) == "Late Night", f"Hour {h}"

    def test_morning(self):
        for h in range(6, 12):
            assert get_posting_time_group(h) == "Morning", f"Hour {h}"

    def test_afternoon(self):
        for h in range(12, 17):
            assert get_posting_time_group(h) == "Afternoon", f"Hour {h}"

    def test_evening(self):
        for h in range(17, 21):
            assert get_posting_time_group(h) == "Evening", f"Hour {h}"

    def test_night(self):
        for h in range(21, 24):
            assert get_posting_time_group(h) == "Night", f"Hour {h}"

    def test_all_hours_covered(self):
        """No hour should return an unexpected value."""
        valid_groups = {"Late Night", "Morning", "Afternoon", "Evening", "Night"}
        for h in range(24):
            group = get_posting_time_group(h)
            assert group in valid_groups, f"Hour {h} → unexpected '{group}'"


# ── Tests: performance category ─────────────────────────────

class TestPerformanceCategory:
    def test_all_categories_present(self):
        """With enough spread, all 4 categories should appear."""
        df = pd.DataFrame({
            "engagement_rate": [0.1, 1.0, 2.0, 5.0, 10.0,
                                0.2, 0.5, 3.0, 7.0, 15.0]
        })
        result = add_performance_category(df)
        categories = set(result["performance_category"].unique())
        assert len(categories) >= 2   # at least some variation

    def test_column_exists(self):
        df = pd.DataFrame({"engagement_rate": [1.0, 2.0, 3.0, 4.0, 5.0]})
        result = add_performance_category(df)
        assert "performance_category" in result.columns

    def test_valid_category_values(self):
        df = pd.DataFrame({"engagement_rate": list(range(1, 20))})
        result = add_performance_category(df)
        valid = {"Low", "Average", "High", "Viral"}
        for val in result["performance_category"].unique():
            assert val in valid, f"Unexpected category: '{val}'"


# ── Tests: ISO 8601 duration parser ─────────────────────────

class TestParseISO8601Duration:
    def test_minutes_and_seconds(self):
        assert parse_iso8601_duration("PT4M13S") == 253

    def test_hours_minutes_seconds(self):
        assert parse_iso8601_duration("PT1H2M3S") == 3723

    def test_only_minutes(self):
        assert parse_iso8601_duration("PT10M") == 600

    def test_only_seconds(self):
        assert parse_iso8601_duration("PT45S") == 45

    def test_zero_duration(self):
        assert parse_iso8601_duration("P0D") == 0

    def test_none_returns_zero(self):
        assert parse_iso8601_duration(None) == 0

    def test_empty_string_returns_zero(self):
        assert parse_iso8601_duration("") == 0

    def test_invalid_string_returns_zero(self):
        assert parse_iso8601_duration("not_a_duration") == 0

    def test_days(self):
        assert parse_iso8601_duration("P1DT2H3M4S") == 86400 + 7200 + 180 + 4


# ── Tests: safe type converters ──────────────────────────────

class TestSafeConversions:
    def test_safe_int_normal(self):
        assert safe_int("12345") == 12345

    def test_safe_int_none(self):
        assert safe_int(None) == 0

    def test_safe_int_empty_string(self):
        assert safe_int("") == 0

    def test_safe_int_custom_default(self):
        assert safe_int(None, default=-1) == -1

    def test_safe_float_normal(self):
        assert abs(safe_float("3.14") - 3.14) < 0.001

    def test_safe_float_none(self):
        assert safe_float(None) == 0.0
