from __future__ import annotations

from datetime import datetime, timedelta

from domain.common import utcnow
from services.behavior_event_repository import BehaviorEventRecord


STAGE_EVENTS = [
    ("browse", "browse"),
    ("click", "click"),
    ("cart", "cart_add"),
    ("order", "order_submit"),
    ("payment", "payment_success"),
]


class FunnelService:
    def analyze(self, events: list[BehaviorEventRecord]) -> dict[str, object]:
        ordered_paths = _ordered_paths(events)
        subjects_by_stage = _subjects_by_ordered_stage(ordered_paths)
        stages = []
        biggest_stage = "browse"
        biggest_dropoff = -1
        for index, (stage, _) in enumerate(STAGE_EVENTS):
            entered = len(subjects_by_stage[stage])
            converted = (
                entered
                if index == len(STAGE_EVENTS) - 1
                else len(subjects_by_stage[STAGE_EVENTS[index + 1][0]])
            )
            denominator = entered
            dropoff = 0 if denominator == 0 else max(denominator - converted, 0)
            conversion_rate = 0 if denominator == 0 else min(max((converted / denominator) * 100, 0), 100)
            dropoff_rate = 0 if denominator == 0 else min(max((dropoff / denominator) * 100, 0), 100)
            if dropoff > biggest_dropoff:
                biggest_dropoff = dropoff
                biggest_stage = stage
            stages.append(
                {
                    "stage": stage,
                    "enteredCount": entered,
                    "convertedCount": converted,
                    "dropoffCount": dropoff,
                    "conversionRate": round(conversion_rate, 2),
                    "dropoffRate": round(dropoff_rate, 2),
                }
            )
        return {
            "stages": stages,
            "biggestDropoffStage": biggest_stage,
            "windowHours": 168,
            "algorithmVersion": "ordered-path-v2",
            "freshnessAt": utcnow().isoformat(),
        }


def _ordered_paths(events: list[BehaviorEventRecord]) -> dict[str, list[BehaviorEventRecord]]:
    paths: dict[str, list[BehaviorEventRecord]] = {}
    for event in events:
        paths.setdefault(event.subject_id, []).append(event)
    return {
        subject: sorted(subject_events, key=lambda event: _timestamp(event.occurred_at))
        for subject, subject_events in paths.items()
    }


def _subjects_by_ordered_stage(
    paths: dict[str, list[BehaviorEventRecord]],
    window: timedelta = timedelta(days=7),
) -> dict[str, set[str]]:
    subjects_by_stage = {stage: set() for stage, _ in STAGE_EVENTS}
    for subject, events in paths.items():
        next_index = 0
        started_at: datetime | None = None
        for event in events:
            if next_index >= len(STAGE_EVENTS):
                break
            stage, expected_type = STAGE_EVENTS[next_index]
            if event.event_type != expected_type:
                continue
            occurred_at = _timestamp(event.occurred_at)
            if started_at is None:
                started_at = occurred_at
            if occurred_at - started_at > window:
                break
            subjects_by_stage[stage].add(subject)
            next_index += 1
    return subjects_by_stage


def _timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    return datetime.min
