import { useEffect, useState } from "react";
import { fetchSensors, createSensor, type SensorDto } from "../../services/api";

export default function SensorList() {
  const [sensors, setSensors] = useState<SensorDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadSensors = async () => {
    try {
      const data = await fetchSensors();
      setSensors(data);
    } catch (err) {
      setError("Failed to load sensors");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadSensors(); }, []);

  const handleAdd = async (type: string) => {
    try {
      await createSensor(type);
      await loadSensors(); // Reload the list
    } catch (err) {
      alert("Failed to add sensor");
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
      
      {sensors.length === 0 ? (
        <p className="text-sm text-gray-500">No sensors added yet.</p>
      ) : (
        <div className="space-y-3">
          {sensors.map((sensor) => (
            <div key={sensor.id} className="bg-gray-800 border border-gray-700 p-3 rounded-lg flex flex-col">
              <span className="font-medium text-gray-200">{sensor.display_name}</span>
              <span className="text-xs text-gray-400 mt-1">Type: {sensor.device_type}</span>
              <span className="text-xs text-gray-500 mt-1 font-mono">
                {JSON.stringify(sensor.default_config)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}