import { DashboardFilters } from "../components/analytics/DashboardFilters";
import { FreshnessBadge } from "../components/analytics/States";

export function BehaviorSummaryPage() {
  return (
    <main>
      <h1>Behavior Summary</h1>
      <DashboardFilters value={{ timeRange: "today" }} />
      <FreshnessBadge />
      <section aria-label="metric cards">Visits, clicks, carts, orders, payments</section>
    </main>
  );
}
