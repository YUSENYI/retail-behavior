from __future__ import annotations

from api.filters import AnalysisFilters
from security.audit import audit_recorder
from security.auth import Principal, assert_allowed
from services.behavior_event_repository import BehaviorEventRecord, BehaviorEventRepository, repository


class BehaviorQueryService:
    def __init__(self, repo: BehaviorEventRepository = repository) -> None:
        self.repo = repo

    def list_events(self, principal: Principal, filters: AnalysisFilters | None = None) -> list[BehaviorEventRecord]:
        assert_allowed(principal, "behavior_event", "view", getattr(filters, "channel_id", None))
        audit_recorder.log(principal, "query", "behavior_event")
        return self.repo.query(filters)
