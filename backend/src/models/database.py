from __future__ import annotations

import os
from pathlib import Path
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / ".env.example", override=False)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://retail:retail@localhost:3306/retail_behavior",
)


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def use_mysql_persistence() -> bool:
    app_env = os.getenv("APP_ENV", "development").lower()
    in_memory = os.getenv("USE_IN_MEMORY_REPOSITORY", "").lower() in {"1", "true", "yes"}
    return app_env != "test" and not in_memory


def import_all_models() -> None:
    import models.alerts_recommendations  # noqa: F401
    import models.behavior_event  # noqa: F401
    import models.foundation  # noqa: F401
    import models.metrics  # noqa: F401
    import models.profiles  # noqa: F401
    import models.reports  # noqa: F401
    import models.security  # noqa: F401


def init_database() -> None:
    import_all_models()
    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
