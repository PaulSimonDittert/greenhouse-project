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
  } catch {
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

export interface DeviceDto {
  id: string;
  device_type: string;
  role: "sensor" | "actuator";
  device_family: string;
  display_name: string;
  default_config: Record<string, unknown>;
  zone_id: string | null;
  location_id: string | null;
}

export interface LocationDto {
  id: string;
  name: string;
}

export interface ZoneDto {
  id: string;
  location_id: string;
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  schedule: Record<string, unknown> | null;
}

export interface LocationConfigDto {
  location: LocationDto;
  zones: ZoneDto[];
}

export interface ZoneInput {
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  schedule: Record<string, unknown> | null;
}

async function apiError(response: Response, fallback: string): Promise<Error> {
  try {
    const body = await response.json();
    const detail = body.detail;
    if (typeof detail === "string") return new Error(detail);
    if (Array.isArray(detail)) {
      return new Error(detail.map((item: { msg?: string }) => item.msg ?? "Invalid request").join("; "));
    }
  } catch {
    // Keep the endpoint-specific fallback when the response has no JSON body.
  }
  return new Error(fallback);
}

export async function fetchLocations(): Promise<LocationDto[]> {
  const response = await fetch(`${API_BASE_URL}/api/locations`);
  if (!response.ok) throw await apiError(response, "Failed to load locations");
  return response.json();
}

export async function fetchLocationConfig(locationId: string): Promise<LocationConfigDto> {
  const response = await fetch(`${API_BASE_URL}/api/locations/${locationId}/config`);
  if (!response.ok) throw await apiError(response, "Failed to load location configuration");
  return response.json();
}

export async function createLocationConfig(
  locationName: string,
  zones: ZoneInput[],
): Promise<LocationConfigDto> {
  const response = await fetch(`${API_BASE_URL}/api/locations/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ location_name: locationName, zones }),
  });
  if (!response.ok) throw await apiError(response, "Failed to create location");
  return response.json();
}

export async function deleteLocation(locationId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/locations/${locationId}`, { method: "DELETE" });
  if (!response.ok) throw await apiError(response, "Failed to delete location");
}

export async function addZone(locationId: string, zone: ZoneInput): Promise<ZoneDto> {
  const response = await fetch(`${API_BASE_URL}/api/locations/${locationId}/zones`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(zone),
  });
  if (!response.ok) throw await apiError(response, "Failed to add zone");
  return response.json();
}

export async function updateZone(locationId: string, zoneId: string, zone: ZoneInput): Promise<ZoneDto> {
  const response = await fetch(`${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(zone),
  });
  if (!response.ok) throw await apiError(response, "Failed to update zone");
  return response.json();
}

export async function deleteZone(locationId: string, zoneId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}`, { method: "DELETE" });
  if (!response.ok) throw await apiError(response, "Failed to delete zone");
}

export async function fetchZoneDevices(locationId: string, zoneId: string): Promise<DeviceDto[]> {
  const response = await fetch(`${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}/devices`);
  if (!response.ok) throw await apiError(response, "Failed to load zone devices");
  return response.json();
}

export async function assignDeviceZone(deviceId: string, zoneId: string | null): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/zone`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ zone_id: zoneId }),
  });
  if (!response.ok) throw await apiError(response, "Failed to update device zone");
}

export async function fetchDevices(family?: string, role?: string): Promise<DeviceDto[]> {
  const params = new URLSearchParams();
  if (family) params.append("family", family);
  if (role) params.append("role", role);
  
  const queryString = params.toString();
  const url = `${API_BASE_URL}/api/devices${queryString ? `?${queryString}` : ""}`;
  
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch devices");
  return res.json();
}

export async function provisionDeviceFamily(family: string): Promise<DeviceDto[]> {
  const res = await fetch(`${API_BASE_URL}/api/devices/provision?family=${family}`, {
    method: "POST"
  });
  if (!res.ok) throw new Error("Failed to provision devices");
  return res.json();
}