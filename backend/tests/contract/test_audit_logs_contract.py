from __future__ import annotations

from helpers import load_openapi


def test_audit_logs_contract_exists() -> None:
    spec = load_openapi()
    assert "/audit-logs" in spec["paths"]
