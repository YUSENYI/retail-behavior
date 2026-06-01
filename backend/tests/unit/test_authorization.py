from __future__ import annotations

import pytest

from domain.enums import DataScope, Role
from security.audit import AuditRecorder
from security.auth import PermissionDenied, Principal, assert_allowed, can


def test_admin_can_export_all_scope() -> None:
    principal = Principal("admin", Role.ADMINISTRATOR, DataScope.ALL)
    assert can(principal, "report", "export")


def test_read_only_cannot_export() -> None:
    principal = Principal("viewer", Role.READ_ONLY_VIEWER, DataScope.NONE)
    with pytest.raises(PermissionDenied):
        assert_allowed(principal, "report", "export")


def test_denied_action_can_be_audited() -> None:
    recorder = AuditRecorder()
    principal = Principal("viewer", Role.READ_ONLY_VIEWER, DataScope.NONE)
    record = recorder.log(principal, "export", "report", result="denied", reason="no export permission")
    assert record.result == "denied"
    assert record.reason == "no export permission"
