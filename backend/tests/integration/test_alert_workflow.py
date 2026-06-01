from __future__ import annotations

from domain.enums import DataScope, Role
from security.auth import Principal
from services.alert_workflow_service import AlertWorkflowService


def test_alert_transition_records_status() -> None:
    status = AlertWorkflowService().transition(Principal("ops", Role.OPERATIONS_MANAGER, DataScope.ALL), "new", "acknowledged", "alert-1")
    assert status == "acknowledged"
