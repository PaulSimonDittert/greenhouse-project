import { useEffect, useRef, useState } from "react";
import {
  fetchLocations,
  fetchOverview,
  type LocationDto,
  type LocationOverviewDto,
} from "../../services/api";

function asErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "The request failed. Please try again.";
}

export default function OverviewPanel() {
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [selectedLocationId, setSelectedLocationId] = useState("");
  const [overview, setOverview] = useState<LocationOverviewDto | null>(null);
  const [isLoadingLocations, setIsLoadingLocations] = useState(true);
  const [isLoadingOverview, setIsLoadingOverview] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const requestId = useRef(0);

  const loadOverview = async (locationId: string) => {
    const currentRequestId = ++requestId.current;
    setSelectedLocationId(locationId);
    setOverview(null);
    setError(null);
    setIsLoadingOverview(true);
    try {
      const result = await fetchOverview(locationId);
      if (currentRequestId === requestId.current) setOverview(result);
    } catch (loadError) {
      if (currentRequestId === requestId.current) setError(asErrorMessage(loadError));
    } finally {
      if (currentRequestId === requestId.current) setIsLoadingOverview(false);
    }
  };

  useEffect(() => {
    const loadSavedLocations = async () => {
      setIsLoadingLocations(true);
      try {
        const savedLocations = await fetchLocations();
        setLocations(savedLocations);
        if (savedLocations.length > 0) {
          void loadOverview(savedLocations[0].id);
        }
      } catch (loadError) {
        setError(asErrorMessage(loadError));
      } finally {
        setIsLoadingLocations(false);
      }
    };

    void loadSavedLocations();
  }, []);

  return (
    <section id="overview" className="space-y-5 rounded-xl border border-gray-800 bg-gray-900 p-5">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-white">Overview</h2>
          <p className="mt-1 text-sm text-gray-500">Current location status and latest device readings</p>
        </div>
        <div className="flex flex-wrap items-end gap-3">
          <label className="block text-sm text-gray-300">
            Location
            <select
              value={selectedLocationId}
              onChange={(event) => void loadOverview(event.target.value)}
              className="mt-1 min-w-48 rounded border border-gray-700 bg-gray-900 px-2.5 py-2 text-sm text-gray-200 disabled:opacity-50"
              disabled={isLoadingLocations || locations.length === 0}
            >
              {locations.length === 0 ? <option value="">No locations available</option> : null}
              {locations.map((location) => (
                <option key={location.id} value={location.id}>
                  {location.name}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            onClick={() => void loadOverview(selectedLocationId)}
            disabled={!selectedLocationId || isLoadingOverview}
            className="rounded bg-emerald-800 px-3 py-2 text-sm text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoadingOverview ? "Refreshing..." : "Refresh"}
          </button>
        </div>
      </div>

      {error ? <p role="alert" className="text-sm text-red-400">{error}</p> : null}

      {isLoadingOverview && !overview ? (
        <p role="status" className="text-sm text-gray-400">Loading overview...</p>
      ) : null}

      {!isLoadingLocations && locations.length === 0 ? (
        <p className="rounded-lg border border-gray-800 bg-gray-950 p-4 text-sm text-gray-400">
          Create a location to see its overview.
        </p>
      ) : null}

      {overview ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <article className="rounded-lg border border-gray-800 bg-gray-950 p-4">
              <h3 className="text-sm text-gray-400">Assigned sensors</h3>
              <p className="mt-2 text-2xl font-semibold text-white">{overview.device_counts.sensor}</p>
            </article>
            <article className="rounded-lg border border-gray-800 bg-gray-950 p-4">
              <h3 className="text-sm text-gray-400">Assigned actuators</h3>
              <p className="mt-2 text-2xl font-semibold text-white">{overview.device_counts.actuator}</p>
            </article>
            <article className="rounded-lg border border-gray-800 bg-gray-950 p-4">
              <h3 className="text-sm text-gray-400">Strategy</h3>
              <p className="mt-2 text-lg font-medium text-white">
                {overview.strategy_key ?? "No strategy saved"}
              </p>
            </article>
            <article className="rounded-lg border border-gray-800 bg-gray-950 p-4">
              <h3 className="text-sm text-gray-400">Recommendation</h3>
              {overview.last_recommendation ? (
                <>
                  <p className="mt-2 text-lg font-medium capitalize text-white">
                    {overview.last_recommendation.action}
                  </p>
                  <p className="mt-1 text-sm text-gray-400">{overview.last_recommendation.reason}</p>
                </>
              ) : (
                <p className="mt-2 text-sm text-gray-500">No recommendation available</p>
              )}
            </article>
          </div>

          <div>
            <h3 className="mb-3 font-medium text-gray-200">Zones at {overview.location.name}</h3>
            {overview.zones.length === 0 ? (
              <p className="rounded-lg border border-gray-800 bg-gray-950 p-4 text-sm text-gray-400">
                This location has no zones.
              </p>
            ) : (
              <div className="grid gap-4 lg:grid-cols-2">
                {overview.zones.map((zone) => {
                  const readingsByDevice = new Map(
                    zone.latest_readings.map((reading) => [reading.device_id, reading]),
                  );

                  return (
                    <article key={zone.id} className="rounded-lg border border-gray-800 bg-gray-950 p-4">
                      <div className="flex flex-wrap items-start justify-between gap-2">
                        <h4 className="font-medium text-white">{zone.name}</h4>
                        <p className="text-xs text-gray-500">
                          Moisture thresholds: {zone.moisture_threshold_low}–{zone.moisture_threshold_high}
                        </p>
                      </div>
                      {zone.devices.length === 0 ? (
                        <p className="mt-4 text-sm text-gray-500">No assigned devices</p>
                      ) : (
                        <ul className="mt-3 divide-y divide-gray-800">
                          {zone.devices.map((device) => {
                            const reading = readingsByDevice.get(device.id);
                            return (
                              <li key={device.id} className="py-3 first:pt-0 last:pb-0">
                                <div className="flex flex-wrap items-baseline justify-between gap-2">
                                  <span className="font-medium text-gray-200">{device.display_name}</span>
                                  <span className="text-xs text-gray-500">
                                    {device.role} · {device.device_type}
                                  </span>
                                </div>
                                {reading ? (
                                  <p className="mt-2 text-sm text-gray-300">
                                    {reading.value} {reading.unit}
                                    <span className="ml-2 text-gray-500">
                                      Tracking {reading.tracking_enabled ? "on" : "off"} · Sampling every{" "}
                                      {reading.sampling_interval_seconds}s
                                    </span>
                                  </p>
                                ) : (
                                  <p className="mt-2 text-sm text-gray-500">No reading available</p>
                                )}
                              </li>
                            );
                          })}
                        </ul>
                      )}
                    </article>
                  );
                })}
              </div>
            )}
          </div>
        </>
      ) : null}
    </section>
  );
}
