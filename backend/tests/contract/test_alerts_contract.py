from __future__ import annotations

from helpers import load_openapi


def test_alert_contracts_exist() -> None:
    spec = load_openapi()
    assert "/alerts" in spec["paths"]
    assert "/alerts/{alertId}" in spec["paths"]
