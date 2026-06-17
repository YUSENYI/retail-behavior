from __future__ import annotations

from collections import Counter
from datetime import datetime
import json

from domain.common import utcnow
from models.database import SessionLocal, use_mysql_persistence
from models.profiles import UserProfile
from services.behavior_event_repository import BehaviorEventRecord


class ProfileService:
    def build_profile(
        self, user_id: str, events: list[BehaviorEventRecord] | None = None
    ) -> dict[str, object]:
        if events is None:
            stored = self.get_profile(user_id)
            if stored is not None:
                return stored
            events = []

        user_events = [event for event in events if event.user_id == user_id]
        categories = Counter(str(event.metadata.get("category") or event.product_id) for event in user_events if event.product_id)
        paid_events = [event for event in user_events if event.event_type == "payment_success"]
        paid_amount = sum(_event_amount(event) for event in paid_events)
        recent_days = _days_since_latest(user_events)
        activity_score = _activity_score(user_events, recent_days)
        value_score = min(100, paid_amount / 20 + len(paid_events) * 15 + activity_score * 0.2)
        price_values = [_event_amount(event) for event in user_events if _event_amount(event) > 0]
        avg_price = sum(price_values) / len(price_values) if price_values else 0
        activity = "high" if activity_score >= 70 else "medium" if activity_score >= 30 else "low"
        value = "high" if paid_events or value_score >= 70 else "medium" if value_score >= 30 else "low"
        price_sensitivity = "high" if avg_price and avg_price <= 150 else "medium" if avg_price <= 500 else "low"
        profile = {
            "userId": user_id,
            "maskedUser": {"userId": user_id},
            "consumptionLevel": value,
            "interestTags": [key for key, _ in categories.most_common(5)],
            "activityLevel": activity,
            "valueGrade": value,
            "rfm": {
                "recencyDays": recent_days,
                "frequency": len(user_events),
                "monetary": round(paid_amount, 2),
            },
            "activityScore": round(activity_score, 2),
            "valueScore": round(value_score, 2),
            "priceSensitivity": price_sensitivity,
            "algorithmVersion": "rfm-behavior-v2",
            "updatedAt": utcnow().isoformat(),
        }
        self._save_profile(profile)
        return profile

    def get_profile(self, user_id: str) -> dict[str, object] | None:
        if not use_mysql_persistence():
            return None
        with SessionLocal() as session:
            row = session.get(UserProfile, f"profile-{user_id}")
            return self._row_to_dict(row) if row is not None else None

    def _save_profile(self, profile: dict[str, object]) -> None:
        if not use_mysql_persistence():
            return
        now = utcnow().replace(tzinfo=None)
        user_id = str(profile["userId"])
        with SessionLocal() as session:
            row = session.get(UserProfile, f"profile-{user_id}")
            if row is None:
                row = UserProfile(
                    profile_id=f"profile-{user_id}",
                    user_id=user_id,
                    basic_attribute_tags=None,
                    consumption_level=str(profile["consumptionLevel"]),
                    interest_tags=json.dumps(profile["interestTags"], ensure_ascii=False),
                    activity_level=str(profile["activityLevel"]),
                    value_grade=str(profile["valueGrade"]),
                    basis_window="all_accepted_events",
                    updated_at=now,
                )
                session.add(row)
            else:
                row.consumption_level = str(profile["consumptionLevel"])
                row.interest_tags = json.dumps(profile["interestTags"], ensure_ascii=False)
                row.activity_level = str(profile["activityLevel"])
                row.value_grade = str(profile["valueGrade"])
                row.basis_window = "all_accepted_events"
                row.updated_at = now
            session.commit()

    def _row_to_dict(self, row: UserProfile) -> dict[str, object]:
        interest_tags: list[str] = []
        if row.interest_tags:
            loaded = json.loads(row.interest_tags)
            if isinstance(loaded, list):
                interest_tags = [str(item) for item in loaded]
        return {
            "userId": row.user_id,
            "maskedUser": {"userId": row.user_id},
            "consumptionLevel": row.consumption_level,
            "interestTags": interest_tags,
            "activityLevel": row.activity_level,
            "valueGrade": row.value_grade,
            "algorithmVersion": "rfm-behavior-v2",
            "updatedAt": row.updated_at.isoformat(),
        }


def _event_amount(event: BehaviorEventRecord) -> float:
    value = event.metadata.get("amount", event.metadata.get("price", 0))
    try:
        return max(float(value), 0)
    except (TypeError, ValueError):
        return 0


def _days_since_latest(events: list[BehaviorEventRecord]) -> int:
    timestamps = [_timestamp(event.occurred_at) for event in events]
    if not timestamps:
        return 999
    return max(int((utcnow().replace(tzinfo=None) - max(timestamps)).total_seconds() // 86400), 0)


def _activity_score(events: list[BehaviorEventRecord], recency_days: int) -> float:
    frequency_score = min(len(events) * 12, 75)
    recency_score = max(25 - recency_days * 2, 0)
    return min(frequency_score + recency_score, 100)


def _timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    return datetime.min
