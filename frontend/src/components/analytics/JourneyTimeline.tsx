export interface JourneyEvent {
  eventId: string;
  eventType: string;
  occurredAt: string;
  idempotencyState?: string;
}

export function JourneyTimeline({ events }: { events: JourneyEvent[] }) {
  return (
    <ol aria-label="journey timeline">
      {events.map((event) => (
        <li key={event.eventId}>
          {event.occurredAt} - {event.eventType} - {event.idempotencyState ?? "accepted"}
        </li>
      ))}
    </ol>
  );
}
