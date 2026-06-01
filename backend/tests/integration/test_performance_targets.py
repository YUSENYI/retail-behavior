from __future__ import annotations

from conftest import load_fixture


def test_validation_fixture_represents_mvp_scale_assumptions() -> None:
    assert len(load_fixture()["events"]) >= 7
