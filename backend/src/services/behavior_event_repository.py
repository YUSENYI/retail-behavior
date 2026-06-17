from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import json
from typing import Any
from typing import Protocol

from api.filters import AnalysisFilters
from domain.common import utcnow
from domain.enums import IdempotencyState
from models.behavior_event import BehaviorEvent
from models.database import SessionLocal, use_mysql_persistence
from models.foundation import Channel, Order, Payment, Product, Session as RetailSession, User, Visitor
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


@dataclass(slots=True)
class BehaviorEventRecord:
    event_id: str
    source_system: str
    event_type: str
    session_id: str
    channel_id: str
    occurred_at: object
    user_id: str | None = None
    visitor_id: str | None = None
    product_id: str | None = None
    order_id: str | None = None
    payment_id: str | None = None
    search_keyword: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    received_at: object = field(default_factory=utcnow)
    idempotency_state: IdempotencyState = IdempotencyState.ACCEPTED
    exclusion_reason: str | None = None

    @property
    def subject_id(self) -> str:
        return self.user_id or self.visitor_id or self.session_id


class BehaviorEventRepository(Protocol):
    def ingest(self, event: BehaviorEventRecord) -> BehaviorEventRecord: ...

    def accepted_events(self) -> list[BehaviorEventRecord]: ...

    def all_attempts(self) -> list[BehaviorEventRecord]: ...

    def query(self, filters: AnalysisFilters | None = None) -> list[BehaviorEventRecord]: ...

    def clear(self) -> None: ...


class InMemoryBehaviorEventRepository:
    def __init__(self) -> None:
        self._events: dict[tuple[str, str], BehaviorEventRecord] = {}
        self._all_attempts: list[BehaviorEventRecord] = []

    def ingest(self, event: BehaviorEventRecord) -> BehaviorEventRecord:
        key = (event.source_system, event.event_id)
        if key in self._events:
            event.idempotency_state = IdempotencyState.DUPLICATE
            event.exclusion_reason = "duplicate event_id for source_system"
        elif not event.event_id or not event.session_id or not event.channel_id or not event.occurred_at:
            event.idempotency_state = IdempotencyState.INVALID
            event.exclusion_reason = "missing required event identity or path fields"
        elif getattr(event, "occurred_at") < utcnow() - timedelta(days=7):
            event.idempotency_state = IdempotencyState.DELAYED
            event.exclusion_reason = "late-arriving event outside normal freshness window"
            self._events[key] = event
        else:
            event.idempotency_state = IdempotencyState.ACCEPTED
            self._events[key] = event
        self._all_attempts.append(event)
        return event

    def accepted_events(self) -> list[BehaviorEventRecord]:
        return [e for e in self._events.values() if e.idempotency_state == IdempotencyState.ACCEPTED]

    def all_attempts(self) -> list[BehaviorEventRecord]:
        return list(self._all_attempts)

    def query(self, filters: AnalysisFilters | None = None) -> list[BehaviorEventRecord]:
        filters = filters or AnalysisFilters()
        return [event for event in self._events.values() if filters.matches(event)]

    def clear(self) -> None:
        self._events.clear()
        self._all_attempts.clear()


def _to_db_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        value = value if value.tzinfo else value.replace(tzinfo=UTC)
        return value.astimezone(UTC).replace(tzinfo=None)
    return datetime.min


