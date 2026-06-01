from __future__ import annotations

from analytics.funnel_service import FunnelService
from services.behavior_event_repository import BehaviorEventRecord


class AlertRuleService:
    def evaluate(self, events: list[BehaviorEventRecord]) -> list[dict[str, object]]:
        alerts: list[dict[str, object]] = []
        invalid_count = sum(1 for event in events if event.idempotency_state.value in {"invalid", "quarantined"})
        if invalid_count:
            alerts.append({"alertId": "behavior-data-anomaly", "alertType": "behavior_data_anomaly", "severity": "high", "status": "new", "triggerReason": f"{invalid_count} invalid behavior events"})
        funnel = FunnelService().analyze(events)
        for stage in funnel["stages"]:
            if stage["dropoffRate"] > 80:
                alerts.append({"alertId": f"conversion-{stage['stage']}", "alertType": "conversion_anomaly", "severity": "medium", "status": "new", "triggerReason": f"{stage['stage']} dropoff above threshold"})
        return alerts
