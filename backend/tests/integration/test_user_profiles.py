from __future__ import annotations

from conftest import load_fixture
from services.behavior_event_repository import InMemoryBehaviorEventRepository
from services.behavior_ingestion_service import BehaviorIngestionService
from services.profile_service import ProfileService


def test_profile_dimensions_are_calculated() -> None:
    repo = InMemoryBehaviorEventRepository()
    BehaviorIngestionService(repo).ingest_batch(load_fixture()["events"])
    profile = ProfileService().build_profile("user-001", repo.accepted_events())
    assert profile["activityLevel"] == "high"
    assert profile["valueGrade"] == "high"
