from __future__ import annotations

from analytics.behavior_summary_service import BehaviorSummaryService
from conftest import load_fixture
from services.behavior_event_repository import InMemoryBehaviorEventRepository
from services.behavior_ingestion_service import BehaviorIngestionService


def test_behavior_summary_counts_accepted_events() -> None:
    repo = InMemoryBehaviorEventRepository()
    BehaviorIngestionService(repo).ingest_batch(load_fixture()["events"])
    summary = BehaviorSummaryService().summarize(repo.accepted_events())
    values = {metric["key"]: metric["value"] for metric in summary["metrics"]}
    assert values["visits"] == 1
    assert values["clicks"] == 1
    assert values["payments"] == 1