def _from_db_datetime(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


class MySQLBehaviorEventRepository:
    def ingest(self, event: BehaviorEventRecord) -> BehaviorEventRecord:
        key_valid = bool(event.event_id and event.session_id and event.channel_id and event.occurred_at)
        if not key_valid:
            event.idempotency_state = IdempotencyState.INVALID
            event.exclusion_reason = "missing required event identity or path fields"
            return event
        if getattr(event, "occurred_at") < utcnow() - timedelta(days=7):
            event.idempotency_state = IdempotencyState.DELAYED
            event.exclusion_reason = "late-arriving event outside normal freshness window"
        else:
            event.idempotency_state = IdempotencyState.ACCEPTED

        with SessionLocal() as session:
            existing = session.scalar(
                select(BehaviorEvent.event_pk).where(
                    BehaviorEvent.source_system == event.source_system,
                    BehaviorEvent.event_id == event.event_id,
                )
            )
            if existing is not None:
                event.idempotency_state = IdempotencyState.DUPLICATE
                event.exclusion_reason = "duplicate event_id for source_system"
                return event

            self._upsert_related_entities(session, event)
            session.add(self._to_model(event))
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                event.idempotency_state = IdempotencyState.DUPLICATE
                event.exclusion_reason = "duplicate event_id for source_system"
        return event

    def accepted_events(self) -> list[BehaviorEventRecord]:
        with SessionLocal() as session:
            rows = session.scalars(
                select(BehaviorEvent)
                .where(BehaviorEvent.idempotency_state == IdempotencyState.ACCEPTED.value)
                .order_by(BehaviorEvent.occurred_at)
            ).all()
            return [self._to_record(row) for row in rows]

    def all_attempts(self) -> list[BehaviorEventRecord]:
        with SessionLocal() as session:
            rows = session.scalars(select(BehaviorEvent).order_by(BehaviorEvent.occurred_at)).all()
            return [self._to_record(row) for row in rows]

    def query(self, filters: AnalysisFilters | None = None) -> list[BehaviorEventRecord]:
        filters = filters or AnalysisFilters()
        statement = select(BehaviorEvent)
        for field_name in ["product_id", "user_id", "visitor_id", "session_id", "channel_id", "event_type"]:
            value = getattr(filters, field_name)
            if value is not None:
                statement = statement.where(getattr(BehaviorEvent, field_name) == value)
        if filters.start_time is not None:
            statement = statement.where(BehaviorEvent.occurred_at >= _to_db_datetime(filters.start_time))
        if filters.end_time is not None:
            statement = statement.where(BehaviorEvent.occurred_at <= _to_db_datetime(filters.end_time))
        statement = statement.order_by(BehaviorEvent.occurred_at)
        with SessionLocal() as session:
            rows = session.scalars(statement).all()
            return [self._to_record(row) for row in rows]

    def clear(self) -> None:
        with SessionLocal() as session:
            session.execute(delete(BehaviorEvent))
            session.commit()

    def _to_model(self, event: BehaviorEventRecord) -> BehaviorEvent:
        return BehaviorEvent(
            event_id=event.event_id,
            source_system=event.source_system,
            event_type=event.event_type,
            user_id=event.user_id,
            visitor_id=event.visitor_id,
            session_id=event.session_id,
            product_id=event.product_id,
            order_id=event.order_id,
            payment_id=event.payment_id,
            channel_id=event.channel_id,
            search_keyword=event.search_keyword,
            occurred_at=_to_db_datetime(event.occurred_at),
            received_at=_to_db_datetime(event.received_at),
            idempotency_state=event.idempotency_state.value,
            exclusion_reason=event.exclusion_reason,
            metadata_json=json.dumps(event.metadata, ensure_ascii=False, default=str),
        )

    def _to_record(self, row: BehaviorEvent) -> BehaviorEventRecord:
        metadata: dict[str, Any] = {}
        if row.metadata_json:
            try:
                loaded = json.loads(row.metadata_json)
                if isinstance(loaded, dict):
                    metadata = loaded
            except json.JSONDecodeError:
                metadata = {}
        return BehaviorEventRecord(
            event_id=row.event_id,
            source_system=row.source_system,
            event_type=row.event_type,
            user_id=row.user_id,
            visitor_id=row.visitor_id,
            session_id=row.session_id,
            product_id=row.product_id,
            order_id=row.order_id,
            payment_id=row.payment_id,
            channel_id=row.channel_id,
            search_keyword=row.search_keyword,
            occurred_at=_from_db_datetime(row.occurred_at),
            received_at=_from_db_datetime(row.received_at),
            idempotency_state=IdempotencyState(row.idempotency_state),
            exclusion_reason=row.exclusion_reason,
            metadata=metadata,
        )

    def _upsert_related_entities(self, session: Session, event: BehaviorEventRecord) -> None:
        now = _to_db_datetime(utcnow())
        if event.user_id and session.get(User, event.user_id) is None:
            session.add(
                User(
                    user_id=event.user_id,
                    visitor_id=event.visitor_id,
                    display_name=event.metadata.get("userName") or event.user_id,
                    phone_masked=None,
                    email_masked=None,
                    address_masked=None,
                    demographic_attributes=None,
                    status="active",
                    created_at=now,
                    updated_at=now,
                )
            )
        if event.visitor_id and session.get(Visitor, event.visitor_id) is None:
            session.add(
                Visitor(
                    visitor_id=event.visitor_id,
                    first_seen_at=now,
                    last_seen_at=now,
                    linked_user_id=event.user_id,
                    source_channel_id=event.channel_id,
                )
            )
        if event.channel_id and session.get(Channel, event.channel_id) is None:
            session.add(
                Channel(
                    channel_id=event.channel_id,
                    name=event.channel_id,
                    type="web",
                    owner=None,
                    status="active",
                )
            )
        session.flush()
        if event.session_id and session.get(RetailSession, event.session_id) is None:
            session.add(
                RetailSession(
                    session_id=event.session_id,
                    user_id=event.user_id,
                    visitor_id=event.visitor_id,
                    channel_id=event.channel_id,
                    started_at=_to_db_datetime(event.occurred_at),
                    ended_at=None,
                    entry_url=None,
                    exit_url=None,
                    device_context=str(event.metadata.get("device") or "browser"),
                )
            )
        if event.product_id:
            product = session.get(Product, event.product_id)
            if product is None:
                price = event.metadata.get("price")
                session.add(
                    Product(
                        product_id=event.product_id,
                        sku=event.product_id,
                        name=str(event.metadata.get("productName") or event.product_id),
                        category_id=str(event.metadata.get("category") or "uncategorized"),
                        brand=str(event.metadata.get("brand") or ""),
                        status="active",
                        list_price=price,
                        current_price=price,
                        created_at=now,
                        updated_at=now,
                    )
                )
            else:
                product.updated_at = now
        session.flush()
        if event.order_id:
            order = session.get(Order, event.order_id)
            amount = float(event.metadata.get("price") or 0)
            if order is None:
                order = Order(
                    order_id=event.order_id,
                    user_id=event.user_id,
                    visitor_id=event.visitor_id,
                    session_id=event.session_id,
                    status="paid" if event.event_type == "payment_success" else "submitted",
                    gross_amount=amount,
                    net_amount=amount,
                    submitted_at=_to_db_datetime(event.occurred_at),
                    paid_at=_to_db_datetime(event.occurred_at) if event.event_type == "payment_success" else None,
                    cancelled_at=None,
                    refunded_at=None,
                )
                session.add(order)
            elif event.event_type == "payment_success":
                order.status = "paid"
                order.paid_at = _to_db_datetime(event.occurred_at)
                if amount:
                    order.net_amount = amount
                    order.gross_amount = amount
        session.flush()
        if event.payment_id and event.order_id and event.event_type == "payment_success":
            if session.get(Payment, event.payment_id) is None:
                amount = float(event.metadata.get("price") or 0)
                session.add(
                    Payment(
                        payment_id=event.payment_id,
                        order_id=event.order_id,
                        status="success",
                        amount=amount,
                        payment_time=_to_db_datetime(event.occurred_at),
                        payment_identifier_masked=None,
                    )
                )


repository: BehaviorEventRepository
if use_mysql_persistence():
    repository = MySQLBehaviorEventRepository()
else:
    repository = InMemoryBehaviorEventRepository()
