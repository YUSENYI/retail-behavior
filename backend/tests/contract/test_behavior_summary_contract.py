from __future__ import annotations

from helpers import load_openapi


def test_behavior_summary_contract_exists() -> None:
    spec = load_openapi()
    assert "/analytics/behavior-summary" in spec["paths"]
