from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.database import Base


class Report(Base):
    __tablename__ = "reports"

    report_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    report_type: Mapped[str] = mapped_column(String(64), index=True)
    filters: Mapped[str] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(32), default="ready")
    export_uri: Mapped[str | None] = mapped_column(String(512))
    sensitive_data_state: Mapped[str] = mapped_column(String(32), default="masked")
    freshness_at: Mapped[datetime | None] = mapped_column(DateTime)
