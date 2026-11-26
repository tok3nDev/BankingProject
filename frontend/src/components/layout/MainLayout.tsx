
import { Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

const pageTitles: Record<string, string> = {
  "/": "Dashboard",
  "/customers": "Customers",
  "/applications": "Applications",
  "/credit-scoring": "Credit Scoring",
  "/decisions": "Decisions",
  "/ai-assistant": "AI Assistant",
  "/settings": "Settings",
};

export function MainLayout() {
  const location = useLocation();

  const title = pageTitles[location.pathname] ?? "Dashboard";

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />

      <div className="flex min-w-0 flex-1 flex-col">
        <Header title={title} />

        <main className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
