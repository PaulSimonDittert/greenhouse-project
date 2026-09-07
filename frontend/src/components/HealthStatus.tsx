import { useEffect, useState } from "react";
import { fetchHealth, type HealthResponse } from "../services/api";

export default function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setHealth(data);
        setLoading(false);
      })
      .catch(() => {
        setHealth({ status: "degraded", db: "fail" });
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <span className="text-gray-400 text-sm">Checking system health...</span>;
  }

  const isOk = health?.status === "ok" && health?.db === "ok";

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-800 border border-gray-700 text-sm">
      <span className={`w-2.5 h-2.5 rounded-full ${isOk ? "bg-green-500 animate-pulse" : "bg-red-500"}`} />
      <span className="text-gray-200 font-medium">
        API: {health?.status} | DB: {health?.db}
      </span>
    </div>
  );
}