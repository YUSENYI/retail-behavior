from __future__ import annotations

from helpers import load_openapi


def test_segments_and_purchase_intent_contracts_exist() -> None:
    spec = load_openapi()
    assert "/segments" in spec["paths"]
    assert "/segments/{segmentId}/users" in spec["paths"]
    assert "/purchase-intent/users" in spec["paths"]
