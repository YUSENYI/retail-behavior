from __future__ import annotations

import pytest

from domain.common import utcnow
from domain.enums import DataScope, Role
from reports.export_service import ExportService
from security.auth import PermissionDenied, Principal
from services.behavior_event_repository import BehaviorEventRecord, InMemoryBehaviorEventRepository


def test_export_denies_read_only_user() -> None:
    with pytest.raises(PermissionDenied):
        ExportService().create_export(Principal("viewer", Role.READ_ONLY_VIEWER, DataScope.NONE), "behavior_detail", {})


def test_export_creates_ready_csv_file(tmp_path) -> None:
    repo = InMemoryBehaviorEventRepository()
    repo.ingest(
        BehaviorEventRecord(
            event_id="evt-export-1",
            source_system="web",
            event_type="payment_success",
            session_id="session-export-123",
            channel_id="search",
            occurred_at=utcnow(),
            user_id="user-export-123",
            product_id="SKU-001",
            order_id="order-export-123",
            payment_id="payment-export-123",
            metadata={"price": 199.0},
        )
    )

    result = ExportService(repo=repo, storage_path=tmp_path).create_export(
        Principal("analyst", Role.ANALYST, DataScope.ALL),
        "behavior_detail",
        {"channelId": "search"},
    )

    exported_file = tmp_path / str(result["fileName"])
    csv_text = exported_file.read_text(encoding="utf-8-sig")
    assert result["status"] == "ready"
    assert str(result["exportUri"]).startswith("data:text/csv")
    assert "evt-export-1" in csv_text
    assert "us***-123" in csv_text
