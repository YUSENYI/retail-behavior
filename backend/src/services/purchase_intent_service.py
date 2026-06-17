from __future__ import annotations

from collections import Counter
from datetime import datetime

from domain.common import utcnow
from models.database import SessionLocal, use_mysql_persistence
from models.profiles import PurchaseIntent
from sqlalchemy import select
from services.behavior_event_repository import BehaviorEventRecord


class PurchaseIntentService:
    def classify(self, user_id: str, events: list[BehaviorEventRecord]) -> dict[str, object]:
        user_events = [event for event in events if event.user_id == user_id]
        has_payment = any(e.event_type == "payment_success" for e in user_events)
        has_cart = any(e.event_type == "cart_add" for e in user_events)
        browse_count = sum(1 for e in user_events if e.event_type == "browse")
        favorite_count = sum(1 for e in user_events if e.event_type == "favorite")
        click_count = sum(1 for e in user_events if e.event_type == "click")
        repeated_product_count = max(Counter(event.product_id for event in user_events if event.product_id).values() or [0])
        recent_days = _days_since_latest(user_events)
        score = (
            (30 if has_cart and not has_payment else 0)
            + min(browse_count * 6, 24)
            + min(click_count * 5, 15)
            + min(favorite_count * 12, 24)
            + min(repeated_product_count * 8, 24)
            + (25 if has_payment else 0)
            + max(20 - recent_days * 2, 0)
        )
        score = max(min(score, 100), 0)
        if has_cart and not has_payment:
            level, basis = "cart_unpaid", "cart added but payment not completed"
        elif has_payment:
            level, basis = "high", "recent payment behavior"
        elif score >= 80:
            level, basis = "high", "high weighted behavior intent score"
        elif score >= 50:
            level, basis = "medium", "repeated browse, click, favorite, or product focus"
        else:
            level, basis = "low", "limited purchase signal"
        intent = {
            "userId": user_id,
            "intentLevel": level,
            "basis": basis,
            "score": round(score, 2),
            "signals": {
                "browseCount": browse_count,
                "clickCount": click_count,
                "favoriteCount": favorite_count,
                "hasCartUnpaid": has_cart and not has_payment,
                "repeatedProductCount": repeated_product_count,
                "recencyDays": recent_days,
            },
            "algorithmVersion": "weighted-intent-v2",
        }
        self._save_intent(intent)
        return intent

    def list_intents(
        self, events: list[BehaviorEventRecord] | None = None, user_id: str | None = None
    ) -> list[dict[str, object]]:
        if events is not None:
            user_ids = [user_id] if user_id else sorted({event.user_id for event in events if event.user_id})
            return [self.classify(current_user_id, events) for current_user_id in user_ids]
        if not use_mysql_persistence():
            return []
        statement = select(PurchaseIntent).order_by(PurchaseIntent.updated_at.desc())
        if user_id:
            statement = statement.where(PurchaseIntent.user_id == user_id)
        with SessionLocal() as session:
            rows = session.scalars(statement).all()
            return [self._row_to_dict(row) for row in rows]

    def _save_intent(self, intent: dict[str, object]) -> None:
        if not use_mysql_persistence():
            return
        now = utcnow().replace(tzinfo=None)
        user_id = str(intent["userId"])
        with SessionLocal() as session:
            row = session.get(PurchaseIntent, f"intent-{user_id}")
            if row is None:
                row = PurchaseIntent(
                    intent_id=f"intent-{user_id}",
                    user_id=user_id,
                    intent_level=str(intent["intentLevel"]),
                    related_product_id=None,
                    basis=str(intent["basis"]),
                    score=float(intent["score"]),
                    updated_at=now,
                )
                session.add(row)
            else:
                row.intent_level = str(intent["intentLevel"])
                row.basis = str(intent["basis"])
                row.score = float(intent["score"])
                row.updated_at = now
            session.commit()

    def _row_to_dict(self, row: PurchaseIntent) -> dict[str, object]:
        return {
            "userId": row.user_id,
            "intentLevel": row.intent_level,
            "basis": row.basis,
            "score": float(row.score),
            "algorithmVersion": "weighted-intent-v2",
            "updatedAt": row.updated_at.isoformat(),
        }


def _days_since_latest(events: list[BehaviorEventRecord]) -> int:
    timestamps = [_timestamp(event.occurred_at) for event in events]
    if not timestamps:
        return 999
    return max(int((utcnow().replace(tzinfo=None) - max(timestamps)).total_seconds() // 86400), 0)


def _timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    return datetime.min
