from __future__ import annotations

from helpers import load_openapi


def test_profile_contract_exists() -> None:
    spec = load_openapi()
    assert "/profiles/{userId}" in spec["paths"]
