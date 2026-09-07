export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-emerald-900/40 to-gray-900 p-6 rounded-2xl border border-emerald-800/30">
        <h2 className="text-2xl font-semibold text-emerald-400">System Overview</h2>
        <p className="text-gray-400 mt-1">
          Infrastructure skeleton is fully operational. Future phases will inject live telemetry, actuators, and control patterns here.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="font-medium text-gray-300">Sensors</h3>
          <p className="text-sm text-gray-500 mt-1">Placeholder for sensors</p>
          <div className="mt-4 text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded inline-block">Placeholder</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="font-medium text-gray-300">Configuration</h3>
          <p className="text-sm text-gray-500 mt-1">Placeholder for configuration</p>
          <div className="mt-4 text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded inline-block">Placeholder</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="font-medium text-gray-300">Automation</h3>
          <p className="text-sm text-gray-500 mt-1">Placeholder for automation</p>
          <div className="mt-4 text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded inline-block">Placeholder</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="font-medium text-gray-300">Overview</h3>
          <p className="text-sm text-gray-500 mt-1">Placeholder for overview</p>
          <div className="mt-4 text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded inline-block">Placeholder</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="font-medium text-gray-300">Controls</h3>
          <p className="text-sm text-gray-500 mt-1">Placeholder for controls</p>
          <div className="mt-4 text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded inline-block">Placeholder</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="font-medium text-gray-300">Events</h3>
          <p className="text-sm text-gray-500 mt-1">Placeholder for events</p>
          <div className="mt-4 text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded inline-block">Placeholder</div>
        </div>
      </div>
    </div>
  );
}