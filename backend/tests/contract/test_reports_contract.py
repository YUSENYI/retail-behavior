from __future__ import annotations

from helpers import load_openapi


def test_report_contracts_exist() -> None:
    spec = load_openapi()
    assert "/reports" in spec["paths"]
    assert "/reports/{reportType}/exports" in spec["paths"]
