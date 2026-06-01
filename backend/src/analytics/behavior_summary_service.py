from __future__ import annotations

from collections import Counter

from domain.common import utcnow
from services.behavior_event_repository import BehaviorEventRecord


class BehaviorSummaryService:
    def summarize(self, events: list[BehaviorEventRecord]) -> dict[str, object]:
        counts = Counter(event.event_type for event in events)
        sources = Counter(event.channel_id for event in events)
        keywords = Counter(event.search_keyword for event in events if event.search_keyword)
        metrics = [
            {"key": "visits", "name": "Visits", "value": counts["browse"], "unit": "count", "metricVersion": "v1"},
            {"key": "clicks", "name": "Clicks", "value": counts["click"], "unit": "count", "metricVersion": "v1"},
            {"key": "cart_adds", "name": "Cart Additions", "value": counts["cart_add"], "unit": "count", "metricVersion": "v1"},
            {"key": "orders", "name": "Orders", "value": counts["order_submit"], "unit": "count", "metricVersion": "v1"},
            {"key": "payments", "name": "Payments", "value": counts["payment_success"], "unit": "count", "metricVersion": "v1"},
        ]
        return {
            "metrics": metrics,
            "sourceDistribution": dict(sources),
            "searchKeywords": dict(keywords),
            "freshnessAt": utcnow().isoformat(),
        }
