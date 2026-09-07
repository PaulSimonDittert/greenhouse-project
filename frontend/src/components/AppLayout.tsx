import React from "react";
import HealthStatus from "./HealthStatus";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col font-sans">
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🌱</span>
          <h1 className="text-xl font-bold tracking-tight text-white">Smart Greenhouse Control</h1>
        </div>
        <HealthStatus />
      </header>
      <main className="flex-1 max-w-7xl w-full mx-auto p-6">{children}</main>
      <footer className="border-t border-gray-800 py-4 text-center text-xs text-gray-500">
        Design Patterns & Object Oriented Techniques — Phase 1 Skeleton
      </footer>
    </div>
  );
}