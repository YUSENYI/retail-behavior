from __future__ import annotations

from api.routes.system import reset_system_data
from services.behavior_event_repository import repository


def test_system_reset_clears_in_memory_behavior_data() -> None:
    result = reset_system_data()
    assert result["status"] == "reset"
    assert repository.accepted_events() == []
