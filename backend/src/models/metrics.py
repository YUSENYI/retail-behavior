from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.database import Base


class MetricDefinition(Base):
    __tablename__ = "metric_definitions"

    metric_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    version: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(32))
    deduplication_rule: Mapped[str] = mapped_column(Text)
    calculation_rule: Mapped[str] = mapped_column(Text)
    valid_min: Mapped[float | None] = mapped_column(Numeric(12, 4))
    valid_max: Mapped[float | None] = mapped_column(Numeric(12, 4))
    effective_from: Mapped[datetime] = mapped_column(DateTime)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime)


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    snapshot_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    metric_key: Mapped[str] = mapped_column(String(64), index=True)
    metric_version: Mapped[str] = mapped_column(String(32))
    scope_type: Mapped[str] = mapped_column(String(32), default="global")
    scope_id: Mapped[str | None] = mapped_column(String(64), index=True)
    window_start: Mapped[datetime] = mapped_column(DateTime)
    window_end: Mapped[datetime] = mapped_column(DateTime)
    value: Mapped[float] = mapped_column(Numeric(16, 4), default=0)
    unit: Mapped[str] = mapped_column(String(32))
    freshness_at: Mapped[datetime] = mapped_column(DateTime)
    calculated_at: Mapped[datetime] = mapped_column(DateTime)
    validation_state: Mapped[str] = mapped_column(String(32), default="valid")
    source_event_count: Mapped[int] = mapped_column(default=0)


class FunnelStageSnapshot(Base):
    __tablename__ = "funnel_stage_snapshots"

    snapshot_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    funnel_id: Mapped[str] = mapped_column(String(64), index=True)
    stage: Mapped[str] = mapped_column(String(32))
    window_start: Mapped[datetime] = mapped_column(DateTime)
    window_end: Mapped[datetime] = mapped_column(DateTime)
    scope_type: Mapped[str] = mapped_column(String(32), default="global")
    scope_id: Mapped[str | None] = mapped_column(String(64), index=True)
    entered_count: Mapped[int] = mapped_column(default=0)
    converted_count: Mapped[int] = mapped_column(default=0)
    dropoff_count: Mapped[int] = mapped_column(default=0)
    conversion_rate: Mapped[float] = mapped_column(Numeric(7, 4), default=0)
    dropoff_rate: Mapped[float] = mapped_column(Numeric(7, 4), default=0)
    freshness_at: Mapped[datetime] = mapped_column(DateTime)
