from __future__ import annotations

from helpers import repo_root


def test_shared_openapi_matches_feature_contract() -> None:
    root = repo_root()
    feature_contract = root / "specs/001-retail-behavior-analytics/contracts/openapi.yaml"
    shared_contract = root / "shared/contracts/openapi.yaml"
    assert shared_contract.read_text(encoding="utf-8") == feature_contract.read_text(encoding="utf-8")
