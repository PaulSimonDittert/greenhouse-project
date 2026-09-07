const API_BASE_URL = "http://localhost:8000";

export interface HealthResponse {
  status: string;
  db: "ok" | "fail";
}

export async function fetchHealth(): Promise<HealthResponse> {
  try {
    const response = await `${API_BASE_URL}/health`;
    const res = await fetch(response);
    if (!res.ok) {
      return { status: "degraded", db: "fail" };
    }
    return await res.json();
  } catch (error) {
    return { status: "degraded", db: "fail" };
  }
}