import { useEffect, useState } from "react";
import {
  evaluateStrategy,
  fetchLocations,
  saveStrategy,
  type LocationDto,
  type StrategyRecommendationDto,
} from "../../services/api";

const strategyOptions = [
  { value: "conservative", label: "Conservative" },
  { value: "aggressive", label: "Aggressive" },
];

export default function StrategyPanel() {
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [selectedLocationId, setSelectedLocationId] = useState("");
  const [strategyKey, setStrategyKey] = useState("conservative");
  const [recommendation, setRecommendation] = useState<StrategyRecommendationDto | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    const loadLocations = async () => {
      try {
        const nextLocations = await fetchLocations();
        setLocations(nextLocations);
        if (nextLocations.length > 0) {
          setSelectedLocationId(nextLocations[0].id);
        }
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Failed to load locations");
      }
    };

    void loadLocations();
  }, []);

  const handleSave = async () => {
    if (!selectedLocationId) {
      setError("Select a location before saving the strategy.");
      return;
    }

    setIsSaving(true);
    setError(null);
    setSuccess(null);
    setRecommendation(null);

    try {
      await saveStrategy(selectedLocationId, strategyKey);
      setSuccess(`Saved strategy "${strategyKey}" for the selected location.`);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Failed to save the strategy.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleEvaluate = async () => {
    if (!selectedLocationId) {
      setError("Select a location before evaluating the strategy.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);
    setRecommendation(null);

    try {
      const result = await evaluateStrategy(selectedLocationId);
      setRecommendation(result);
      setSuccess("Evaluation completed.");
    } catch (evaluateError) {
      setError(evaluateError instanceof Error ? evaluateError.message : "Failed to evaluate automation strategy.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div id="automation" className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="mb-4">
        <h3 className="font-medium text-gray-300">Automation Strategy</h3>
        <p className="font-medium text-gray-500 mt-1">Phase 6</p>
      </div>

      <div className="space-y-4">
        <label className="block text-sm text-gray-300">
          Location
          <select
            value={selectedLocationId}
            onChange={(event) => setSelectedLocationId(event.target.value)}
            className="mt-1 w-full rounded border border-gray-700 bg-gray-900 px-2.5 py-2 text-sm text-gray-200 disabled:opacity-50"
            disabled={locations.length === 0}
          >
            {locations.length === 0 ? <option value="">No locations available</option> : null}
            {locations.map((location) => (
              <option key={location.id} value={location.id}>
                {location.name}
              </option>
            ))}
          </select>
        </label>

        <label className="block text-sm text-gray-300">
          Strategy
          <select
            value={strategyKey}
            onChange={(event) => setStrategyKey(event.target.value)}
            className="mt-1 w-full rounded border border-gray-700 bg-gray-900 px-2.5 py-2 text-sm text-gray-200"
          >
            {strategyOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handleSave}
            disabled={!selectedLocationId || isSaving}
            className="rounded bg-emerald-800 px-3 py-1.5 text-sm text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSaving ? "Saving..." : "Save strategy"}
          </button>
          <button
            type="button"
            onClick={handleEvaluate}
            disabled={!selectedLocationId || isLoading}
            className="rounded bg-emerald-800 px-3 py-1.5 text-sm text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoading ? "Evaluating..." : "Evaluate"}
          </button>
        </div>

        {success ? <div role="status" className="text-sm text-emerald-400">{success}</div> : null}
        {error ? <div role="alert" className="text-sm text-red-400">{error}</div> : null}

        {recommendation ? (
          <div className="border-t border-gray-800 pt-4">
            <h4 className="font-medium text-gray-300">Recommendation</h4>
            <p className="mt-2 text-sm text-gray-200">
              Action: <span className="font-medium">{recommendation.action}</span>
            </p>
            <p className="mt-1 text-sm text-gray-400">{recommendation.reason}</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}
