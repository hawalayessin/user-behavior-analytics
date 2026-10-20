import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import Footer from "./Footer";
import { isDemoMode } from "../../demo/config";
import MobileNavigation from "../../demo/MobileNavigation";
import "../../demo/demo.css";

const ROUTE_META = {
  "/dashboard": { title: "Analytics Overview", notifications: true, export: true },
  "/dashboard-1": { title: "Analytics Overview", notifications: true, export: true },
  "/analytics/behaviors": { title: "Users Activity" },
  "/analytics/trial": { title: "Free Trial Behavior" },
  "/analytics/retention": { title: "Retention Analysis" },
  "/analytics/campaigns": { title: "Campaign Impact Analysis" },
  "/analytics/churn": { title: "Churn Analysis" },
  "/analytics/churn-prediction": { title: "Churn Prediction" },
  "/analytics/cross-service": { title: "Cross-Service Behavior" },
  "/analytics/segmentation": { title: "User Segmentation" },
  "/analytics/anomalies": { title: "Anomaly Detection — AI" },
  "/management/subscribers": { title: "Abonnés" },
  "/admin/users": { title: "Platform Users" },
  "/admin/import": { title: "Import Data" },
  "/admin/management": { title: "Management" },
  "/admin/settings": { title: "System Settings" },
  "/admin/run-ai-models": { title: "Run AI Models" },
  "/admin/reports": { title: "Report Generator" },
  "/account/profile": { title: "Profile Settings" },
  "/notes": { title: "Analyst Notes" },
};

export default function AppLayout() {
  const location = useLocation();
  const meta = ROUTE_META[location.pathname] || {};
  const pageTitle = meta.title ?? "Dashboard";
  const hasNotifications = meta.notifications ?? false;
  const showExportButton = meta.export ?? false;

  return (
    <div
      className={`flex h-screen overflow-hidden${isDemoMode ? " portfolio-demo" : ""}`}
      style={{
        backgroundColor: "var(--color-bg-primary)",
        minHeight: "100vh",
      }}
    >
      <div className={isDemoMode ? "hidden md:block shrink-0" : "shrink-0"}>
        <Sidebar />
      </div>

      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {isDemoMode && (
          <div role="status" className="flex flex-wrap items-center justify-between gap-2 px-6 py-2 text-xs" style={{ backgroundColor: "#164e3b", color: "#d1fae5" }}>
            <span>Portfolio Demo | Synthetic Data | Illustrative AI Results</span>
            <a href="https://github.com/hawalayessin/user-behavior-analytics" target="_blank" rel="noreferrer" className="underline">GitHub</a>
          </div>
        )}
        {isDemoMode && <MobileNavigation />}
        <div className={isDemoMode ? "hidden md:block" : ""}>
        <Topbar
          pageTitle={pageTitle}
          hasNotifications={hasNotifications}
          showExportButton={showExportButton}
        />
        </div>

        <main className="flex-1 overflow-y-auto px-6 py-6 scrollbar-modern">
          <Outlet />
        </main>

        <Footer />
      </div>
    </div>
  );
}
