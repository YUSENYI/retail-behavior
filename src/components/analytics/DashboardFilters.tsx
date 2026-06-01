export interface DashboardFiltersValue {
  timeRange?: string;
  productId?: string;
  userId?: string;
  channelId?: string;
  segmentId?: string;
  behaviorType?: string;
}

export function DashboardFilters({ value }: { value: DashboardFiltersValue }) {
  const labels = Object.entries(value)
    .filter(([, v]) => Boolean(v))
    .map(([k, v]) => `${k}: ${v}`);
  return <div aria-label="current filters">{labels.length ? labels.join(" | ") : "All data"}</div>;
}
