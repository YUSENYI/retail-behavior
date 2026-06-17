from __future__ import annotations

from api.compat import APIRouter
from services.ai_preference_service import AIUserPreferenceService
from services.behavior_event_repository import repository

router = APIRouter()


@router.get("/ai/preference-categories")
def preference_categories(target_id: str = "all", top_n: int = 5) -> dict[str, object]:
    return AIUserPreferenceService().classify(
        repository.accepted_events(),
        target_id=None if target_id == "all" else target_id,
        top_n=top_n,
    )
