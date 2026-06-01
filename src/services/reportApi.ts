import { apiGet, apiPost } from "./apiClient";

export const reportApi = {
  reports: () => apiGet("/reports"),
  exportReport: (reportType: string, filters: Record<string, unknown>) =>
    apiPost(`/reports/${reportType}/exports`, { filters }),
  auditLogs: () => apiGet("/audit-logs"),
};
