import { useEffect, useState } from "react";
import {
  createSensor,
  fetchSensorReadings,
  fetchSensors,
  readSensor,
  updateSamplingSettings,
  type ReadingDto,
  type SensorDto,
} from "../../services/api";

export default function SensorList() {
  const [sensors, setSensors] = useState<SensorDto[]>([]);
  const [latestReadings, setLatestReadings] = useState<Record<string, ReadingDto | null>>({});
  const [intervalDrafts, setIntervalDrafts] = useState<Record<string, string>>({});
  const [cardErrors, setCardErrors] = useState<Record<string, string>>({});
  const [cardNotices, setCardNotices] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [readingDeviceId, setReadingDeviceId] = useState<string | null>(null);
  const [settingsDeviceId, setSettingsDeviceId] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const applySensors = (data: SensorDto[]) => {
    setSensors(data);
    setIntervalDrafts((current) => Object.fromEntries(data.map((sensor) => [
      sensor.id,
      current[sensor.id] ?? String(sensor.sampling_interval_seconds),
    ])));
  };

  const loadSensors = async () => {
    try {
      const data = await fetchSensors();
      applySensors(data);
      setError(null);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Failed to load sensors");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let active = true;
    Promise.resolve().then(fetchSensors).then((data) => {
      if (active) applySensors(data);
    }).catch((loadError: unknown) => {
      if (active) setError(loadError instanceof Error ? loadError.message : "Failed to load sensors");
    }).finally(() => {
      if (active) setLoading(false);
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    let active = true;
    const pollLatestReadings = async () => {
      const results = await Promise.all(sensors.map(async (sensor) => {
        try {
          const readings = await fetchSensorReadings(sensor.id, 1);
          return [sensor.id, readings[0] ?? null] as const;
        } catch {
          return [sensor.id, null] as const;
        }
      }));
      if (active) setLatestReadings(Object.fromEntries(results));
    };

    // Temporary polling; Phase 12 replaces this with WebSocket updates.
    void pollLatestReadings();
    const timer = window.setInterval(() => void pollLatestReadings(), 5000);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [sensors]);

  const handleAdd = async (type: string) => {
    setError(null);
    setNotice(null);
    try {
      await createSensor(type);
      await loadSensors(); // Reload the list
      setNotice("Sensor added.");
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Failed to add sensor");
    }
  };

  const setCardMessage = (sensorId: string, message: string) => {
    setCardNotices((current) => ({ ...current, [sensorId]: message }));
  };

  const setCardError = (sensorId: string, message: string) => {
    setCardErrors((current) => ({ ...current, [sensorId]: message }));
    setCardNotices((current) => ({ ...current, [sensorId]: "" }));
  };

  const handleReadNow = async (sensor: SensorDto) => {
    setReadingDeviceId(sensor.id);
    setCardErrors((current) => ({ ...current, [sensor.id]: "" }));
    setCardNotices((current) => ({ ...current, [sensor.id]: "" }));
    try {
      const reading = await readSensor(sensor.id);
      setLatestReadings((current) => ({ ...current, [sensor.id]: reading }));
      setCardMessage(sensor.id, "Reading saved.");
    } catch (readError) {
      setCardError(sensor.id, readError instanceof Error ? readError.message : "Failed to read sensor");
    } finally {
      setReadingDeviceId(null);
    }
  };

  const handleSamplingUpdate = async (
    sensor: SensorDto,
    samplingIntervalSeconds: number,
    trackingEnabled: boolean,
  ) => {
    if (!Number.isInteger(samplingIntervalSeconds) || samplingIntervalSeconds < 5) {
      setCardError(sensor.id, "Sampling interval must be a whole number of at least 5 seconds.");
      return;
    }

    setSettingsDeviceId(sensor.id);
    setCardErrors((current) => ({ ...current, [sensor.id]: "" }));
    setCardNotices((current) => ({ ...current, [sensor.id]: "" }));
    try {
      const updated = await updateSamplingSettings(sensor.id, {
        sampling_interval_seconds: samplingIntervalSeconds,
        tracking_enabled: trackingEnabled,
      });
      setSensors((current) => current.map((item) => item.id === sensor.id ? { ...item, ...updated } : item));
      setIntervalDrafts((current) => ({ ...current, [sensor.id]: String(updated.sampling_interval_seconds) }));
      setCardMessage(sensor.id, "Sampling settings saved.");
    } catch (settingsError) {
      setCardError(sensor.id, settingsError instanceof Error ? settingsError.message : "Failed to update sampling settings");
    } finally {
      setSettingsDeviceId(null);
    }
  };

  if (loading) return <div className="text-gray-400">Loading sensors...</div>;
  if (error) return <div className="text-red-400">{error}</div>;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5" id="sensors">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-medium text-gray-300">Sensors</h3>
        <div className="space-x-2">
          <button onClick={() => handleAdd("moisture")} className="bg-emerald-600 hover:bg-emerald-500 text-xs px-3 py-1.5 rounded transition">
            + Moisture
          </button>
          <button onClick={() => handleAdd("light")} className="bg-emerald-600 hover:bg-emerald-500 text-xs px-3 py-1.5 rounded transition">
            + Light
          </button>
        </div>
      </div>

      {error && <p role="alert" className="mb-3 text-sm text-red-400">{error}</p>}
      {notice && <p role="status" className="mb-3 text-sm text-emerald-400">{notice}</p>}
      
      {sensors.length === 0 ? (
        <p className="text-sm text-gray-500">No sensors added yet.</p>
      ) : (
        <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
          {sensors.map((sensor) => (
            <div key={sensor.id} className="bg-gray-800 border border-gray-700 p-3 rounded-lg">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <span className="font-medium text-gray-200">{sensor.display_name || sensor.device_type}</span>
                  <span className="block text-xs text-gray-400 mt-1">Type: {sensor.device_type}</span>
                  <span className="mt-1 block max-w-full truncate font-mono text-xs text-gray-500" title={JSON.stringify(sensor.default_config)}>
                    {JSON.stringify(sensor.default_config)}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => void handleReadNow(sensor)}
                  disabled={readingDeviceId === sensor.id}
                  className="rounded bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-emerald-500 disabled:opacity-50"
                >
                  {readingDeviceId === sensor.id ? "Reading..." : "Read now"}
                </button>
              </div>

              <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-gray-700 pt-3">
                {latestReadings[sensor.id] ? (
                  <>
                    <span className="text-lg font-semibold text-gray-100">
                      {latestReadings[sensor.id]!.value.toFixed(2)} {latestReadings[sensor.id]!.unit}
                    </span>
                    <span className="rounded bg-gray-700 px-2 py-1 text-[10px] uppercase tracking-wide text-gray-300">
                      {latestReadings[sensor.id]!.source}
                    </span>
                    <time className="text-xs text-gray-500" dateTime={latestReadings[sensor.id]!.recorded_at}>
                      {new Date(latestReadings[sensor.id]!.recorded_at).toLocaleString()}
                    </time>
                  </>
                ) : <span className="text-sm text-gray-500">No readings recorded.</span>}
              </div>

              <div className="mt-3 flex flex-wrap items-end gap-3 border-t border-gray-700 pt-3">
                <label className="text-xs text-gray-400">
                  Sampling interval (seconds)
                  <input
                    type="number"
                    min="5"
                    step="1"
                    value={intervalDrafts[sensor.id] ?? String(sensor.sampling_interval_seconds)}
                    onChange={(event) => setIntervalDrafts((current) => ({ ...current, [sensor.id]: event.target.value }))}
                    className="mt-1 block w-36 rounded border border-gray-600 bg-gray-900 px-2.5 py-2 text-sm text-gray-100"
                    aria-label={`Sampling interval for ${sensor.display_name || sensor.device_type}`}
                  />
                </label>
                <button
                  type="button"
                  onClick={() => void handleSamplingUpdate(
                    sensor,
                    Number(intervalDrafts[sensor.id] ?? sensor.sampling_interval_seconds),
                    sensor.tracking_enabled,
                  )}
                  disabled={settingsDeviceId === sensor.id}
                  className="rounded border border-gray-600 px-3 py-2 text-xs text-gray-300 hover:bg-gray-700 disabled:opacity-50"
                >
                  Save interval
                </button>
                <label className="ml-auto flex items-center gap-2 text-sm text-gray-300">
                  <input
                    type="checkbox"
                    checked={sensor.tracking_enabled}
                    disabled={settingsDeviceId === sensor.id}
                    onChange={(event) => void handleSamplingUpdate(sensor, sensor.sampling_interval_seconds, event.target.checked)}
                    className="h-4 w-4 accent-emerald-500"
                  />
                  Tracking
                </label>
              </div>
              {cardErrors[sensor.id] && <p role="alert" className="mt-2 text-xs text-red-300">{cardErrors[sensor.id]}</p>}
              {cardNotices[sensor.id] && <p role="status" className="mt-2 text-xs text-emerald-300">{cardNotices[sensor.id]}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}