# ============================================================
# src/database.py
# ============================================================
# Purpose:
#   Loads the processed CSV into SQLite (or MySQL) using
#   SQLAlchemy so that SQL queries can be run directly.
#
# Called by:  python main.py load-database
# ============================================================

import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text, Index
from sqlalchemy.exc import SQLAlchemyError

from src.config import settings
from src.utils import get_logger, ensure_directory

logger = get_logger(__name__)

TABLE_NAME = "youtube_engagement"


def get_engine():
    """
    Create and return a SQLAlchemy engine based on the
    DATABASE_TYPE setting in .env.

    SQLite (default):
        A file-based database stored at data/social_media.db
        No server required — perfect for beginners.

    MySQL (optional):
        Requires a running MySQL server.
        Set DATABASE_TYPE=mysql in .env and fill MySQL credentials.
    """
    db_type = settings["DATABASE_TYPE"]

    if db_type == "mysql":
        user     = settings["MYSQL_USER"]
        password = settings["MYSQL_PASSWORD"]
        host     = settings["MYSQL_HOST"]
        port     = settings["MYSQL_PORT"]
        database = settings["MYSQL_DATABASE"]
        url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        logger.info(f"Connecting to MySQL: {host}:{port}/{database}")
    else:
        # SQLite — create the directory if it doesn't exist
        db_path = settings["SQLITE_DATABASE_PATH"]
        ensure_directory(Path(db_path).parent)
        url = f"sqlite:///{db_path}"
        logger.info(f"Using SQLite database: {db_path}")

    return create_engine(url, echo=False)


def load_data_to_database(csv_path=None) -> int:
    """
    Read the processed CSV and insert all rows into the
    youtube_engagement table.

    Parameters
    ----------
    csv_path : str | Path | None
        Path to the cleaned CSV. Defaults to the processed-data path.

    Returns
    -------
    int — number of rows inserted
    """
    in_path = Path(csv_path or settings["PROCESSED_DATA_PATH"])

    if not in_path.exists():
        raise FileNotFoundError(
            f"Processed data file not found: {in_path}\n"
            "Run:  python main.py clean   (or  python main.py run-all)"
        )

    logger.info(f"Reading processed data: {in_path}")
    df = pd.read_csv(in_path, low_memory=False)
    logger.info(f"  Loaded {len(df)} rows from CSV")

    # Prepare columns for the database
    df = _prepare_for_db(df)

    engine = get_engine()

    try:
        with engine.connect() as conn:
            # Create the table (replaces it if it already exists)
            _create_table(conn, engine)

            # if_exists='replace' drops and recreates the table
            # if_exists='append' adds rows without recreating
            # We use 'replace' for simplicity; use 'append' for
            # incremental updates in production
            df.to_sql(
                TABLE_NAME,
                con=engine,
                if_exists="replace",   # change to "append" for incremental loads
                index=False,
                chunksize=500,         # write in batches for large datasets
            )

            result = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
            row_count = result.scalar()
            logger.info(f"  Rows in database: {row_count}")

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise

    logger.info("  Database load complete ✓")
    return row_count


def query_database(sql: str) -> pd.DataFrame:
    """
    Run a SQL query and return results as a DataFrame.

    Parameters
    ----------
    sql : str — SQL query string

    Returns
    -------
    pd.DataFrame
    """
    engine = get_engine()
    try:
        return pd.read_sql(sql, engine)
    except SQLAlchemyError as e:
        logger.error(f"Query failed: {e}")
        raise


# ── Private helpers ──────────────────────────────────────────

def _prepare_for_db(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure the DataFrame has the correct types before loading.
    SQLAlchemy will infer types, but being explicit avoids issues.
    """
    # Convert date column to string (SQLite stores dates as TEXT)
    if "publication_date" in df.columns:
        df["publication_date"] = df["publication_date"].astype(str)

    # Convert boolean outlier flag to integer (SQLite has no bool)
    if "is_outlier" in df.columns:
        df["is_outlier"] = df["is_outlier"].astype(int)

    return df


def _create_table(conn, engine) -> None:
    """
    Create the youtube_engagement table with indexes.
    This is called before pandas to_sql so indexes can be
    defined explicitly.
    """
    # Drop existing table to ensure a clean load
    conn.execute(text(f"DROP TABLE IF EXISTS {TABLE_NAME}"))
    conn.commit()
    # Table will be created by pandas to_sql with inferred types.
    # Indexes are added afterwards via SQLAlchemy Core.


def add_indexes(engine) -> None:
    """
    Add performance indexes after the table is created.
    Indexes speed up GROUP BY and WHERE queries in Power BI
    and SQL analysis.
    """
    try:
        with engine.connect() as conn:
            # SQLite CREATE INDEX syntax
            index_definitions = [
                f"CREATE INDEX IF NOT EXISTS idx_channel_title   ON {TABLE_NAME}(channel_title);",
                f"CREATE INDEX IF NOT EXISTS idx_published_at    ON {TABLE_NAME}(published_at);",
                f"CREATE INDEX IF NOT EXISTS idx_day_name        ON {TABLE_NAME}(publication_day_name);",
                f"CREATE INDEX IF NOT EXISTS idx_engagement_rate ON {TABLE_NAME}(engagement_rate);",
            ]
            for stmt in index_definitions:
                conn.execute(text(stmt))
            conn.commit()
            logger.info("  Indexes created ✓")
    except Exception as e:
        logger.warning(f"Could not create indexes (non-fatal): {e}")


if __name__ == "__main__":
    count = load_data_to_database()
    print(f"Database load complete — {count} rows inserted")
