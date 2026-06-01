from __future__ import annotations

from conftest import load_fixture
from services.behavior_event_repository import InMemoryBehaviorEventRepository
from services.behavior_ingestion_service import BehaviorIngestionService


def test_duplicate_and_invalid_events_are_not_counted_as_accepted() -> None:
    service = BehaviorIngestionService(InMemoryBehaviorEventRepository())
    result = service.ingest_batch(load_fixture()["events"])
    assert result["acceptedCount"] == 5
    assert result["duplicateCount"] == 1
    assert result["invalidCount"] == 1
