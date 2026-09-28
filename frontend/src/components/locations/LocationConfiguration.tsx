import { useEffect, useState } from "react";
import {
  addZone,
  createLocationConfig,
  deleteLocation,
  deleteZone,
  fetchLocationConfig,
  fetchLocations,
  fetchZoneDevices,
  updateZone,
  type LocationConfigDto,
  type LocationDto,
  type ZoneDto,
  type ZoneInput,
} from "../../services/api";

type ZoneForm = {
  name: string;
  low: string;
  high: string;
  schedule: string;
};

type DisplayZone = ZoneDto & { device_names: string[] };

const emptyZone = (): ZoneForm => ({ name: "", low: "0.3", high: "0.7", schedule: "" });

function toZoneInput(form: ZoneForm): ZoneInput {
  const scheduleText = form.schedule.trim();
  let schedule: Record<string, unknown> | null = null;
  if (scheduleText) {
    const parsed: unknown = JSON.parse(scheduleText);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      throw new Error("Schedule must be a JSON object or left empty.");
    }
    schedule = parsed as Record<string, unknown>;
  }

  if (!form.low.trim() || !form.high.trim()) {
    throw new Error("Both moisture thresholds are required.");
  }
  const low = Number(form.low);
  const high = Number(form.high);
  if (!form.name.trim()) throw new Error("Zone name is required.");
  if (!Number.isFinite(low) || !Number.isFinite(high) || low < 0 || high > 1 || low >= high) {
    throw new Error("Thresholds must be between 0 and 1, with the low value below the high value.");
  }

  return {
    name: form.name.trim(),
    moisture_threshold_low: low,
    moisture_threshold_high: high,
    schedule,
  };
}

function asErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "The request failed. Please try again.";
}

function toForm(zone: ZoneDto): ZoneForm {
  return {
    name: zone.name,
    low: String(zone.moisture_threshold_low),
    high: String(zone.moisture_threshold_high),
    schedule: zone.schedule ? JSON.stringify(zone.schedule, null, 2) : "",
  };
}

