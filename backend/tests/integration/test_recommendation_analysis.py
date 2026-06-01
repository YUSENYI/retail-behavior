from __future__ import annotations

from conftest import load_fixture
from services.behavior_event_repository import InMemoryBehaviorEventRepository
from services.behavior_ingestion_service import BehaviorIngestionService
from services.recommendation_service import RecommendationService


def test_recommendation_includes_explainable_basis() -> None:
    repo = InMemoryBehaviorEventRepository()
    BehaviorIngestionService(repo).ingest_batch(load_fixture()["events"])
    recommendations = RecommendationService().recommend("user-001", repo.accepted_events())
    assert recommendations[0]["basisType"] == "browse_history"
    assert recommendations[0]["reason"]
