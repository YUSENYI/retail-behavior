from __future__ import annotations

from services.alert_rule_service import AlertRuleService
from services.behavior_event_repository import repository
from services.recommendation_service import RecommendationService


def refresh_alerts_and_recommendations(target_id: str = "all") -> dict[str, object]:
    events = repository.query()
    return {
        "alerts": AlertRuleService().evaluate(events),
        "recommendations": RecommendationService().recommend(target_id, events),
    }
