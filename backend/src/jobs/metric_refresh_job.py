from __future__ import annotations

from analytics.behavior_summary_service import BehaviorSummaryService
from analytics.funnel_service import FunnelService
from analytics.product_heat_service import ProductHeatService
from services.behavior_event_repository import repository


def refresh_metrics() -> dict[str, object]:
    events = repository.accepted_events()
    return {
        "summary": BehaviorSummaryService().summarize(events),
        "funnel": FunnelService().analyze(events),
        "productHeat": ProductHeatService().rank(events),
    }
