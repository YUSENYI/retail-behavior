from __future__ import annotations

from helpers import load_openapi


def test_behavior_ingestion_contract_exists() -> None:
    spec = load_openapi()
    assert "/events/behavior" in spec["paths"]
    assert "post" in spec["paths"]["/events/behavior"]
