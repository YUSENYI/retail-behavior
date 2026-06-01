from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    alert_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    alert_type: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="new")
    scope_type: Mapped[str | None] = mapped_column(String(64))
    scope_id: Mapped[str | None] = mapped_column(String(64), index=True)
    trigger_reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)
    owner_id: Mapped[str | None] = mapped_column(String(64))


class RecommendationInsight(Base):
    __tablename__ = "recommendation_insights"

    insight_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    target_type: Mapped[str] = mapped_column(String(32), index=True)
    target_id: Mapped[str] = mapped_column(String(64), index=True)
    product_id: Mapped[str] = mapped_column(String(64), index=True)
    basis_type: Mapped[str] = mapped_column(String(64))
    reason: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(32), default="medium")
    score: Mapped[float] = mapped_column(Numeric(7, 4), default=0)
    generated_at: Mapped[datetime] = mapped_column(DateTime)
