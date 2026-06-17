const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

function authHeaders() {
  const fallback = { actorId: "demo", role: "administrator", dataScope: "all" };
  try {
    const stored = window.localStorage.getItem("retail-auth");
    const auth = stored ? { ...fallback, ...JSON.parse(stored) } : fallback;
    return {
      "x-role": String(auth.role),
      "x-data-scope": String(auth.dataScope),
      "x-actor-id": String(auth.actorId),
    };
  } catch {
    return {
      "x-role": fallback.role,
      "x-data-scope": fallback.dataScope,
      "x-actor-id": fallback.actorId,
    };
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: authHeaders(),
  });
  if (!response.ok) throw new Error(`GET ${path} failed`);
  return response.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`POST ${path} failed`);
  return response.json() as Promise<T>;
}
