import { apiGet } from "./apiClient";

export const alertRecommendationApi = {
  alerts: () => apiGet("/alerts"),
  recommendations: () => apiGet("/recommendations/analysis"),
};
