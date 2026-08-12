#!/usr/bin/env python
# ============================================================
# main.py — Command-Line Interface
# ============================================================
# Purpose:
#   Single entry point for all project commands.
#   Run this file with different sub-commands to execute
#   each stage of the pipeline.
#
# Quick reference
# ───────────────
#   python main.py generate-sample
#   python main.py collect --query "data analytics" --max-results 100
#   python main.py collect --channel-id UC_XXXXXXXX --max-results 50
#   python main.py clean
#   python main.py load-database
#   python main.py analyze
#   python main.py run-all
# ============================================================

import argparse
import sys
from pathlib import Path

# Force UTF-8 encoding for stdout and stderr on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Ensure the project root is on the Python path ───────────
# This lets us do "from src.xxx import yyy" from anywhere
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils import get_logger

logger = get_logger("main")


# ════════════════════════════════════════════════════════════
# Command handlers
# ════════════════════════════════════════════════════════════

def cmd_generate_sample(args) -> None:
    """Generate the synthetic 200-row sample dataset."""
    from src.generate_sample import generate_sample_data
    from src.config import settings

    logger.info("Generating synthetic sample dataset...")
    df = generate_sample_data(n=200)

    # Also copy to raw/ so the clean pipeline can pick it up
    import shutil
    raw_path = settings["RAW_DATA_PATH"]
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    sample_path = settings["SAMPLE_DATA_PATH"]
    shutil.copy(sample_path, raw_path)

    print(f"\n[OK] Sample data generated:")
    print(f"   {sample_path}  ({len(df)} rows)")
    print(f"   Also copied to: {raw_path}")
    print("\n[NOTE] This is SYNTHETIC data -- not real YouTube results.\n")


def cmd_collect(args) -> None:
    """Collect real data from the YouTube API."""
    from src.config import validate_api_key
    from src.collect_data import (
        collect_by_query,
        collect_by_channel,
        save_raw_data,
    )

    if not validate_api_key():
        print("\n[ERROR] No valid YouTube API key found.")
        print("   Steps to fix:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your YouTube API key to YOUTUBE_API_KEY")
        print("   3. Re-run this command")
        print("\n   Alternative: python main.py generate-sample\n")
        sys.exit(1)

    if args.channel_id:
        df = collect_by_channel(
            channel_id=args.channel_id,
            max_results=args.max_results,
        )
    elif args.query:
        df = collect_by_query(
            query=args.query,
            max_results=args.max_results,
        )
    else:
        print("[ERROR] Provide either --query or --channel-id")
        sys.exit(1)

    if df.empty:
        print("[ERROR] No data collected. Check your API key and network connection.")
        sys.exit(1)

    path = save_raw_data(df)
    print(f"\n✅ Raw data saved: {path}  ({len(df)} rows)\n")


