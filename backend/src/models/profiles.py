from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    profile_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    basic_attribute_tags: Mapped[str | None] = mapped_column(Text)
    consumption_level: Mapped[str] = mapped_column(String(32), default="low")
    interest_tags: Mapped[str | None] = mapped_column(Text)
    activity_level: Mapped[str] = mapped_column(String(32), default="low")
    value_grade: Mapped[str] = mapped_column(String(32), default="low")
    basis_window: Mapped[str | None] = mapped_column(String(128))
    updated_at: Mapped[datetime] = mapped_column(DateTime)


class UserSegment(Base):
    __tablename__ = "user_segments"

    segment_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    segment_type: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(Text)
    rule_description: Mapped[str] = mapped_column(Text)
    member_count: Mapped[int] = mapped_column(default=0)
    last_calculated_at: Mapped[datetime] = mapped_column(DateTime)


class UserSegmentMembership(Base):
    __tablename__ = "user_segment_memberships"

    membership_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    segment_id: Mapped[str] = mapped_column(String(64), index=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime)
    left_at: Mapped[datetime | None] = mapped_column(DateTime)
    reason: Mapped[str] = mapped_column(String(255))
    score: Mapped[float | None] = mapped_column(Numeric(7, 4))


class PurchaseIntent(Base):
    __tablename__ = "purchase_intents"

    intent_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    intent_level: Mapped[str] = mapped_column(String(32), index=True)
    related_product_id: Mapped[str | None] = mapped_column(String(64), index=True)
    basis: Mapped[str] = mapped_column(String(255))
    score: Mapped[float] = mapped_column(Numeric(7, 4), default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
