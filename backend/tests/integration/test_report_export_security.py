from __future__ import annotations

import pytest

from domain.enums import DataScope, Role
from reports.export_service import ExportService
from security.auth import PermissionDenied, Principal


def test_export_denies_read_only_user() -> None:
    with pytest.raises(PermissionDenied):
        ExportService().create_export(Principal("viewer", Role.READ_ONLY_VIEWER, DataScope.NONE), "behavior_detail", {})
