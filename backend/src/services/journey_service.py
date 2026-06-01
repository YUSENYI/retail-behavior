from __future__ import annotations

from security.audit import audit_recorder
from security.auth import Principal, assert_allowed
from services.behavior_event_repository import BehaviorEventRecord, BehaviorEventRepository, repository


class JourneyService:
    def __init__(self, repo: BehaviorEventRepository = repository) -> None:
        self.repo = repo

    def get_journey(self, principal: Principal, subject_id: str) -> list[BehaviorEventRecord]:
        assert_allowed(principal, "journey", "view")
        audit_recorder.log(principal, "query", "journey", subject_id)
        events = [
            event
            for event in self.repo.query()
            if event.user_id == subject_id or event.visitor_id == subject_id or event.session_id == subject_id
        ]
        return sorted(events, key=lambda event: event.occurred_at)
