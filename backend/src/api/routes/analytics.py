from __future__ import annotations

from api.compat import APIRouter
from analytics.behavior_summary_service import BehaviorSummaryService
from analytics.funnel_service import FunnelService
from analytics.product_heat_service import ProductHeatService
from services.behavior_event_repository import repository

router = APIRouter()


@router.get("/analytics/behavior-summary")
def behavior_summary() -> dict[str, object]:
    return BehaviorSummaryService().summarize(repository.accepted_events())


@router.get("/analytics/funnel")
def funnel() -> dict[str, object]:
    return FunnelService().analyze(repository.accepted_events())


@router.get("/analytics/product-heat")
def product_heat(rankBy: str | None = None, rank_by: str | None = None) -> dict[str, object]:
    return ProductHeatService().rank(repository.accepted_events(), rankBy or rank_by or "browse")
