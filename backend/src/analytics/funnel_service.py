from __future__ import annotations

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
        subjects_by_stage: dict[str, set[str]] = {}
        for stage, event_type in STAGE_EVENTS:
            subjects_by_stage[stage] = {event.subject_id for event in events if event.event_type == event_type}
        stages = []
        previous_count = 0
        biggest_stage = "browse"
        biggest_dropoff = -1
        for index, (stage, _) in enumerate(STAGE_EVENTS):
            entered = len(subjects_by_stage[stage])
            converted = entered if index == len(STAGE_EVENTS) - 1 else len(subjects_by_stage[STAGE_EVENTS[index + 1][0]])
            denominator = previous_count or entered
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
            previous_count = entered
        return {"stages": stages, "biggestDropoffStage": biggest_stage, "freshnessAt": utcnow().isoformat()}
