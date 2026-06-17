import { DashboardFilters } from "../components/analytics/DashboardFilters";
import { FreshnessBadge } from "../components/analytics/States";

export function BehaviorEventsPage() {
  return (
    <main>
      <h1>Behavior Events</h1>
      <DashboardFilters value={{ timeRange: "today" }} />
      <FreshnessBadge />
      <section aria-label="behavior details">Behavior detail table placeholder</section>
    </main>
  );
}
