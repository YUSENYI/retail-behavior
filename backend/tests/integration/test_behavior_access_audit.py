from __future__ import annotations

from api.filters import AnalysisFilters
from conftest import load_fixture
from domain.enums import DataScope, Role
from security.audit import audit_recorder
from security.auth import Principal
from services.behavior_event_repository import InMemoryBehaviorEventRepository
from services.behavior_ingestion_service import BehaviorIngestionService
from services.behavior_query_service import BehaviorQueryService


def test_behavior_query_records_audit() -> None:
    repo = InMemoryBehaviorEventRepository()
    BehaviorIngestionService(repo).ingest_batch(load_fixture()["events"])
    principal = Principal("analyst", Role.ANALYST, DataScope.ALL)
    events = BehaviorQueryService(repo).list_events(principal, AnalysisFilters(channel_id="search"))
    assert len(events) >= 5
    assert any(record.action == "query" and record.resource_type == "behavior_event" for record in audit_recorder.records)
