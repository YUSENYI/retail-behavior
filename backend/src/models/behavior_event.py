from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.database import Base


class BehaviorEvent(Base):
    __tablename__ = "behavior_events"
    __table_args__ = (
        UniqueConstraint("source_system", "event_id", name="uq_behavior_event_source_event"),
        Index("ix_behavior_path", "user_id", "visitor_id", "session_id", "occurred_at"),
        Index("ix_behavior_metrics", "event_type", "product_id", "channel_id", "occurred_at"),
    )

    event_pk: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(128), nullable=False)
    source_system: Mapped[str] = mapped_column(String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(64), index=True)
    visitor_id: Mapped[str | None] = mapped_column(String(64), index=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    product_id: Mapped[str | None] = mapped_column(String(64), index=True)
    order_id: Mapped[str | None] = mapped_column(String(64), index=True)
    payment_id: Mapped[str | None] = mapped_column(String(64), index=True)
    channel_id: Mapped[str] = mapped_column(String(64), index=True)
    search_keyword: Mapped[str | None] = mapped_column(String(255))
    occurred_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    idempotency_state: Mapped[str] = mapped_column(String(32), default="accepted")
    exclusion_reason: Mapped[str | None] = mapped_column(String(255))
    metadata_json: Mapped[str | None] = mapped_column(Text)
