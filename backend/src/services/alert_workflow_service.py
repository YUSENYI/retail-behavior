from __future__ import annotations

from domain.enums import AlertStatus
from security.audit import audit_recorder
from security.auth import Principal, assert_allowed


ALLOWED_TRANSITIONS = {
    AlertStatus.NEW: {AlertStatus.ACKNOWLEDGED, AlertStatus.IGNORED},
    AlertStatus.ACKNOWLEDGED: {AlertStatus.PROCESSING, AlertStatus.IGNORED},
    AlertStatus.PROCESSING: {AlertStatus.RESOLVED},
}


class AlertWorkflowService:
    def transition(self, principal: Principal, current: str, desired: str, alert_id: str) -> str:
        assert_allowed(principal, "alert", "handle")
        current_status = AlertStatus(current)
        desired_status = AlertStatus(desired)
        if desired_status not in ALLOWED_TRANSITIONS.get(current_status, set()):
            raise ValueError(f"invalid alert transition {current}->{desired}")
        audit_recorder.log(principal, "alert_handling", "alert", alert_id)
        return desired_status.value
