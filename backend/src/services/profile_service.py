from __future__ import annotations

from collections import Counter

from domain.common import utcnow
from services.behavior_event_repository import BehaviorEventRecord


class ProfileService:
    def build_profile(self, user_id: str, events: list[BehaviorEventRecord]) -> dict[str, object]:
        user_events = [event for event in events if event.user_id == user_id]
        categories = Counter(event.product_id for event in user_events if event.product_id)
        activity = "high" if len(user_events) >= 5 else "medium" if user_events else "low"
        value = "high" if any(e.event_type == "payment_success" for e in user_events) else "medium"
        return {
            "userId": user_id,
            "maskedUser": {"userId": user_id},
            "consumptionLevel": value,
            "interestTags": [key for key, _ in categories.most_common(5)],
            "activityLevel": activity,
            "valueGrade": value,
            "updatedAt": utcnow().isoformat(),
        }
