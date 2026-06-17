from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    visitor_id: Mapped[str | None] = mapped_column(String(64), index=True)
    display_name: Mapped[str | None] = mapped_column(String(128))
    phone_masked: Mapped[str | None] = mapped_column(String(64))
    email_masked: Mapped[str | None] = mapped_column(String(128))
    address_masked: Mapped[str | None] = mapped_column(String(255))
    demographic_attributes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)


class Visitor(Base):
    __tablename__ = "visitors"

    visitor_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime)
    linked_user_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("users.user_id"))
    source_channel_id: Mapped[str | None] = mapped_column(String(64))


class Channel(Base):
    __tablename__ = "channels"

    channel_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    type: Mapped[str] = mapped_column(String(64))
    owner: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="active")


class Session(Base):
    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("users.user_id"))
    visitor_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("visitors.visitor_id"))
    channel_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("channels.channel_id"))
    started_at: Mapped[datetime] = mapped_column(DateTime)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)
    entry_url: Mapped[str | None] = mapped_column(String(512))
    exit_url: Mapped[str | None] = mapped_column(String(512))
    device_context: Mapped[str | None] = mapped_column(String(128))


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    sku: Mapped[str | None] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[str | None] = mapped_column(String(64))
    brand: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="active")
    list_price: Mapped[float | None] = mapped_column(Numeric(12, 2))
    current_price: Mapped[float | None] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("users.user_id"))
    visitor_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("visitors.visitor_id"))
    session_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("sessions.session_id"))
    status: Mapped[str] = mapped_column(String(32), default="submitted")
    gross_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    net_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime)


class Payment(Base):
    __tablename__ = "payments"

    payment_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(64), ForeignKey("orders.order_id"))
    status: Mapped[str] = mapped_column(String(32), default="attempted")
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    payment_time: Mapped[datetime | None] = mapped_column(DateTime)
    payment_identifier_masked: Mapped[str | None] = mapped_column(String(128))
