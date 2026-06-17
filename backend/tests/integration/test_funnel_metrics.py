from __future__ import annotations

from analytics.funnel_service import FunnelService
from conftest import load_fixture
from services.behavior_event_repository import InMemoryBehaviorEventRepository
from services.behavior_ingestion_service import BehaviorIngestionService


def test_funnel_rates_are_bounded() -> None:
    repo = InMemoryBehaviorEventRepository()
    BehaviorIngestionService(repo).ingest_batch(load_fixture()["events"])
    funnel = FunnelService().analyze(repo.accepted_events())
    assert all(0 <= stage["conversionRate"] <= 100 for stage in funnel["stages"])
    assert all(stage["dropoffCount"] >= 0 for stage in funnel["stages"])


def test_empty_funnel_does_not_create_artificial_dropoff() -> None:
    funnel = FunnelService().analyze([])
    assert all(stage["enteredCount"] == 0 for stage in funnel["stages"])
    assert all(stage["dropoffCount"] == 0 for stage in funnel["stages"])
    assert all(stage["dropoffRate"] == 0 for stage in funnel["stages"])
