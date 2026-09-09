import { useState } from "react";
import AppLayout from "./components/AppLayout";
import DashboardPage from "./pages/DashboardPage";
import HomePage from "./pages/HomePage";

export default function App() {
  const [currentPage, setCurrentPage] = useState("home");

  return (
    <AppLayout currentPage={currentPage} onNavigate={setCurrentPage}>
      {currentPage === "home" ? <HomePage /> : <DashboardPage />}
    </AppLayout>
  );
}