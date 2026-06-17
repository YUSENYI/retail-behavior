from __future__ import annotations

from api.compat import APIRouter
from api.filters import AnalysisFilters
from api.schemas.behavior_events import BehaviorEventBatchRequest
from security.auth import Principal, Role, DataScope
from services.behavior_ingestion_service import BehaviorIngestionService
from services.behavior_query_service import BehaviorQueryService
from services.journey_service import JourneyService

router = APIRouter()
default_principal = Principal("demo", Role.ADMINISTRATOR, DataScope.ALL)


@router.post("/events/behavior")
def ingest_behavior_events(request: BehaviorEventBatchRequest) -> dict[str, object]:
    return BehaviorIngestionService().ingest_batch([event.model_dump() for event in request.events], default_principal)


@router.get("/behavior/events")
def list_behavior_events() -> list[object]:
    return BehaviorQueryService().list_events(default_principal, AnalysisFilters())


@router.get("/behavior/journeys/{subject_id}")
def get_behavior_journey(subject_id: str) -> list[object]:
    return JourneyService().get_journey(default_principal, subject_id)
