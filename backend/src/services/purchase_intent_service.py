from __future__ import annotations

from services.behavior_event_repository import BehaviorEventRecord


class PurchaseIntentService:
    def classify(self, user_id: str, events: list[BehaviorEventRecord]) -> dict[str, object]:
        user_events = [event for event in events if event.user_id == user_id]
        has_payment = any(e.event_type == "payment_success" for e in user_events)
        has_cart = any(e.event_type == "cart_add" for e in user_events)
        browse_count = sum(1 for e in user_events if e.event_type == "browse")
        if has_cart and not has_payment:
            level, score, basis = "cart_unpaid", 85, "cart added but payment not completed"
        elif has_payment:
            level, score, basis = "high", 95, "recent payment behavior"
        elif browse_count >= 3:
            level, score, basis = "medium", 65, "repeated browse behavior"
        else:
            level, score, basis = "low", 30, "limited purchase signal"
        return {"userId": user_id, "intentLevel": level, "basis": basis, "score": score}
