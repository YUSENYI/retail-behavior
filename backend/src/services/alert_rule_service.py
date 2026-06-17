from __future__ import annotations

from collections import Counter
from statistics import mean, pstdev

from analytics.funnel_service import FunnelService
from domain.common import utcnow
from models.alerts_recommendations import Alert
from models.database import SessionLocal, use_mysql_persistence
from sqlalchemy import select
from services.behavior_event_repository import BehaviorEventRecord


class AlertRuleService:
    def evaluate(self, events: list[BehaviorEventRecord] | None = None) -> list[dict[str, object]]:
        if events is None:
            return self.list_alerts()
        return self.refresh_alerts(events)

    def refresh_alerts(self, events: list[BehaviorEventRecord]) -> list[dict[str, object]]:
        alerts: list[dict[str, object]] = []
        invalid_count = sum(1 for event in events if event.idempotency_state.value in {"invalid", "quarantined"})
        if invalid_count:
            alerts.append({"alertId": "behavior-data-anomaly", "alertType": "behavior_data_anomaly", "severity": "high", "status": "new", "triggerReason": f"{invalid_count} invalid behavior events", "algorithmVersion": "retail-alert-v2"})
        funnel = FunnelService().analyze(events)
        for stage in funnel["stages"]:
            if stage["dropoffRate"] > 80:
                alerts.append({"alertId": f"conversion-{stage['stage']}", "alertType": "conversion_anomaly", "severity": "medium", "status": "new", "triggerReason": f"{stage['stage']} dropoff above threshold", "algorithmVersion": "retail-alert-v2"})
        for alert in _product_conversion_alerts(events):
            alerts.append(alert)
        for alert in _channel_flow_alerts(events):
            alerts.append(alert)
        self._save_alerts(alerts)
        return alerts

    def list_alerts(self) -> list[dict[str, object]]:
        if not use_mysql_persistence():
            return []
        with SessionLocal() as session:
            rows = session.scalars(select(Alert).order_by(Alert.created_at.desc())).all()
            return [self._row_to_dict(row) for row in rows]

    def _save_alerts(self, alerts: list[dict[str, object]]) -> None:
        if not use_mysql_persistence():
            return
        now = utcnow().replace(tzinfo=None)
        with SessionLocal() as session:
            for item in alerts:
                alert_id = str(item["alertId"])
                row = session.get(Alert, alert_id)
                if row is None:
                    row = Alert(
                        alert_id=alert_id,
                        alert_type=str(item["alertType"]),
                        severity=str(item["severity"]),
                        status=str(item["status"]),
                        scope_type=None,
                        scope_id=None,
                        trigger_reason=str(item["triggerReason"]),
                        created_at=now,
                        updated_at=now,
                        resolved_at=None,
                        owner_id=None,
                    )
                    session.add(row)
                else:
                    row.alert_type = str(item["alertType"])
                    row.severity = str(item["severity"])
                    row.trigger_reason = str(item["triggerReason"])
                    row.updated_at = now
            session.commit()

    def _row_to_dict(self, row: Alert) -> dict[str, object]:
        return {
            "alertId": row.alert_id,
            "alertType": row.alert_type,
            "severity": row.severity,
            "status": row.status,
            "scopeType": row.scope_type,
            "scopeId": row.scope_id,
            "triggerReason": row.trigger_reason,
            "algorithmVersion": "retail-alert-v2",
            "createdAt": row.created_at.isoformat(),
            "updatedAt": row.updated_at.isoformat() if row.updated_at else None,
        }


def _product_conversion_alerts(events: list[BehaviorEventRecord]) -> list[dict[str, object]]:
    browse_counts = Counter(event.product_id for event in events if event.product_id and event.event_type == "browse")
    payment_counts = Counter(event.product_id for event in events if event.product_id and event.event_type == "payment_success")
    rates = {
        product_id: payment_counts[product_id] / browse_count
        for product_id, browse_count in browse_counts.items()
        if browse_count > 0
    }
    if len(rates) < 3:
        return []
    values = list(rates.values())
    baseline = mean(values)
    deviation = pstdev(values) or 0.01
    alerts: list[dict[str, object]] = []
    for product_id, rate in rates.items():
        z_score = (rate - baseline) / deviation
        if z_score <= -2 and browse_counts[product_id] >= 5:
            alerts.append(
                {
                    "alertId": f"product-conversion-{product_id}",
                    "alertType": "conversion_anomaly",
                    "severity": "high",
                    "status": "new",
                    "triggerReason": f"{product_id} conversion rate is below product baseline",
                    "algorithmVersion": "retail-alert-v2",
                }
            )
    return alerts


def _channel_flow_alerts(events: list[BehaviorEventRecord]) -> list[dict[str, object]]:
    channel_counts = Counter(event.channel_id for event in events if event.channel_id)
    if not channel_counts:
        return []
    total = sum(channel_counts.values())
    alerts = []
    for channel_id, count in channel_counts.items():
        if total >= 20 and count / total < 0.02:
            alerts.append(
                {
                    "alertId": f"channel-flow-{channel_id}",
                    "alertType": "behavior_data_anomaly",
                    "severity": "medium",
                    "status": "new",
                    "triggerReason": f"{channel_id} channel event flow is unusually low",
                    "algorithmVersion": "retail-alert-v2",
                }
            )
    return alerts