def cmd_clean(args) -> None:
    """Run the data-cleaning + feature-engineering pipeline."""
    from src.clean_data import clean_data
    from src.feature_engineering import engineer_features
    from src.config import settings
    import pandas as pd

    logger.info("Running cleaning pipeline...")
    cleaned = clean_data()

    logger.info("Running feature engineering...")
    enriched = engineer_features(cleaned)

    out_path = settings["PROCESSED_DATA_PATH"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(out_path, index=False, encoding="utf-8")

    print(f"\n[OK] Processed data saved: {out_path}  ({len(enriched)} rows)")
    print(f"   Columns: {enriched.shape[1]}\n")


def cmd_load_database(args) -> None:
    """Load processed CSV into SQLite/MySQL."""
    from src.database import load_data_to_database, add_indexes, get_engine

    logger.info("Loading data into database...")
    count = load_data_to_database()
    engine = get_engine()
    add_indexes(engine)

    print(f"\n[OK] Database loaded: {count} rows inserted")
    from src.config import settings
    print(f"   Database path: {settings['SQLITE_DATABASE_PATH']}\n")


def cmd_analyze(args) -> None:
    """Generate the business-insights report."""
    from src.insights import generate_insights
    from src.config import settings

    logger.info("Generating business insights report...")
    generate_insights()

    report_path = settings["REPORTS_DIR"] / "business_insights.md"
    print(f"\n[OK] Business insights report saved: {report_path}\n")


def cmd_run_all(args) -> None:
    """
    Full pipeline: generate-sample → clean → load-db → analyze.
    Uses sample data when no API key is available.
    """
    from src.config import validate_api_key, settings
    from src.generate_sample import generate_sample_data
    from src.clean_data import clean_data
    from src.feature_engineering import engineer_features
    from src.database import load_data_to_database, add_indexes, get_engine
    from src.insights import generate_insights
    import shutil

    print("\n" + "=" * 60)
    print("  SOCIAL MEDIA ENGAGEMENT ANALYTICS — FULL PIPELINE")
    print("=" * 60)

    # Step 1: data source
    if validate_api_key():
        print("\nStep 1/5 ── API key detected — using real YouTube data")
        print("         (If you prefer sample data, remove the key from .env)")
        # Data was already collected by `collect` command
        raw_path = settings["RAW_DATA_PATH"]
        if not raw_path.exists():
            print(f"  Raw data not found at {raw_path}")
            print("  Run:  python main.py collect --query 'data analytics'")
            print("  Falling back to sample data...\n")
            _copy_sample_to_raw(settings)
    else:
        print("\nStep 1/5 ── No API key — generating synthetic sample data")
        df = generate_sample_data(n=200)
        _copy_sample_to_raw(settings)

    # Step 2: clean
    print("\nStep 2/5 ── Cleaning & validating data...")
    cleaned = clean_data()

    # Step 3: feature engineering
    print("\nStep 3/5 ── Engineering features...")
    enriched = engineer_features(cleaned)
    out_path = settings["PROCESSED_DATA_PATH"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(out_path, index=False, encoding="utf-8")
    print(f"           Processed data: {out_path}  ({len(enriched)} rows)")

    # Step 4: database
    print("\nStep 4/5 ── Loading database...")
    count  = load_data_to_database()
    engine = get_engine()
    add_indexes(engine)
    print(f"           Rows inserted: {count}")

    # Step 5: insights
    print("\nStep 5/5 ── Generating business insights...")
    generate_insights()
    print(f"           Report: {settings['REPORTS_DIR'] / 'business_insights.md'}")

    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Processed CSV : {out_path}")
    print(f"  Database      : {settings['SQLITE_DATABASE_PATH']}")
    print(f"  Insights      : {settings['REPORTS_DIR'] / 'business_insights.md'}")
    print("\n  Open the CSV in Power BI:")
    print("    Home → Get Data → Text/CSV → select processed CSV")
    print("=" * 60 + "\n")


def _copy_sample_to_raw(settings) -> None:
    """Copy sample CSV to raw/ directory."""
    import shutil
    sample = settings["SAMPLE_DATA_PATH"]
    raw    = settings["RAW_DATA_PATH"]
    raw.parent.mkdir(parents=True, exist_ok=True)
    if sample.exists():
        shutil.copy(sample, raw)
    else:
        from src.generate_sample import generate_sample_data
        generate_sample_data()
        shutil.copy(sample, raw)


# ════════════════════════════════════════════════════════════
# Argument parser
# ════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="Social Media Engagement Analytics Dashboard — CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py generate-sample
  python main.py collect --query "data analytics" --max-results 100
  python main.py collect --channel-id UCxxxxxx --max-results 50
  python main.py clean
  python main.py load-database
  python main.py analyze
  python main.py run-all
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate-sample
    subparsers.add_parser(
        "generate-sample",
        help="Create 200-row synthetic sample dataset",
    )

    # collect
    p_collect = subparsers.add_parser(
        "collect",
        help="Collect data from YouTube API",
    )
    p_collect.add_argument("--query",      type=str, help="Search keyword")
    p_collect.add_argument("--channel-id", type=str, help="YouTube channel ID")
    p_collect.add_argument(
        "--max-results", type=int, default=50,
        help="Maximum videos to collect (default: 50)",
    )

    # clean
    subparsers.add_parser(
        "clean",
        help="Run cleaning + feature engineering pipeline",
    )

    # load-database
    subparsers.add_parser(
        "load-database",
        help="Load processed CSV into SQLite/MySQL",
    )

    # analyze
    subparsers.add_parser(
        "analyze",
        help="Generate business-insights report",
    )

    # run-all
    subparsers.add_parser(
        "run-all",
        help="Run the complete pipeline end-to-end",
    )

    return parser


# ════════════════════════════════════════════════════════════
# Entry point
# ════════════════════════════════════════════════════════════

def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    dispatch = {
        "generate-sample": cmd_generate_sample,
        "collect":         cmd_collect,
        "clean":           cmd_clean,
        "load-database":   cmd_load_database,
        "analyze":         cmd_analyze,
        "run-all":         cmd_run_all,
    }

    handler = dispatch.get(args.command)
    if handler:
        try:
            handler(args)
        except FileNotFoundError as e:
            print(f"\n❌ File not found: {e}\n")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
