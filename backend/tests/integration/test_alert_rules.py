from __future__ import annotations

from conftest import load_fixture
from services.alert_rule_service import AlertRuleService
from services.behavior_event_repository import InMemoryBehaviorEventRepository
from services.behavior_ingestion_service import BehaviorIngestionService


def test_behavior_data_anomaly_alert_is_generated() -> None:
    repo = InMemoryBehaviorEventRepository()
    BehaviorIngestionService(repo).ingest_batch(load_fixture()["events"])
    alerts = AlertRuleService().evaluate(repo.all_attempts())
    assert any(alert["alertType"] == "behavior_data_anomaly" for alert in alerts)