export default function LocationConfiguration({ onLocationsChanged }: { onLocationsChanged: () => void }) {
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [config, setConfig] = useState<(Omit<LocationConfigDto, "zones"> & { zones: DisplayZone[] }) | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [locationName, setLocationName] = useState("");
  const [newLocationZones, setNewLocationZones] = useState<ZoneForm[]>([emptyZone()]);
  const [newLocationValidation, setNewLocationValidation] = useState<string | null>(null);
  const [newZone, setNewZone] = useState<ZoneForm>(emptyZone());
  const [newZoneValidation, setNewZoneValidation] = useState<string | null>(null);
  const [editingZoneId, setEditingZoneId] = useState<string | null>(null);
  const [editingZone, setEditingZone] = useState<ZoneForm>(emptyZone());
  const [editValidation, setEditValidation] = useState<string | null>(null);

  const loadConfig = async (locationId: string) => {
    setSelectedId(locationId);
    setConfig(null);
    setError(null);
    try {
      const loaded = await fetchLocationConfig(locationId);
      const zones = await Promise.all(loaded.zones.map(async (zone) => {
        const devices = await fetchZoneDevices(locationId, zone.id);
        return { ...zone, device_names: devices.map((device) => device.display_name || device.device_type) };
      }));
      setConfig({ ...loaded, zones });
    } catch (loadError) {
      setConfig(null);
      setError(asErrorMessage(loadError));
    }
  };

  useEffect(() => {
    const loadSavedLocations = async () => {
      setLoading(true);
      try {
        setLocations(await fetchLocations());
      } catch (loadError) {
        setError(asErrorMessage(loadError));
      } finally {
        setLoading(false);
      }
    };
    void loadSavedLocations();
  }, []);

  const submitNewLocation = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setNewLocationValidation(null);
    setError(null);
    setSuccess(null);
    if (!locationName.trim()) {
      setNewLocationValidation("Location name is required.");
      return;
    }

    let zoneInputs: ZoneInput[];
    try {
      if (newLocationZones.length === 0) throw new Error("Add at least one zone.");
      zoneInputs = newLocationZones.map(toZoneInput);
      const normalizedNames = zoneInputs.map((zone) => zone.name.toLocaleLowerCase());
      if (new Set(normalizedNames).size !== normalizedNames.length) {
        throw new Error("Zone names must be unique within a location.");
      }
    } catch (validationError) {
      setNewLocationValidation(asErrorMessage(validationError));
      return;
    }

    setBusy(true);
    try {
      const created = await createLocationConfig(locationName.trim(), zoneInputs);
      setLocations((current) => [...current, created.location]);
      setLocationName("");
      setNewLocationZones([emptyZone()]);
      await loadConfig(created.location.id);
      setSuccess(`Location "${created.location.name}" created.`);
      onLocationsChanged();
    } catch (requestError) {
      setError(asErrorMessage(requestError));
    } finally {
      setBusy(false);
    }
  };

  const handleDeleteLocation = async (location: LocationDto) => {
    if (!window.confirm(`Delete location "${location.name}" and all of its zones?`)) return;
    setError(null);
    setSuccess(null);
    setBusy(true);
    try {
      await deleteLocation(location.id);
      setLocations((current) => current.filter((item) => item.id !== location.id));
      if (selectedId === location.id) {
        setSelectedId("");
        setConfig(null);
        setEditingZoneId(null);
      }
      setSuccess(`Location "${location.name}" deleted.`);
      onLocationsChanged();
    } catch (requestError) {
      setError(asErrorMessage(requestError));
    } finally {
      setBusy(false);
    }
  };

  const submitNewZone = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setNewZoneValidation(null);
    setError(null);
    setSuccess(null);
    if (!selectedId) return;
    let zone: ZoneInput;
    try {
      zone = toZoneInput(newZone);
    } catch (validationError) {
      setNewZoneValidation(asErrorMessage(validationError));
      return;
    }

    setBusy(true);
    try {
      await addZone(selectedId, zone);
      setNewZone(emptyZone());
      await loadConfig(selectedId);
      setSuccess("Zone added.");
      onLocationsChanged();
    } catch (requestError) {
      setError(asErrorMessage(requestError));
    } finally {
      setBusy(false);
    }
  };

  const submitZoneEdit = async (zoneId: string) => {
    setEditValidation(null);
    setError(null);
    setSuccess(null);
    if (!selectedId) return;
    let zone: ZoneInput;
    try {
      zone = toZoneInput(editingZone);
    } catch (validationError) {
      setEditValidation(asErrorMessage(validationError));
      return;
    }

    setBusy(true);
    try {
      await updateZone(selectedId, zoneId, zone);
      setEditingZoneId(null);
      await loadConfig(selectedId);
      setSuccess("Zone updated.");
      onLocationsChanged();
    } catch (requestError) {
      setError(asErrorMessage(requestError));
    } finally {
      setBusy(false);
    }
  };

  const handleDeleteZone = async (zone: DisplayZone) => {
    if (!selectedId) return;
    setError(null);
    setSuccess(null);
    setBusy(true);
    try {
      await deleteZone(selectedId, zone.id);
      await loadConfig(selectedId);
      setSuccess(`Zone "${zone.name}" deleted.`);
      onLocationsChanged();
    } catch (requestError) {
      setError(asErrorMessage(requestError));
    } finally {
      setBusy(false);
    }
  };

  const updateZoneForm = (index: number, field: keyof ZoneForm, value: string) => {
    setNewLocationZones((current) => current.map((zone, zoneIndex) =>
      zoneIndex === index ? { ...zone, [field]: value } : zone,
    ));
  };

  const zoneFields = (form: ZoneForm, onChange: (field: keyof ZoneForm, value: string) => void, idPrefix: string) => (
    <div className="grid gap-3 sm:grid-cols-2">
      <label className="text-xs text-gray-400">
        Zone name
        <input className="mt-1 w-full rounded border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-100" value={form.name} onChange={(event) => onChange("name", event.target.value)} />
      </label>
      <div className="grid grid-cols-2 gap-3">
        <label className="text-xs text-gray-400" htmlFor={`${idPrefix}-low`}>
          Low threshold
          <input id={`${idPrefix}-low`} type="number" min="0" max="1" step="0.01" className="mt-1 w-full rounded border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-100" value={form.low} onChange={(event) => onChange("low", event.target.value)} />
        </label>
        <label className="text-xs text-gray-400" htmlFor={`${idPrefix}-high`}>
          High threshold
          <input id={`${idPrefix}-high`} type="number" min="0" max="1" step="0.01" className="mt-1 w-full rounded border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-100" value={form.high} onChange={(event) => onChange("high", event.target.value)} />
        </label>
      </div>
      <label className="text-xs text-gray-400 sm:col-span-2">
        Schedule (JSON)
        <textarea rows={2} className="mt-1 w-full rounded border border-gray-700 bg-gray-950 px-3 py-2 font-mono text-xs text-gray-100" placeholder='{"days": ["Mon", "Wed"]}' value={form.schedule} onChange={(event) => onChange("schedule", event.target.value)} />
      </label>
    </div>
  );

  return (
    <section id="configuration" className="space-y-5 rounded-xl border border-gray-800 bg-gray-900 p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-gray-100">Configuration</h2>
          <p className="mt-1 text-sm text-gray-400">Locations, zones, moisture thresholds, and schedules</p>
        </div>
        {config && <p className="font-mono text-xs text-gray-500">Location ID: {config.location.id}</p>}
      </div>

      {error && <div role="alert" className="rounded border border-red-800 bg-red-950/50 px-3 py-2 text-sm text-red-300">{error}</div>}
      {success && <div role="status" className="rounded border border-emerald-800 bg-emerald-950/40 px-3 py-2 text-sm text-emerald-300">{success}</div>}

      <div className="grid gap-5 lg:grid-cols-[minmax(14rem,0.8fr)_minmax(0,1.6fr)]">
        <div className="space-y-4">
          <div>
            <h3 className="mb-2 text-sm font-medium text-gray-300">Saved locations</h3>
            {loading ? <p className="text-sm text-gray-500">Loading locations...</p> : locations.length === 0 ? (
              <p className="rounded border border-dashed border-gray-700 px-3 py-4 text-sm text-gray-500">No saved locations.</p>
            ) : (
              <ul className="divide-y divide-gray-800 rounded border border-gray-800">
                {locations.map((location) => (
                  <li key={location.id} className={`flex items-center gap-2 p-2 ${selectedId === location.id ? "bg-gray-800/80" : ""}`}>
                    <button type="button" onClick={() => void loadConfig(location.id)} className="min-w-0 flex-1 truncate px-2 py-1 text-left text-sm text-gray-200 hover:text-emerald-300" aria-pressed={selectedId === location.id}>
                      {location.name}
                    </button>
                    <button type="button" onClick={() => void handleDeleteLocation(location)} disabled={busy} className="rounded border border-gray-700 px-2 py-1 text-xs text-gray-400 hover:border-red-700 hover:text-red-300 disabled:opacity-50" aria-label={`Delete ${location.name}`}>
                      Delete
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <form onSubmit={submitNewLocation} className="space-y-3 border-t border-gray-800 pt-4">
            <h3 className="text-sm font-medium text-gray-300">Create location</h3>
            <label className="block text-xs text-gray-400">
              Location name
              <input value={locationName} onChange={(event) => setLocationName(event.target.value)} className="mt-1 w-full rounded border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-100" />
            </label>
            {newLocationZones.map((zone, index) => (
              <fieldset key={index} className="space-y-3 rounded border border-gray-800 p-3">
                <div className="flex items-center justify-between">
                  <legend className="text-xs font-medium text-gray-400">Zone {index + 1}</legend>
                  {newLocationZones.length > 1 && <button type="button" onClick={() => setNewLocationZones((current) => current.filter((_, zoneIndex) => zoneIndex !== index))} className="text-xs text-gray-500 hover:text-red-300">Remove</button>}
                </div>
                {zoneFields(zone, (field, value) => updateZoneForm(index, field, value), `new-location-${index}`)}
              </fieldset>
            ))}
            {newLocationValidation && <p role="alert" className="text-xs text-red-300">{newLocationValidation}</p>}
            <div className="flex flex-wrap gap-2">
              <button type="button" onClick={() => setNewLocationZones((current) => [...current, emptyZone()])} className="rounded border border-gray-700 px-3 py-2 text-xs text-gray-300 hover:bg-gray-800">Add another zone</button>
              <button type="submit" disabled={busy} className="rounded bg-emerald-600 px-3 py-2 text-xs font-medium text-white hover:bg-emerald-500 disabled:opacity-50">Create location</button>
            </div>
          </form>
        </div>

        <div className="min-w-0">
          {!selectedId ? (
            <div className="flex min-h-40 items-center justify-center rounded border border-dashed border-gray-700 p-6 text-center text-sm text-gray-500">Select a saved location to manage its zones.</div>
          ) : !config ? (
            <div className="p-4 text-sm text-gray-400">Loading location configuration...</div>
          ) : (
            <div className="space-y-4">
              <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-gray-800 pb-3">
                <h3 className="text-base font-semibold text-gray-100">{config.location.name}</h3>
                <span className="text-xs text-gray-500">{config.zones.length} {config.zones.length === 1 ? "zone" : "zones"}</span>
              </div>

              <div className="space-y-3">
                {config.zones.map((zone) => (
                  <article key={zone.id} className="rounded-lg border border-gray-800 bg-gray-950/50 p-4">
                    {editingZoneId === zone.id ? (
                      <div className="space-y-3">
                        {zoneFields(editingZone, (field, value) => setEditingZone((current) => ({ ...current, [field]: value })), `edit-${zone.id}`)}
                        {editValidation && <p role="alert" className="text-xs text-red-300">{editValidation}</p>}
                        <div className="flex gap-2">
                          <button type="button" onClick={() => void submitZoneEdit(zone.id)} disabled={busy} className="rounded bg-emerald-600 px-3 py-1.5 text-xs text-white hover:bg-emerald-500 disabled:opacity-50">Save changes</button>
                          <button type="button" onClick={() => setEditingZoneId(null)} className="rounded border border-gray-700 px-3 py-1.5 text-xs text-gray-300 hover:bg-gray-800">Cancel</button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <h4 className="font-medium text-gray-100">{zone.name}</h4>
                            <p className="mt-1 text-xs text-gray-400">Moisture {zone.moisture_threshold_low}–{zone.moisture_threshold_high} VWC</p>
                            <p className="mt-1 text-xs text-gray-500">Schedule: {zone.schedule ? JSON.stringify(zone.schedule) : "None"}</p>
                          </div>
                          <div className="flex gap-2">
                            <button type="button" onClick={() => { setEditingZone(toForm(zone)); setEditingZoneId(zone.id); setEditValidation(null); }} className="rounded border border-gray-700 px-2.5 py-1.5 text-xs text-gray-300 hover:bg-gray-800">Edit</button>
                            <button type="button" onClick={() => void handleDeleteZone(zone)} disabled={busy} className="rounded border border-gray-700 px-2.5 py-1.5 text-xs text-gray-400 hover:border-red-700 hover:text-red-300 disabled:opacity-50">Delete</button>
                          </div>
                        </div>
                        <div className="mt-3 border-t border-gray-800 pt-3">
                          <p className="text-[11px] font-medium uppercase text-gray-500">Devices</p>
                          {zone.device_names.length ? <ul className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-sm text-gray-300">{zone.device_names.map((name, index) => <li key={`${zone.id}-${index}`}>{name}</li>)}</ul> : <p className="mt-1 text-xs text-gray-600">No devices assigned.</p>}
                        </div>
                      </>
                    )}
                  </article>
                ))}
              </div>

              <form onSubmit={submitNewZone} className="space-y-3 border-t border-gray-800 pt-4">
                <h4 className="text-sm font-medium text-gray-300">Add zone</h4>
                {zoneFields(newZone, (field, value) => setNewZone((current) => ({ ...current, [field]: value })), "add-zone")}
                {newZoneValidation && <p role="alert" className="text-xs text-red-300">{newZoneValidation}</p>}
                <button type="submit" disabled={busy} className="rounded bg-emerald-600 px-3 py-2 text-xs font-medium text-white hover:bg-emerald-500 disabled:opacity-50">Add zone</button>
              </form>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}