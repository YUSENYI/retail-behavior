import { apiGet, apiPost } from "./apiClient";

export interface BehaviorEventInput {
  eventId: string;
  sourceSystem: string;
  eventType: string;
  sessionId: string;
  channelId: string;
  occurredAt: string;
  userId?: string;
  visitorId?: string;
  productId?: string;
  orderId?: string;
  paymentId?: string;
  searchKeyword?: string;
  metadata?: Record<string, unknown>;
}

export const behaviorApi = {
  ingest: (events: BehaviorEventInput[]) => apiPost("/events/behavior", { events }),
  list: () => apiGet("/behavior/events"),
  journey: (subjectId: string) => apiGet(`/behavior/journeys/${subjectId}`),
};
