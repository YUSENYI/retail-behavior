import { apiGet } from "./apiClient";

export const analyticsApi = {
  summary: () => apiGet("/analytics/behavior-summary"),
  funnel: () => apiGet("/analytics/funnel"),
  productHeat: (rankBy = "browse") => apiGet(`/analytics/product-heat?rankBy=${rankBy}`),
};
