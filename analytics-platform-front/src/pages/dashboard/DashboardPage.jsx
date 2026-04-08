import { useMemo, useState } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import AppLayout from "../../components/layout/AppLayout";
import FilterBar from "../../components/dashboard/FilterBar";
import TabNavigation from "../../components/dashboard/TabNavigation";
import OverviewTab from "../../components/dashboard/tabs/OverviewTab";
import EngagementTab from "../../components/dashboard/tabs/EngagementTab";
import RevenueTab from "../../components/dashboard/tabs/RevenueTab";
import TrialChurnTab from "../../components/dashboard/tabs/TrialChurnTab";
import { DEFAULT_ANALYTICS_FILTERS } from "../../constants/dateFilters";
import { useOverview } from "../../hooks/useOverview";

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
  const normalizedFilters = useMemo(
    () => ({
      start_date: filters.start_date ?? null,
      end_date: filters.end_date ?? null,
      service_id: filters.service_id ?? null,
    }),
    [filters.end_date, filters.service_id, filters.start_date],
  );

  const { data, loading, error, refetch } = useOverview(normalizedFilters);

  const errorMessage =
    error?.response?.data?.detail ??
    error?.message ??
    "Impossible de charger les données.";

  return (
    <AppLayout pageTitle="Analytics Overview" hasNotifications showExportButton>
      <div className="space-y-5 pb-6">
        {/* Filter Bar — toujours visible */}
        <FilterBar onApply={setFilters} appliedFilters={filters} />

        {/* Tab Navigation */}
        <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Contenu */}
        {loading && <DashboardSkeleton />}

        {!loading && error && (
          <DashboardError message={errorMessage} onRetry={refetch} />
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
