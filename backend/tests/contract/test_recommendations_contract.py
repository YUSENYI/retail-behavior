from __future__ import annotations

from helpers import load_openapi


def test_recommendation_contract_exists() -> None:
    spec = load_openapi()
    assert "/recommendations/analysis" in spec["paths"]
