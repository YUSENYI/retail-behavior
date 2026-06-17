from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from domain.common import utcnow
from models.database import SessionLocal, use_mysql_persistence
from models.profiles import UserSegment, UserSegmentMembership
from sqlalchemy import delete, select
from services.behavior_event_repository import BehaviorEventRecord


class SegmentService:
    SEGMENTS = {
        "high_value": ("High Value", "paid users"),
        "potential": ("Potential", "cart behavior without payment"),
        "new_user": ("New User", "limited observed behavior"),
        "silent": ("Silent", "no recent behavior"),
        "price_sensitive": ("Price Sensitive", "low price preference"),
        "churn_risk": ("Churn Risk", "historical activity with no recent payment"),
    }

    def classify(self, user_id: str, events: list[BehaviorEventRecord]) -> list[dict[str, object]]:
        user_events = [event for event in events if event.user_id == user_id]
        paid_events = [event for event in user_events if event.event_type == "payment_success"]
        paid = bool(paid_events)
        cart = any(event.event_type == "cart_add" for event in user_events)
        paid_amount = sum(_event_amount(event) for event in paid_events)
        recent_days = _days_since_latest(user_events)
        low_price_ratio = _low_price_ratio(user_events)
        segments = []
        if paid:
            score = 90 if paid_amount >= 1000 or len(paid_events) >= 3 else 75
            segments.append({"segmentType": "high_value", "reason": "successful payment and value signal", "score": score})
        if cart and not paid:
            segments.append({"segmentType": "potential", "reason": "cart behavior without payment", "score": 70})
        if len(user_events) <= 1:
            segments.append({"segmentType": "new_user", "reason": "limited observed behavior", "score": 60})
        if not user_events or recent_days >= 30:
            segments.append({"segmentType": "silent", "reason": "no recent behavior", "score": 50})
        if low_price_ratio >= 0.5:
            segments.append({"segmentType": "price_sensitive", "reason": "low price product interest", "score": 65})
        if len(user_events) >= 3 and (not paid or recent_days >= 14):
            segments.append({"segmentType": "churn_risk", "reason": "activity dropped or no successful recent payment", "score": 55})
        return segments

    def refresh_segments(self, events: list[BehaviorEventRecord]) -> list[dict[str, object]]:
        user_ids = sorted({event.user_id for event in events if event.user_id})
        memberships: list[dict[str, object]] = []
        for user_id in user_ids:
            for segment in self.classify(user_id, events):
                memberships.append({"userId": user_id, **segment})

        if use_mysql_persistence():
            self._save_segments(memberships)
        return self.list_segments(events)

    def list_segments(self, events: list[BehaviorEventRecord] | None = None) -> list[dict[str, object]]:
        if use_mysql_persistence():
            with SessionLocal() as session:
                rows = session.scalars(select(UserSegment).order_by(UserSegment.segment_id)).all()
                if rows:
                    return [self._segment_to_dict(row) for row in rows]
        if events is not None:
            return self.refresh_segments(events) if use_mysql_persistence() else self._summarize(events)
        return []

    def list_segment_users(
        self, segment_id: str, events: list[BehaviorEventRecord] | None = None
    ) -> list[dict[str, object]]:
        if use_mysql_persistence():
            with SessionLocal() as session:
                rows = session.scalars(
                    select(UserSegmentMembership)
                    .where(
                        UserSegmentMembership.segment_id == segment_id,
                        UserSegmentMembership.left_at.is_(None),
                    )
                    .order_by(UserSegmentMembership.user_id)
                ).all()
                if rows:
                    return [
                        {
                            "userId": row.user_id,
                            "segmentId": row.segment_id,
                            "reason": row.reason,
                            "score": float(row.score or 0),
                        }
                        for row in rows
                    ]
        if events is None:
            return []
        return [
            {"userId": user_id, "segmentId": segment_id, "reason": item["reason"], "score": item["score"]}
            for user_id in sorted({event.user_id for event in events if event.user_id})
            for item in self.classify(user_id, events)
            if item["segmentType"] == segment_id
        ]

    def _summarize(self, events: list[BehaviorEventRecord]) -> list[dict[str, object]]:
        counts: dict[str, int] = defaultdict(int)
        for user_id in sorted({event.user_id for event in events if event.user_id}):
            for segment in self.classify(user_id, events):
                counts[str(segment["segmentType"])] += 1
        return [
            {
                "segmentId": segment_id,
                "segmentType": segment_id,
                "name": self.SEGMENTS[segment_id][0],
                "memberCount": counts.get(segment_id, 0),
                "ruleDescription": self.SEGMENTS[segment_id][1],
            }
            for segment_id in self.SEGMENTS
        ]

    def _save_segments(self, memberships: list[dict[str, object]]) -> None:
        now = utcnow().replace(tzinfo=None)
        counts: dict[str, int] = defaultdict(int)
        for membership in memberships:
            counts[str(membership["segmentType"])] += 1
        with SessionLocal() as session:
            session.execute(delete(UserSegmentMembership))
            for segment_id, (name, rule) in self.SEGMENTS.items():
                row = session.get(UserSegment, segment_id)
                if row is None:
                    row = UserSegment(
                        segment_id=segment_id,
                        segment_type=segment_id,
                        name=name,
                        description=rule,
                        rule_description=rule,
                        member_count=counts.get(segment_id, 0),
                        last_calculated_at=now,
                    )
                    session.add(row)
                else:
                    row.member_count = counts.get(segment_id, 0)
                    row.last_calculated_at = now
            for membership in memberships:
                segment_type = str(membership["segmentType"])
                session.add(
                    UserSegmentMembership(
                        segment_id=segment_type,
                        user_id=str(membership["userId"]),
                        joined_at=now,
                        left_at=None,
                        reason=str(membership["reason"]),
                        score=float(membership["score"]),
                    )
                )
            session.commit()

    def _segment_to_dict(self, row: UserSegment) -> dict[str, object]:
        return {
            "segmentId": row.segment_id,
            "segmentType": row.segment_type,
            "name": row.name,
            "memberCount": row.member_count,
            "ruleDescription": row.rule_description,
            "lastCalculatedAt": row.last_calculated_at.isoformat(),
        }


def _event_amount(event: BehaviorEventRecord) -> float:
    value = event.metadata.get("amount", event.metadata.get("price", 0))
    try:
        return max(float(value), 0)
    except (TypeError, ValueError):
        return 0


def _low_price_ratio(events: list[BehaviorEventRecord]) -> float:
    prices = [_event_amount(event) for event in events if _event_amount(event) > 0]
    if not prices:
        return 0
    return sum(1 for price in prices if price <= 150) / len(prices)


def _days_since_latest(events: list[BehaviorEventRecord]) -> int:
    timestamps = [_timestamp(event.occurred_at) for event in events]
    if not timestamps:
        return 999
    return max(int((utcnow().replace(tzinfo=None) - max(timestamps)).total_seconds() // 86400), 0)


def _timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    return datetime.min
