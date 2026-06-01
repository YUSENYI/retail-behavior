from __future__ import annotations

import argparse
from pathlib import Path
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC = BACKEND_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from models.database import DATABASE_URL, init_database  # noqa: E402


def create_database_if_needed(database_url: str) -> None:
    url = make_url(database_url)
    database = url.database
    if not database:
        raise SystemExit("DATABASE_URL must include a database name.")

    server_url = url.set(database=None)
    engine = create_engine(server_url, pool_pre_ping=True)
    with engine.connect() as connection:
        connection.execution_options(isolation_level="AUTOCOMMIT").execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{database}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize the MySQL schema for this project.")
    parser.add_argument(
        "--skip-create-database",
        action="store_true",
        help="Only create tables in the configured database.",
    )
    args = parser.parse_args()

    if not args.skip_create_database:
        create_database_if_needed(DATABASE_URL)
    init_database()
    print("MySQL database and tables are ready.")


if __name__ == "__main__":
    main()
