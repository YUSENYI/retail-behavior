export type Role =
  | "administrator"
  | "operations_manager"
  | "analyst"
  | "customer_service_viewer"
  | "read_only_viewer";

export interface AuthState {
  actorId: string;
  role: Role;
  dataScope: string;
}

export const demoAuth: AuthState = {
  actorId: "demo",
  role: "administrator",
  dataScope: "all",
};
