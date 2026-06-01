from __future__ import annotations

from collections import Counter

from services.behavior_event_repository import BehaviorEventRecord


class RecommendationService:
    def recommend(self, target_id: str, events: list[BehaviorEventRecord]) -> list[dict[str, object]]:
        product_counts = Counter(event.product_id for event in events if event.product_id)
        recommendations = []
        for idx, (product_id, count) in enumerate(product_counts.most_common(5), start=1):
            recommendations.append(
                {
                    "insightId": f"rec-{target_id}-{idx}",
                    "targetType": "user",
                    "targetId": target_id,
                    "productId": product_id,
                    "basisType": "browse_history",
                    "reason": "popular among recent behavior records",
                    "priority": "high" if idx == 1 else "medium",
                    "score": max(100 - idx * 10, 10),
                }
            )
        return recommendations
