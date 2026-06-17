from __future__ import annotations

from collections import Counter
from datetime import datetime

from domain.common import utcnow
from services.behavior_event_repository import BehaviorEventRecord


class BehaviorSummaryService:
    def summarize(self, events: list[BehaviorEventRecord]) -> dict[str, object]:
        counts = Counter(event.event_type for event in events)
        sources = Counter(event.channel_id for event in events)
        keywords = Counter(event.search_keyword for event in events if event.search_keyword)
        users = {event.subject_id for event in events}
        sessions = {event.session_id for event in events if event.session_id}
        sales_amount = sum(_event_amount(event) for event in events if event.event_type == "payment_success")
        avg_order_value = sales_amount / counts["payment_success"] if counts["payment_success"] else 0
        visit_count = counts["browse"]
        click_count = counts["click"]
        cart_count = counts["cart_add"]
        order_count = counts["order_submit"]
        payment_count = counts["payment_success"]
        click_through_rate = _rate(click_count, visit_count)
        cart_rate = _rate(cart_count, visit_count)
        order_rate = _rate(order_count, cart_count)
        payment_conversion_rate = _rate(payment_count, visit_count)
        browse_duration_seconds = _browse_duration_seconds(events)
        metrics = [
            {"key": "visits", "name": "Visits", "value": visit_count, "unit": "count", "metricVersion": "v2"},
            {"key": "unique_users", "name": "Unique Users", "value": len(users), "unit": "count", "metricVersion": "v2"},
            {"key": "sessions", "name": "Sessions", "value": len(sessions), "unit": "count", "metricVersion": "v2"},
            {"key": "clicks", "name": "Clicks", "value": click_count, "unit": "count", "metricVersion": "v2"},
            {"key": "cart_adds", "name": "Cart Additions", "value": cart_count, "unit": "count", "metricVersion": "v2"},
            {"key": "orders", "name": "Orders", "value": order_count, "unit": "count", "metricVersion": "v2"},
            {"key": "payments", "name": "Payments", "value": payment_count, "unit": "count", "metricVersion": "v2"},
            {"key": "sales_amount", "name": "Sales Amount", "value": round(sales_amount, 2), "unit": "amount", "metricVersion": "v2"},
            {"key": "average_order_value", "name": "Average Order Value", "value": round(avg_order_value, 2), "unit": "amount", "metricVersion": "v2"},
            {"key": "browse_duration_seconds", "name": "Browse Duration", "value": browse_duration_seconds, "unit": "seconds", "metricVersion": "v2"},
            {"key": "click_through_rate", "name": "Click Through Rate", "value": click_through_rate, "unit": "percent", "metricVersion": "v2"},
            {"key": "cart_rate", "name": "Cart Rate", "value": cart_rate, "unit": "percent", "metricVersion": "v2"},
            {"key": "order_rate", "name": "Order Rate", "value": order_rate, "unit": "percent", "metricVersion": "v2"},
            {"key": "payment_conversion_rate", "name": "Payment Conversion Rate", "value": payment_conversion_rate, "unit": "percent", "metricVersion": "v2"},
        ]
        return {
            "metrics": metrics,
            "sourceDistribution": dict(sources),
            "searchKeywords": dict(keywords),
            "metricDefinitions": {
                "payment_conversion_rate": "payment_success / browse within the selected event set",
                "browse_duration_seconds": "sum of adjacent in-session event gaps capped at 30 minutes",
            },
            "freshnessAt": utcnow().isoformat(),
        }


def _rate(numerator: int | float, denominator: int | float) -> float:
    if denominator <= 0:
        return 0
    return round(min(max((numerator / denominator) * 100, 0), 100), 2)


def _event_amount(event: BehaviorEventRecord) -> float:
    value = event.metadata.get("amount", event.metadata.get("price", 0))
    try:
        return max(float(value), 0)
    except (TypeError, ValueError):
        return 0


def _browse_duration_seconds(events: list[BehaviorEventRecord]) -> int:
    duration = 0
    sessions: dict[str, list[BehaviorEventRecord]] = {}
    for event in events:
        sessions.setdefault(event.session_id, []).append(event)
    for session_events in sessions.values():
        ordered = sorted(session_events, key=lambda event: _timestamp(event.occurred_at))
        for current, next_event in zip(ordered, ordered[1:]):
            gap = int((_timestamp(next_event.occurred_at) - _timestamp(current.occurred_at)).total_seconds())
            if 0 < gap <= 1800:
                duration += gap
    return duration


def _timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    return datetime.min
