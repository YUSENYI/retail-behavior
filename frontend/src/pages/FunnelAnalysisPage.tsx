import { DashboardFilters } from "../components/analytics/DashboardFilters";

export function FunnelAnalysisPage() {
  return (
    <main>
      <h1>Conversion Funnel</h1>
      <DashboardFilters value={{ timeRange: "today" }} />
      <section aria-label="funnel stages">Browse {"->"} Click {"->"} Cart {"->"} Order {"->"} Payment</section>
    </main>
  );
}
