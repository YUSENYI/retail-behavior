from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from math import exp

from domain.common import utcnow
from models.alerts_recommendations import RecommendationInsight
from models.database import SessionLocal, use_mysql_persistence
from sqlalchemy import delete, select
from services.behavior_event_repository import BehaviorEventRecord


class RecommendationService:
    def recommend(
        self, target_id: str, events: list[BehaviorEventRecord] | None = None
    ) -> list[dict[str, object]]:
        if events is None:
            stored = self.list_recommendations(target_id)
            if stored:
                return stored
            events = []

        user_events = [event for event in events if target_id == "all" or event.user_id == target_id]
        category_pref = _category_preferences(user_events)
        product_counts = Counter(event.product_id for event in events if event.product_id)
        purchased = {event.product_id for event in user_events if event.event_type == "payment_success" and event.product_id}
        product_meta = _product_metadata(events)
        recommendations = []
        scored_products = []
        for product_id, count in product_counts.items():
            meta = product_meta.get(product_id, {})
            category = str(meta.get("category") or product_id)
            category_score = min(category_pref.get(category, 0) * 6, 30)
            collaborative_score = min(count * 3, 25)
            heat_score = min(_recent_heat(product_id, events), 20)
            price_score = _price_match_score(user_events, meta)
            novelty_score = 10 if product_id not in purchased else -20
            score = max(min(category_score + collaborative_score + heat_score + price_score + novelty_score, 100), 0)
            scored_products.append((product_id, score, category_score, collaborative_score, heat_score, price_score, novelty_score))
        scored_products.sort(key=lambda item: item[1], reverse=True)
        for idx, (product_id, score, category_score, collaborative_score, heat_score, price_score, novelty_score) in enumerate(scored_products[:5], start=1):
            reasons = []
            if category_score:
                reasons.append("user category preference matched")
            if collaborative_score:
                reasons.append("popular among similar recent behavior")
            if heat_score:
                reasons.append("recent product heat is strong")
            if price_score:
                reasons.append("price band matches user history")
            if novelty_score > 0:
                reasons.append("not purchased by this user")
            recommendations.append(
                {
                    "insightId": f"rec-{target_id}-{idx}",
                    "targetType": "user",
                    "targetId": target_id,
                    "productId": product_id,
                    "basisType": "browse_history",
                    "reason": "; ".join(reasons) or "composite retail behavior score",
                    "priority": "high" if score >= 75 else "medium" if score >= 45 else "low",
                    "score": round(score, 2),
                    "scoreBreakdown": {
                        "category": round(category_score, 2),
                        "collaborative": round(collaborative_score, 2),
                        "heat": round(heat_score, 2),
                        "price": round(price_score, 2),
                        "novelty": round(novelty_score, 2),
                    },
                    "algorithmVersion": "hybrid-retail-v2",
                }
            )
        self._save_recommendations(target_id, recommendations)
        return recommendations

    def list_recommendations(self, target_id: str) -> list[dict[str, object]]:
        if not use_mysql_persistence():
            return []
        with SessionLocal() as session:
            rows = session.scalars(
                select(RecommendationInsight)
                .where(RecommendationInsight.target_id == target_id)
                .order_by(RecommendationInsight.score.desc(), RecommendationInsight.generated_at.desc())
            ).all()
            return [self._row_to_dict(row) for row in rows]

    def _save_recommendations(
        self, target_id: str, recommendations: list[dict[str, object]]
    ) -> None:
        if not use_mysql_persistence():
            return
        now = utcnow().replace(tzinfo=None)
        with SessionLocal() as session:
            session.execute(
                delete(RecommendationInsight).where(RecommendationInsight.target_id == target_id)
            )
            for item in recommendations:
                session.add(
                    RecommendationInsight(
                        insight_id=str(item["insightId"]),
                        target_type=str(item["targetType"]),
                        target_id=str(item["targetId"]),
                        product_id=str(item["productId"]),
                        basis_type=str(item["basisType"]),
                        reason=str(item["reason"]),
                        priority=str(item["priority"]),
                        score=float(item["score"]),
                        generated_at=now,
                    )
                )
            session.commit()

    def _row_to_dict(self, row: RecommendationInsight) -> dict[str, object]:
        return {
            "insightId": row.insight_id,
            "targetType": row.target_type,
            "targetId": row.target_id,
            "productId": row.product_id,
            "basisType": row.basis_type,
            "reason": row.reason,
            "priority": row.priority,
            "score": float(row.score),
            "algorithmVersion": "hybrid-retail-v2",
            "generatedAt": row.generated_at.isoformat(),
        }


def _category_preferences(events: list[BehaviorEventRecord]) -> dict[str, float]:
    weights = {"browse": 1, "click": 2, "favorite": 4, "cart_add": 6, "payment_success": 8}
    preferences: dict[str, float] = defaultdict(float)
    for event in events:
        category = event.metadata.get("category") or event.product_id
        if not category:
            continue
        preferences[str(category)] += weights.get(event.event_type, 0)
    return preferences


def _product_metadata(events: list[BehaviorEventRecord]) -> dict[str, dict[str, object]]:
    metadata: dict[str, dict[str, object]] = {}
    for event in events:
        if not event.product_id:
            continue
        metadata.setdefault(event.product_id, {}).update(event.metadata)
    return metadata


def _recent_heat(product_id: str, events: list[BehaviorEventRecord]) -> float:
    weights = {"browse": 1, "click": 2, "favorite": 3, "cart_add": 5, "payment_success": 8}
    now = utcnow().replace(tzinfo=None)
    score = 0.0
    for event in events:
        if event.product_id != product_id:
            continue
        occurred_at = event.occurred_at.replace(tzinfo=None) if isinstance(event.occurred_at, datetime) else now
        age_days = max((now - occurred_at).total_seconds() / 86400, 0)
        score += weights.get(event.event_type, 0) * exp(-age_days / 14)
    return score


def _price_match_score(events: list[BehaviorEventRecord], metadata: dict[str, object]) -> float:
    prices = [_event_price(event.metadata) for event in events if _event_price(event.metadata) > 0]
    price = _event_price(metadata)
    if not prices or price <= 0:
        return 0
    avg_price = sum(prices) / len(prices)
    if avg_price <= 0:
        return 0
    distance = abs(price - avg_price) / avg_price
    return max(10 * (1 - min(distance, 1)), 0)


def _event_price(metadata: dict[str, object]) -> float:
    try:
        return max(float(metadata.get("price", metadata.get("amount", 0))), 0)
    except (TypeError, ValueError):
        return 0
