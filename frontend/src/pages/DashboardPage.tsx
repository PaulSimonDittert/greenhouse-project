import SensorList from "../features/sensors/SensorList";
import DeviceList from "../components/devices/DeviceList";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <SensorList />
        <DeviceList />
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