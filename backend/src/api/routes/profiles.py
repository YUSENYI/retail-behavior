from __future__ import annotations

from api.compat import APIRouter
from services.behavior_event_repository import repository
from services.profile_service import ProfileService
from services.purchase_intent_service import PurchaseIntentService
from services.segment_service import SegmentService

router = APIRouter()


@router.get("/profiles/{user_id}")
def get_user_profile(user_id: str) -> dict[str, object]:
    return ProfileService().build_profile(user_id, repository.accepted_events())


@router.get("/segments")
def list_segments() -> dict[str, object]:
    return {"items": [{"segmentId": "high_value", "segmentType": "high_value", "name": "High Value", "memberCount": 0, "ruleDescription": "paid users"}]}


@router.get("/segments/{segment_id}/users")
def list_segment_users(segment_id: str) -> dict[str, object]:
    return {"items": [], "segmentId": segment_id}


@router.get("/purchase-intent/users")
def list_purchase_intent_users(user_id: str = "demo-user") -> dict[str, object]:
    return {"items": [PurchaseIntentService().classify(user_id, repository.accepted_events())]}
