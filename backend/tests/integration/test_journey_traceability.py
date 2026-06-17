from __future__ import annotations

from conftest import load_fixture
from domain.enums import DataScope, Role
from security.auth import Principal
from services.behavior_event_repository import InMemoryBehaviorEventRepository
from services.behavior_ingestion_service import BehaviorIngestionService
from services.journey_service import JourneyService


def test_complete_journey_orders_events_from_visit_to_payment() -> None:
    repo = InMemoryBehaviorEventRepository()
    BehaviorIngestionService(repo).ingest_batch(load_fixture()["events"])
    journey = JourneyService(repo).get_journey(Principal("admin", Role.ADMINISTRATOR, DataScope.ALL), "user-001")
    assert [event.event_type for event in journey] == ["browse", "click", "cart_add", "order_submit", "payment_success"]
