from __future__ import annotations

from helpers import load_openapi


def test_funnel_and_product_heat_contracts_exist() -> None:
    spec = load_openapi()
    assert "/analytics/funnel" in spec["paths"]
    assert "/analytics/product-heat" in spec["paths"]
