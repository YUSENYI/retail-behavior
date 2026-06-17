from __future__ import annotations

from security.audit import AuditRecord, audit_recorder
from security.auth import Principal, assert_allowed


def list_audit_logs(principal: Principal, action: str | None = None) -> list[AuditRecord]:
    assert_allowed(principal, "audit", "manage")
    if action is None:
        return list(audit_recorder.records)
    return [record for record in audit_recorder.records if record.action == action]
