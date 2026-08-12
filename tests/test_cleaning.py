# ============================================================
# tests/test_cleaning.py
# ============================================================
# Purpose:
#   Unit tests for the data-cleaning pipeline.
#   Run with:  pytest tests/ -v
#
# Each test creates a small dummy DataFrame, runs one cleaning
# function, and asserts the expected result.
# ============================================================

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Make sure the project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.clean_data import (
    standardise_column_names,
    remove_exact_duplicates,
    remove_duplicate_video_ids,
    convert_numeric_columns,
    remove_negative_values,
    parse_published_at,
    clean_text_columns,
    handle_missing_titles,
    parse_duration_column,
    flag_outliers,
)


# ── Helpers ──────────────────────────────────────────────────

def make_sample_df(**overrides) -> pd.DataFrame:
    """Create a minimal valid DataFrame for testing."""
    data = {
        "video_id":      ["abc123", "def456", "ghi789"],
        "title":         ["Video A", "Video B", "Video C"],
        "channel_title": ["Channel 1", "Channel 2", "Channel 3"],
        "published_at":  [
            "2023-01-15T10:00:00Z",
            "2023-06-20T14:00:00Z",
            "2024-03-10T08:00:00Z",
        ],
        "view_count":    [10000, 5000, 20000],
        "like_count":    [500, 250, 1000],
        "comment_count": [50, 25, 100],
        "favorite_count":[0, 0, 0],
        "duration":      ["PT5M30S", "PT10M", "PT2M45S"],
    }
    data.update(overrides)
    return pd.DataFrame(data)


# ── Tests: column names ──────────────────────────────────────

class TestStandardiseColumnNames:
    def test_converts_to_lowercase(self):
        # Our function converts spaces/dashes to underscores and lowercases
        # CamelCase without separators becomes one word (e.g. videoid)
        df = pd.DataFrame({"View Count": [1], "Like-Count": [1]})
        result = standardise_column_names(df)
        assert "view_count" in result.columns
        assert "like_count" in result.columns

    def test_handles_spaces_in_column_names(self):
        df = pd.DataFrame({"View Count": [1], "Like Count": [1]})
        result = standardise_column_names(df)
        assert "view_count" in result.columns
        assert "like_count" in result.columns

    def test_no_uppercase_remaining(self):
        df = make_sample_df()
        result = standardise_column_names(df)
        for col in result.columns:
            assert col == col.lower(), f"Column '{col}' is not lowercase"


# ── Tests: duplicate removal ─────────────────────────────────

class TestRemoveDuplicates:
    def test_removes_exact_duplicate_rows(self):
        df = make_sample_df()
        # Add an exact duplicate of row 0
        df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
        assert len(df) == 4

        result = remove_exact_duplicates(df)
        assert len(result) == 3

    def test_removes_duplicate_video_ids(self):
        df = make_sample_df()
        # Make row 1 have the same video_id as row 0 but different values
        df.loc[1, "video_id"] = "abc123"
        df.loc[1, "view_count"] = 99999   # different, so not exact duplicate

        result = remove_duplicate_video_ids(df)
        assert len(result) == 2
        assert result["video_id"].nunique() == 2

    def test_keeps_all_rows_when_no_duplicates(self):
        df = make_sample_df()
        result = remove_exact_duplicates(df)
        assert len(result) == 3


# ── Tests: numeric conversion ────────────────────────────────

class TestConvertNumericColumns:
    def test_converts_string_counts_to_int(self):
        df = make_sample_df(
            view_count=["10000", "5000", "20000"],
            like_count=["500", "250", "1000"],
        )
        result = convert_numeric_columns(df)
        assert result["view_count"].dtype in [int, np.int64, np.int32]
        assert result["like_count"].dtype  in [int, np.int64, np.int32]

    def test_fills_missing_like_count_with_zero(self):
        df = make_sample_df(like_count=[None, 250, 1000])
        result = convert_numeric_columns(df)
        assert result["like_count"].iloc[0] == 0

    def test_drops_rows_with_missing_view_count(self):
        df = make_sample_df(view_count=[10000, None, 20000])
        result = convert_numeric_columns(df)
        # Row with None view_count should be removed
        assert len(result) == 2

    def test_handles_mixed_types(self):
        df = make_sample_df(
            comment_count=["100", 0, np.nan]
        )
        result = convert_numeric_columns(df)
        assert result["comment_count"].iloc[0] == 100
        assert result["comment_count"].iloc[2] == 0


# ── Tests: negative value removal ───────────────────────────

