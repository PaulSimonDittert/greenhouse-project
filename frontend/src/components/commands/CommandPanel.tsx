import { useEffect, useState } from "react";
import {
  fetchCommandLog,
  fetchDevices,
  submitCommand,
  type CommandLogDto,
  type DeviceDto,
} from "../../services/api";

export default function CommandPanel() {
  const [actuators, setActuators] = useState<DeviceDto[]>([]);
  const [history, setHistory] = useState<CommandLogDto[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState("");
  const [lightLevel, setLightLevel] = useState(1);
  const [isBusy, setIsBusy] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    try {
      const [deviceRows, commandRows] = await Promise.all([
        fetchDevices(undefined, "actuator"),
        fetchCommandLog(20),
      ]);
      setActuators(deviceRows);
      setSelectedDeviceId((current) => current || deviceRows[0]?.id || "");
      setHistory(commandRows);
      setError(null);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Failed to load actuator controls");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  const selectedDevice = actuators.find((device) => device.id === selectedDeviceId) ?? null;
  const allowedCommands = selectedDevice?.allowed_commands ?? [];

  const handleCommand = async (commandType: string) => {
    if (!selectedDeviceId) {
      setError("Select an actuator before issuing a command.");
      return;
    }

    setIsBusy(true);
    setError(null);

    try {
      const payload = commandType === "set_light_level" ? { level: Number(lightLevel) || 1 } : {};
      await submitCommand({
        command_type: commandType,
        device_id: selectedDeviceId,
        payload,
      });
      await refresh();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Failed to issue command");
    } finally {
      setIsBusy(false);
    }
  };

  return (
    <section id="controls" className="rounded-xl border border-gray-800 bg-gray-900 p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="font-medium text-gray-300">Controls</h3>
          <p className="mt-1 text-sm text-gray-500">State-aware actuator commands and command history</p>
        </div>
        <button
          type="button"
          onClick={() => void refresh()}
          disabled={isLoading || isBusy}
          className="rounded bg-gray-800 px-3 py-2 text-sm text-gray-200 transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div className="mb-5 grid gap-4 lg:grid-cols-[1.2fr_1fr]">
        <label className="text-sm text-gray-300">
          Actuator
          <select
            value={selectedDeviceId}
            onChange={(event) => setSelectedDeviceId(event.target.value)}
            disabled={actuators.length === 0 || isBusy}
            className="mt-1 w-full rounded border border-gray-700 bg-gray-950 px-2.5 py-2 text-sm text-gray-200 disabled:opacity-50"
          >
            {actuators.length === 0 ? <option value="">No actuators available</option> : null}
            {actuators.map((device) => (
              <option key={device.id} value={device.id}>
                {device.display_name}
              </option>
            ))}
          </select>
        </label>

        <div className="flex items-end gap-3">
          <label className="flex-1 text-sm text-gray-300">
            Light level
            <input
              type="number"
              min={1}
              max={10}
              value={lightLevel}
              onChange={(event) => setLightLevel(Number(event.target.value) || 1)}
              disabled={isBusy}
              className="mt-1 w-full rounded border border-gray-700 bg-gray-950 px-2.5 py-2 text-sm text-gray-200"
            />
          </label>
        </div>
      </div>

      <div className="mb-5 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => void handleCommand("start_pump")}
          disabled={!allowedCommands.includes("start_pump") || isBusy}
          className="rounded bg-emerald-700 px-3 py-2 text-sm text-white transition hover:bg-emerald-600 disabled:cursor-not-allowed disabled:bg-gray-700 disabled:text-gray-400"
        >
          Start Pump
        </button>

        <button
          type="button"
          onClick={() => void handleCommand("stop_pump")}
          disabled={!allowedCommands.includes("stop_pump") || isBusy}
          className="rounded bg-amber-700 px-3 py-2 text-sm text-white transition hover:bg-amber-600 disabled:cursor-not-allowed disabled:bg-gray-700 disabled:text-gray-400"
        >
          Stop Pump
        </button>

        <button
          type="button"
          onClick={() => void handleCommand("set_light_level")}
          disabled={!allowedCommands.includes("set_light_level") || isBusy}
          className="rounded bg-sky-700 px-3 py-2 text-sm text-white transition hover:bg-sky-600 disabled:cursor-not-allowed disabled:bg-gray-700 disabled:text-gray-400"
        >
          Set Light Level
        </button>
      </div>

      {selectedDevice ? (
        <p className="mb-4 text-xs text-gray-400">
          Selected: {selectedDevice.display_name} • state: {selectedDevice.state ?? "idle"} • allowed: {allowedCommands.length ? allowedCommands.join(", ") : "none"}
        </p>
      ) : null}

      {error ? <p role="alert" className="mb-4 text-sm text-red-400">{error}</p> : null}

      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="border-b border-gray-800 text-xs uppercase tracking-wide text-gray-500">
            <tr>
              <th scope="col" className="px-3 py-2">When</th>
              <th scope="col" className="px-3 py-2">Device</th>
              <th scope="col" className="px-3 py-2">Command</th>
              <th scope="col" className="px-3 py-2">Status</th>
              <th scope="col" className="px-3 py-2">Error</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {history.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-3 py-4 text-gray-500">
                  No command history yet.
                </td>
              </tr>
            ) : (
              history.map((entry) => (
                <tr key={entry.id} className="text-gray-300">
                  <td className="whitespace-nowrap px-3 py-3">{new Date(entry.created_at).toLocaleString()}</td>
                  <td className="px-3 py-3">{entry.device_id}</td>
                  <td className="px-3 py-3">{entry.command_type}</td>
                  <td className="px-3 py-3">
                    <span
                      className={`rounded px-2 py-1 text-xs font-medium ${
                        entry.status === "success"
                          ? "bg-emerald-900/70 text-emerald-300"
                          : entry.status === "rejected"
                            ? "bg-amber-900/70 text-amber-300"
                            : "bg-red-900/70 text-red-300"
                      }`}
                    >
                      {entry.status}
                    </span>
                  </td>
                  <td className="px-3 py-3">{entry.error_message ?? "—"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
