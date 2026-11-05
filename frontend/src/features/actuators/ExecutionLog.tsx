import { useEffect, useState } from "react";
import {
  applyActuatorCommand,
  fetchActuatorExecutions,
  fetchDevices,
  type ActuatorExecutionDto,
  type DeviceDto,
} from "../../services/api";

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "The request failed. Please try again.";
}

export default function ExecutionLog() {
  const [executions, setExecutions] = useState<ActuatorExecutionDto[]>([]);
  const [actuators, setActuators] = useState<DeviceDto[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState("");
  const [command, setCommand] = useState("demo_command");
  const [isLoading, setIsLoading] = useState(true);
  const [isApplying, setIsApplying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const refreshExecutions = async () => {
    setIsLoading(true);
    try {
      setExecutions(await fetchActuatorExecutions());
      setError(null);
    } catch (loadError) {
      setError(errorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let active = true;
    Promise.all([fetchDevices(undefined, "actuator"), fetchActuatorExecutions()])
      .then(([deviceRows, executionRows]) => {
        if (!active) return;
        setActuators(deviceRows);
        setSelectedDeviceId((current) => current || deviceRows[0]?.id || "");
        setExecutions(executionRows);
        setError(null);
      })
      .catch((loadError: unknown) => {
        if (active) setError(errorMessage(loadError));
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const handleApply = async () => {
    if (!selectedDeviceId) {
      setError("Select an actuator before applying a command.");
      return;
    }

    setIsApplying(true);
    setError(null);
    setNotice(null);
    try {
      const result = await applyActuatorCommand(selectedDeviceId, command);
      setNotice(result.success
        ? "Attempt completed successfully."
        : result.message ?? "The attempt was blocked by policy.");
    } catch (applyError) {
      setError(errorMessage(applyError));
    } finally {
      await refreshExecutions();
      setIsApplying(false);
    }
  };

  const deviceNames = new Map(actuators.map((device) => [device.id, device.display_name]));

  return (
    <section id="actuator-executions" className="space-y-5 rounded-xl border border-gray-800 bg-gray-900 p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-white">Actuator Execution Log</h2>
          <p className="mt-1 text-sm text-gray-500">
            Commands are not validated in this phase. Any command succeeds unless the actuator has been running
            for at least 30 minutes. A success row has an empty message and policy logging; a blocked row shows
            “Max run time exceeded” with policies maxRunTime and logging.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void refreshExecutions()}
          disabled={isLoading}
          className="rounded bg-gray-800 px-3 py-2 text-sm text-gray-200 transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div className="flex flex-wrap items-end gap-3 rounded-lg border border-gray-800 bg-gray-950 p-4">
        <label className="min-w-52 flex-1 text-sm text-gray-300">
          Actuator
          <select
            value={selectedDeviceId}
            onChange={(event) => setSelectedDeviceId(event.target.value)}
            disabled={actuators.length === 0 || isApplying}
            className="mt-1 w-full rounded border border-gray-700 bg-gray-900 px-2.5 py-2 text-sm text-gray-200 disabled:opacity-50"
          >
            {actuators.length === 0 ? <option value="">No actuators available</option> : null}
            {actuators.map((device) => (
              <option key={device.id} value={device.id}>{device.display_name}</option>
            ))}
          </select>
        </label>
        <label className="min-w-52 flex-1 text-sm text-gray-300">
          Command (not validated)
          <input
            value={command}
            onChange={(event) => setCommand(event.target.value)}
            disabled={isApplying}
            className="mt-1 w-full rounded border border-gray-700 bg-gray-900 px-2.5 py-2 text-sm text-gray-200"
          />
        </label>
        <button
          type="button"
          onClick={() => void handleApply()}
          disabled={!selectedDeviceId || isApplying}
          className="rounded bg-emerald-800 px-3 py-2 text-sm text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isApplying ? "Applying..." : "Apply demo command"}
        </button>
      </div>

      {notice ? <p role="status" className="text-sm text-emerald-400">{notice}</p> : null}
      {error ? <p role="alert" className="text-sm text-red-400">{error}</p> : null}

      {isLoading && executions.length === 0 ? (
        <p role="status" className="text-sm text-gray-400">Loading executions...</p>
      ) : executions.length === 0 ? (
        <p className="rounded-lg border border-gray-800 bg-gray-950 p-4 text-sm text-gray-400">
          No actuator executions yet. Apply a demo command to create the first log entry.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px] text-left text-sm">
            <thead className="border-b border-gray-800 text-xs uppercase tracking-wide text-gray-500">
              <tr>
                <th scope="col" className="px-3 py-2">Time</th>
                <th scope="col" className="px-3 py-2">Device</th>
                <th scope="col" className="px-3 py-2">Result</th>
                <th scope="col" className="px-3 py-2">Policies</th>
                <th scope="col" className="px-3 py-2">Message</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {executions.map((execution) => (
                <tr key={execution.id} className="text-gray-300">
                  <td className="whitespace-nowrap px-3 py-3">{new Date(execution.created_at).toLocaleString()}</td>
                  <td className="px-3 py-3" title={execution.device_id}>
                    {deviceNames.get(execution.device_id) ?? execution.device_id}
                  </td>
                  <td className="px-3 py-3">
                    <span className={`rounded px-2 py-1 text-xs font-medium ${
                      execution.success ? "bg-emerald-900/70 text-emerald-300" : "bg-red-900/70 text-red-300"
                    }`}>
                      {execution.success ? "Success" : "Failed"}
                    </span>
                  </td>
                  <td className="px-3 py-3">{execution.policy_applied.join(", ")}</td>
                  <td className="px-3 py-3">{execution.message ?? <span className="text-gray-500">Empty</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
