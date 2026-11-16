import { useEffect, useMemo, useState } from "react";

import { fetchAlerts, fetchLocationConfig, fetchLocations, type AlertDto, type LocationDto } from "../../services/api";

function severityClass(severity: AlertDto["severity"]): string {
  const map = {
    info: "bg-sky-500/10 text-sky-200 ring-sky-400/30",
    warning: "bg-amber-500/10 text-amber-200 ring-amber-400/30",
    critical: "bg-rose-500/10 text-rose-200 ring-rose-400/30",
  } as const;

  return map[severity] ?? "bg-slate-500/10 text-slate-200 ring-slate-400/30";
}

export default function EventFeed() {
  const [alerts, setAlerts] = useState<AlertDto[]>([]);
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<string>("");
  const [selectedZone, setSelectedZone] = useState<string>("");
  const [zoneOptions, setZoneOptions] = useState<Array<{ id: string; name: string }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void (async () => {
      try {
        const data = await fetchLocations();
        setLocations(data);
        if (data.length > 0) {
          setSelectedLocation((current) => current || data[0].id);
        }
      } catch {
        setLocations([]);
      }
    })();
  }, []);

  useEffect(() => {
    if (!selectedLocation) {
      setZoneOptions([]);
      setSelectedZone("");
      return;
    }

    void (async () => {
      try {
        const config = await fetchLocationConfig(selectedLocation);
        const nextZones = config.zones.map((zone) => ({ id: zone.id, name: zone.name }));
        setZoneOptions(nextZones);
        setSelectedZone((current) => (nextZones.some((zone) => zone.id === current) ? current : ""));
      } catch {
        setZoneOptions([]);
        setSelectedZone("");
      }
    })();
  }, [selectedLocation]);

  useEffect(() => {
    const loadAlerts = async () => {
      try {
        const data = await fetchAlerts({
          status: "active",
          location_id: selectedLocation || undefined,
          zone_id: selectedZone || undefined,
        });
        setAlerts(data);
      } finally {
        setLoading(false);
      }
    };

    void loadAlerts();
    const timer = window.setInterval(() => {
      void loadAlerts();
    }, 5000);

    return () => window.clearInterval(timer);
  }, [selectedLocation, selectedZone]);

  const alertSummary = useMemo(() => {
    if (alerts.length === 0) return "No active alerts";
    return `${alerts.length} active alert${alerts.length === 1 ? "" : "s"}`;
  }, [alerts.length]);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 className="font-medium text-gray-300">Events</h3>
          <p className="text-sm text-gray-500 mt-1">Live feed, refreshed every 5 seconds.</p>
        </div>
        <div className="text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded inline-block">{alertSummary}</div>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <label className="text-sm text-gray-300">
          <span className="mb-1 block">Location</span>
          <select
            value={selectedLocation}
            onChange={(event) => setSelectedLocation(event.target.value)}
            className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-200"
          >
            <option value="">All locations</option>
            {locations.map((location) => (
              <option key={location.id} value={location.id}>{location.name}</option>
            ))}
          </select>
        </label>

        <label className="text-sm text-gray-300">
          <span className="mb-1 block">Zone</span>
          <select
            value={selectedZone}
            onChange={(event) => setSelectedZone(event.target.value)}
            className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-200"
            disabled={zoneOptions.length === 0}
          >
            <option value="">All zones</option>
            {zoneOptions.map((zone) => (
              <option key={zone.id} value={zone.id}>{zone.name}</option>
            ))}
          </select>
        </label>
      </div>

      <div className="mt-4 space-y-3">
        {loading ? (
          <div className="text-sm text-gray-400">Loading alerts…</div>
        ) : alerts.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-700 bg-gray-950/70 px-3 py-6 text-sm text-gray-400 text-center">
            No alerts for the selected filters.
          </div>
        ) : (
          alerts.map((alert) => (
            <div key={alert.id} className="rounded-lg border border-gray-700 bg-gray-950/70 p-3">
              <div className="flex items-center justify-between gap-3">
                <span className={`inline-flex items-center rounded-full px-2 py-1 text-[10px] font-medium ring-1 ${severityClass(alert.severity)}`}>
                  {alert.severity}
                </span>
                <span className="text-[10px] uppercase tracking-wide text-gray-400">{alert.event_type}</span>
              </div>

              <p className="mt-2 text-sm text-gray-100">{alert.message}</p>
              <div className="mt-2 flex items-center justify-between text-[11px] text-gray-400">
                <span>{new Date(alert.created_at).toLocaleString()}</span>
                <span>{alert.status}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
