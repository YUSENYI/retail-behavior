export function FreshnessBadge({ value }: { value?: string }) {
  return <span aria-label="data freshness">Freshness: {value ?? "pending"}</span>;
}

export function LoadingState() {
  return <div role="status">Loading analytics...</div>;
}

export function EmptyState() {
  return <div>No matching data</div>;
}

export function ErrorState({ message }: { message: string }) {
  return <div role="alert">{message}</div>;
}

export function DelayedState() {
  return <div role="status">Data refresh is delayed</div>;
}
