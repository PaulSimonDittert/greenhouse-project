import React from "react";
import HealthStatus from "./HealthStatus";

interface AppLayoutProps {
  children: React.ReactNode;
  currentPage: string;
  onNavigate: (page: string) => void;
}

export default function AppLayout({ children, currentPage, onNavigate }: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col font-sans">
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold tracking-tight text-white">Smart Greenhouse</h1>
          </div>
          
          <nav className="flex items-center gap-2 border-l border-gray-700 pl-6">
            <button
              onClick={() => onNavigate("home")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${
                currentPage === "home" ? "bg-gray-800 text-white" : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/50"
              }`}
            >
              Home
            </button>
            <button
              onClick={() => onNavigate("dashboard")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${
                currentPage === "dashboard" ? "bg-gray-800 text-white" : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/50"
              }`}
            >
              Dashboard
            </button>
          </nav>
        </div>
        
        <HealthStatus />
      </header>
      <main className="flex-1 max-w-7xl w-full mx-auto p-6">{children}</main>
    </div>
  );
}