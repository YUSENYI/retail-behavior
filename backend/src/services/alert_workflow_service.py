from __future__ import annotations

from domain.enums import AlertStatus
from domain.common import utcnow
from models.alerts_recommendations import Alert
from models.database import SessionLocal, use_mysql_persistence
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
        if use_mysql_persistence():
            current = self._current_status(alert_id) or current
        current_status = AlertStatus(current)
        desired_status = AlertStatus(desired)
        if desired_status not in ALLOWED_TRANSITIONS.get(current_status, set()):
            raise ValueError(f"invalid alert transition {current}->{desired}")
        self._save_status(alert_id, desired_status.value)
        audit_recorder.log(principal, "alert_handling", "alert", alert_id)
        return desired_status.value

    def _current_status(self, alert_id: str) -> str | None:
        with SessionLocal() as session:
            row = session.get(Alert, alert_id)
            return row.status if row is not None else None

    def _save_status(self, alert_id: str, status: str) -> None:
        if not use_mysql_persistence():
            return
        now = utcnow().replace(tzinfo=None)
        with SessionLocal() as session:
            row = session.get(Alert, alert_id)
            if row is None:
                return
            row.status = status
            row.updated_at = now
            if status in {AlertStatus.RESOLVED.value, AlertStatus.IGNORED.value}:
                row.resolved_at = now
            session.commit()
