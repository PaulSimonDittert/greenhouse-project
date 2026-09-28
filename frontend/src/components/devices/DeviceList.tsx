import { useEffect, useState } from "react";
import {
  assignDeviceZone,
  fetchDevices,
  fetchLocationConfig,
  fetchLocations,
  provisionDeviceFamily,
  type DeviceDto,
  type LocationDto,
  type ZoneDto,
} from "../../services/api";
import DeviceFamilySwitcher from "./DeviceFamilySwitcher";

interface DeviceListProps {
  configurationRevision: number;
}

type ZoneOption = ZoneDto & { location_name: string };

export default function DeviceList({ configurationRevision }: DeviceListProps) {
  const [devices, setDevices] = useState<DeviceDto[]>([]);
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [zonesByLocation, setZonesByLocation] = useState<Map<string, ZoneOption[]>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [family, setFamily] = useState<string>("simulation");
  const [assigningDeviceId, setAssigningDeviceId] = useState<string | null>(null);

  const loadDevices = async (selectedFamily: string) => {
    try {
      const [deviceRows, savedLocations] = await Promise.all([
        fetchDevices(selectedFamily),
        fetchLocations(),
      ]);
      const configurations = await Promise.all(savedLocations.map(async (location) => ({
        location,
        config: await fetchLocationConfig(location.id),
      })));
      const groupedZones = new Map<string, ZoneOption[]>();
      for (const { location, config } of configurations) {
        groupedZones.set(location.id, config.zones.map((zone) => ({ ...zone, location_name: location.name })));
      }
      setDevices(deviceRows);
      setLocations(savedLocations);
      setZonesByLocation(groupedZones);
      setError(null);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Failed to load devices and location zones");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let active = true;
    Promise.resolve().then(async () => {
      const [deviceRows, savedLocations] = await Promise.all([
        fetchDevices(family),
        fetchLocations(),
      ]);
      const configurations = await Promise.all(savedLocations.map(async (location) => ({
        location,
        config: await fetchLocationConfig(location.id),
      })));
      const groupedZones = new Map<string, ZoneOption[]>();
      for (const { location, config } of configurations) {
        groupedZones.set(location.id, config.zones.map((zone) => ({ ...zone, location_name: location.name })));
      }
      return { deviceRows, savedLocations, groupedZones };
    }).then(({ deviceRows, savedLocations, groupedZones }) => {
      if (!active) return;
      setDevices(deviceRows);
      setLocations(savedLocations);
      setZonesByLocation(groupedZones);
      setError(null);
    }).catch((loadError: unknown) => {
      if (active) setError(loadError instanceof Error ? loadError.message : "Failed to load devices and location zones");
    }).finally(() => {
      if (active) setLoading(false);
    });
    return () => { active = false; };
  }, [family, configurationRevision]);

  const handleZoneChange = async (device: DeviceDto, zoneId: string) => {
    const nextZoneId = zoneId || null;
    setAssigningDeviceId(device.id);
    setError(null);
    try {
      await assignDeviceZone(device.id, nextZoneId);
      setDevices((current) => current.map((item) => item.id === device.id
        ? {
            ...item,
            zone_id: nextZoneId,
            location_id: nextZoneId
              ? locations.find((location) => zonesByLocation.get(location.id)?.some((zone) => zone.id === nextZoneId))?.id ?? null
              : null,
          }
        : item,
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update device zone");
    } finally {
      setAssigningDeviceId(null);
    }
  };

  const handleProvision = async () => {
    setLoading(true);
    setError(null);
    try {
      await provisionDeviceFamily(family);
      await loadDevices(family);
    } catch (provisionError) {
      setError(provisionError instanceof Error ? provisionError.message : "Failed to provision family");
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5" id="devices">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-medium text-gray-300">Device Kits</h3>
        <button 
          onClick={handleProvision}
          className="bg-emerald-600 hover:bg-emerald-500 text-xs px-3 py-1.5 rounded transition text-white"
        >
          Provision Kit
        </button>
      </div>

      <DeviceFamilySwitcher selected={family} onSelect={setFamily} />

      {error && <div role="alert" className="mb-3 text-sm text-red-400">{error}</div>}

      {loading ? (
        <div className="text-gray-400 text-sm">Loading {family} devices...</div>
      ) : error ? (
        <div className="text-red-400 text-sm">{error}</div>
      ) : devices.length === 0 ? (
        <p className="text-sm text-gray-500">No {family} devices provisioned yet.</p>
      ) : (
        <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
          {devices.map((d) => (
            <div key={d.id} className="bg-gray-800 border border-gray-700 p-3 rounded-lg flex flex-col">
              <div className="flex justify-between items-start mb-1">
                <span className="font-medium text-gray-200">{d.display_name}</span>
                <div className="flex gap-1">
                  <span className={`text-[10px] px-1.5 py-0.5 rounded uppercase font-bold tracking-wider ${d.role === "actuator" ? "bg-amber-900/50 text-amber-400" : "bg-purple-900/50 text-purple-400"}`}>
                    {d.role}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-700 text-gray-300 uppercase font-bold tracking-wider">
                    {d.device_family}
                  </span>
                </div>
              </div>
              <span className="text-xs text-gray-400">Type: {d.device_type}</span>
              <span className="text-xs text-gray-500 mt-1 font-mono truncate" title={JSON.stringify(d.default_config)}>
                {JSON.stringify(d.default_config)}
              </span>
              <label className="mt-3 text-xs text-gray-400">
                Assigned zone
                <select
                  value={d.zone_id ?? ""}
                  onChange={(event) => void handleZoneChange(d, event.target.value)}
                  disabled={assigningDeviceId === d.id}
                  className="mt-1 w-full rounded border border-gray-700 bg-gray-900 px-2.5 py-2 text-sm text-gray-200 disabled:opacity-50"
                  aria-label={`Zone assignment for ${d.display_name || d.device_type}`}
                >
                  <option value="">Unassigned</option>
                  {locations.map((location) => {
                    const locationZones = zonesByLocation.get(location.id) ?? [];
                    if (locationZones.length === 0) return null;
                    return (
                      <optgroup key={location.id} label={location.name}>
                        {locationZones.map((zone) => (
                          <option key={zone.id} value={zone.id}>{location.name} — {zone.name}</option>
                        ))}
                      </optgroup>
                    );
                  })}
                </select>
                <span className="mt-1 block text-[11px] text-gray-500">
                  {d.zone_id
                    ? (() => {
                        const assignedZone = locations.flatMap((location) => zonesByLocation.get(location.id) ?? []).find((zone) => zone.id === d.zone_id);
                        return assignedZone ? `${assignedZone.location_name} — ${assignedZone.name}` : "Unassigned";
                      })()
                    : "Unassigned"}
                </span>
              </label>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}