class TestRemoveNegativeValues:
    def test_removes_negative_view_counts(self):
        df = make_sample_df(view_count=[-100, 5000, 20000])
        result = remove_negative_values(df)
        assert len(result) == 2
        assert (result["view_count"] >= 0).all()

    def test_removes_negative_like_counts(self):
        df = make_sample_df(like_count=[500, -1, 1000])
        result = remove_negative_values(df)
        assert len(result) == 2

    def test_keeps_zero_counts(self):
        df = make_sample_df(like_count=[0, 0, 0])
        result = remove_negative_values(df)
        assert len(result) == 3


# ── Tests: date parsing ──────────────────────────────────────

class TestParsePublishedAt:
    def test_converts_to_datetime(self):
        df = make_sample_df()
        result = parse_published_at(df)
        assert pd.api.types.is_datetime64_any_dtype(result["published_at"])

    def test_removes_invalid_dates(self):
        df = make_sample_df(
            published_at=["2023-01-15T10:00:00Z", "NOT_A_DATE", "2024-03-10T08:00:00Z"]
        )
        result = parse_published_at(df)
        assert len(result) == 2

    def test_result_is_timezone_aware(self):
        df = make_sample_df()
        result = parse_published_at(df)
        assert result["published_at"].dt.tz is not None


# ── Tests: text cleaning ─────────────────────────────────────

class TestCleanTextColumns:
    def test_strips_whitespace(self):
        df = make_sample_df(title=["  Video A  ", "Video B", "  Video C"])
        result = clean_text_columns(df)
        assert result["title"].iloc[0] == "Video A"
        assert result["title"].iloc[2] == "Video C"

    def test_replaces_nan_strings(self):
        df = make_sample_df(title=["Video A", "nan", "Video C"])
        result = clean_text_columns(df)
        # "nan" string should be replaced with actual NaN
        assert pd.isna(result["title"].iloc[1])


# ── Tests: missing titles ────────────────────────────────────

class TestHandleMissingTitles:
    def test_fills_missing_title(self):
        df = make_sample_df(title=[None, "Video B", "Video C"])
        result = handle_missing_titles(df)
        assert result["title"].iloc[0] == "[Title Unavailable]"

    def test_fills_missing_channel_title(self):
        df = make_sample_df(channel_title=[None, "Channel 2", "Channel 3"])
        result = handle_missing_titles(df)
        assert result["channel_title"].iloc[0] == "[Unknown Channel]"


# ── Tests: duration parsing ──────────────────────────────────

class TestParseDurationColumn:
    def test_parses_valid_duration(self):
        df = make_sample_df(duration=["PT5M30S", "PT10M", "PT2M45S"])
        result = parse_duration_column(df)
        assert result["duration_seconds"].iloc[0] == 330   # 5*60+30
        assert result["duration_seconds"].iloc[1] == 600   # 10*60
        assert result["duration_seconds"].iloc[2] == 165   # 2*60+45

    def test_handles_missing_duration(self):
        df = make_sample_df(duration=[None, "PT10M", "PT2M45S"])
        result = parse_duration_column(df)
        assert result["duration_seconds"].iloc[0] == 0

    def test_handles_zero_duration(self):
        df = make_sample_df(duration=["P0D", "PT10M", "PT2M45S"])
        result = parse_duration_column(df)
        assert result["duration_seconds"].iloc[0] == 0


# ── Tests: outlier flagging ──────────────────────────────────

class TestFlagOutliers:
    def test_adds_is_outlier_column(self):
        df = make_sample_df()
        result = flag_outliers(df)
        assert "is_outlier" in result.columns

    def test_outlier_is_boolean(self):
        df = make_sample_df()
        result = flag_outliers(df)
        assert result["is_outlier"].dtype == bool

    def test_extreme_value_flagged(self):
        # Build a 9-row DataFrame directly to avoid size mismatch with make_sample_df
        views = [100, 200, 150, 120, 180, 130, 200, 110, 100_000_000]
        n = len(views)
        df = pd.DataFrame({
            "video_id":      [f"v{i}" for i in range(n)],
            "title":         [f"T{i}" for i in range(n)],
            "channel_title": ["C"] * n,
            "published_at":  ["2023-01-15T10:00:00Z"] * n,
            "view_count":    views,
            "like_count":    [10] * n,
            "comment_count": [5] * n,
            "duration":      ["PT5M"] * n,
        })
        result = flag_outliers(df)
        # The last row with 100M views must be flagged
        assert result["is_outlier"].iloc[-1] == True

    def test_normal_values_not_flagged(self):
        df = make_sample_df(view_count=[9000, 10000, 11000])
        result = flag_outliers(df)
        assert result["is_outlier"].sum() == 0
