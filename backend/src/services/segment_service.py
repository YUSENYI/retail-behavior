from __future__ import annotations

from services.behavior_event_repository import BehaviorEventRecord


class SegmentService:
    def classify(self, user_id: str, events: list[BehaviorEventRecord]) -> list[dict[str, object]]:
        user_events = [event for event in events if event.user_id == user_id]
        paid = any(event.event_type == "payment_success" for event in user_events)
        cart = any(event.event_type == "cart_add" for event in user_events)
        segments = []
        if paid:
            segments.append({"segmentType": "high_value", "reason": "successful payment behavior", "score": 90})
        if cart and not paid:
            segments.append({"segmentType": "potential", "reason": "cart behavior without payment", "score": 70})
        if len(user_events) <= 1:
            segments.append({"segmentType": "new_user", "reason": "limited observed behavior", "score": 60})
        if not user_events:
            segments.append({"segmentType": "silent", "reason": "no recent behavior", "score": 50})
        return segments
