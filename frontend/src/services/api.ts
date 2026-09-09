const API_BASE_URL = "http://localhost:8000";

export interface HealthResponse {
  status: string;
  db: "ok" | "fail";
}

export async function fetchHealth(): Promise<HealthResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) {
      return { status: "degraded", db: "fail" };
    }
    return await res.json();
  } catch (error) {
    return { status: "degraded", db: "fail" };
  }
}

export interface SensorDto {
  id: string;
  device_type: string;
  display_name: string;
  default_config: Record<string, unknown>;
}

export async function fetchSensors(): Promise<SensorDto[]> {
  const res = await fetch(`${API_BASE_URL}/api/sensors`);
  if (!res.ok) throw new Error("Failed to fetch sensors");
  return res.json();
}

export async function createSensor(type: string, displayName?: string): Promise<SensorDto> {
  const res = await fetch(`${API_BASE_URL}/api/sensors`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type, display_name: displayName }),
  });
  if (!res.ok) throw new Error("Failed to create sensor");
  return res.json();
}