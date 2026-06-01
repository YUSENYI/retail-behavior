from __future__ import annotations

from helpers import load_openapi


def test_behavior_query_contracts_exist() -> None:
    spec = load_openapi()
    assert "/behavior/events" in spec["paths"]
    assert "/behavior/journeys/{subjectId}" in spec["paths"]
