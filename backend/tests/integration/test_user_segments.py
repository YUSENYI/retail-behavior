from __future__ import annotations

from conftest import load_fixture
from services.behavior_event_repository import InMemoryBehaviorEventRepository
from services.behavior_ingestion_service import BehaviorIngestionService
from services.segment_service import SegmentService


def test_segment_rules_include_high_value_paid_user() -> None:
    repo = InMemoryBehaviorEventRepository()
    BehaviorIngestionService(repo).ingest_batch(load_fixture()["events"])
    segments = SegmentService().classify("user-001", repo.accepted_events())
    assert any(segment["segmentType"] == "high_value" for segment in segments)
