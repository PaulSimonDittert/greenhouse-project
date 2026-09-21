import { useEffect, useState } from "react";
import { fetchDevices, provisionDeviceFamily, type DeviceDto } from "../../services/api";
import DeviceFamilySwitcher from "./DeviceFamilySwitcher";

export default function DeviceList() {
  const [devices, setDevices] = useState<DeviceDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [family, setFamily] = useState<string>("simulation");

  const loadDevices = async (selectedFamily: string) => {
    setLoading(true);
    try {
      const data = await fetchDevices(selectedFamily);
      setDevices(data);
      setError(null);
    } catch (err) {
      setError("Failed to load devices");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadDevices(family); }, [family]);

  const handleProvision = async () => {
    try {
      await provisionDeviceFamily(family);
      await loadDevices(family);
    } catch (err) {
      alert("Failed to provision family");
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
            </div>
          ))}
        </div>
      )}
    </div>
  );
}