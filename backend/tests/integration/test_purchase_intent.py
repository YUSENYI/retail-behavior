from __future__ import annotations

from conftest import load_fixture
from services.behavior_event_repository import InMemoryBehaviorEventRepository
from services.behavior_ingestion_service import BehaviorIngestionService
from services.purchase_intent_service import PurchaseIntentService


def test_purchase_intent_detects_high_intent_after_payment() -> None:
    repo = InMemoryBehaviorEventRepository()
    BehaviorIngestionService(repo).ingest_batch(load_fixture()["events"])
    intent = PurchaseIntentService().classify("user-001", repo.accepted_events())
    assert intent["intentLevel"] == "high"
