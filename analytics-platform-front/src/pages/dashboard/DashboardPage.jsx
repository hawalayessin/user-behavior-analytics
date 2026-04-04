import { useState, useEffect, useCallback } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import api from "../../services/api";
import AppLayout from "../../components/layout/AppLayout";
import FilterBar from "../../components/dashboard/FilterBar";
import TabNavigation from "../../components/dashboard/TabNavigation";
import OverviewTab from "../../components/dashboard/tabs/OverviewTab";
import EngagementTab from "../../components/dashboard/tabs/EngagementTab";
import RevenueTab from "../../components/dashboard/tabs/RevenueTab";
import TrialChurnTab from "../../components/dashboard/tabs/TrialChurnTab";
import { DEFAULT_ANALYTICS_FILTERS } from "../../constants/dateFilters";

const DEFAULT_FILTERS = DEFAULT_ANALYTICS_FILTERS;

// ── Skeleton ───────────────────────────────────────────────────────────────────
function SkeletonBlock({ className }) {
  return (
    <div className={`animate-pulse bg-slate-800 rounded-xl ${className}`} />
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        {Array.from({ length: 7 }).map((_, i) => (
          <SkeletonBlock key={i} className="h-32" />
        ))}
      </div>
      <div className="flex gap-4">
        <SkeletonBlock className="h-72 flex-1" />
        <SkeletonBlock className="h-72 flex-1" />
      </div>
      <SkeletonBlock className="h-64" />
      <SkeletonBlock className="h-56" />
    </div>
  );
}

// ── Error ──────────────────────────────────────────────────────────────────────
function DashboardError({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center h-96 gap-4">
      <AlertCircle size={48} className="text-red-400" />
      <p className="text-slate-400 text-sm">{message}</p>
      <button
        onClick={onRetry}
        className="flex items-center gap-2 px-4 py-2 bg-violet-700 hover:bg-violet-800 text-white text-sm font-semibold rounded-lg transition"
      >
        <RefreshCw size={15} />
        Réessayer
      </button>
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [activeTab, setActiveTab] = useState(0);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();

      if (filters.start_date) params.append("start_date", filters.start_date);
      if (filters.end_date) params.append("end_date", filters.end_date);
      if (filters.service_id) params.append("service_id", filters.service_id);

      const qs = params.toString();
      const res = await api.get(`/analytics/overview${qs ? `?${qs}` : ""}`);
      setData(res.data);
    } catch (err) {
      console.error("[DashboardPage] fetch error:", err?.response?.data ?? err);
      setError("Impossible de charger les données.");
    } finally {
      setLoading(false);
    }
  }, [filters.end_date, filters.service_id, filters.start_date]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <AppLayout pageTitle="Analytics Overview" hasNotifications showExportButton>
      <div className="space-y-5 pb-6">
        {/* Filter Bar — toujours visible */}
        <FilterBar onApply={setFilters} />

        {/* Tab Navigation */}
        <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Contenu */}
        {loading && <DashboardSkeleton />}

        {!loading && error && (
          <DashboardError message={error} onRetry={fetchData} />
        )}

        {!loading && !error && data && (
          <>
            {activeTab === 0 && <OverviewTab data={data} filters={filters} />}
            {activeTab === 1 && <EngagementTab data={data} filters={filters} />}
            {activeTab === 2 && <RevenueTab data={data} filters={filters} />}
            {activeTab === 3 && <TrialChurnTab data={data} filters={filters} />}
          </>
        )}
      </div>
    </AppLayout>
  );
}
