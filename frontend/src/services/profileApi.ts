import { apiGet } from "./apiClient";

export const profileApi = {
  profile: (userId: string) => apiGet(`/profiles/${userId}`),
  segments: () => apiGet("/segments"),
  segmentUsers: (segmentId: string) => apiGet(`/segments/${segmentId}/users`),
  purchaseIntent: () => apiGet("/purchase-intent/users"),
};
