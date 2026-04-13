import { useState, useMemo } from "react";
import { AlertCircle, RotateCcw } from "lucide-react";
import AppLayout from "../components/layout/AppLayout";
import FilterBar from "../components/dashboard/FilterBar";
import KPICard from "../components/dashboard/KPICard";
import DAUTrendChart from "../components/dashboard/userActivity/DAUTrendChart";
import ServiceActivityTable from "../components/dashboard/userActivity/ServiceActivityTable";
import UserGrowthChart from "../components/dashboard/userActivity/UserGrowthChart";
import UserDistributionByServiceChart from "../components/dashboard/userActivity/UserDistributionByServiceChart";
import ActivityHeatmap from "../components/dashboard/userActivity/ActivityHeatmap";
import { useUserActivity } from "../hooks/useUserActivity";
import { DEFAULT_ANALYTICS_FILTERS } from "../constants/dateFilters";
import {
  Users,
  TrendingUp,
  Calendar,
  Zap,
  AlertTriangle,
  Clock,
} from "lucide-react";

function getDefaultFilters() {
  return { ...DEFAULT_ANALYTICS_FILTERS };
}

const KPISkeleton = () => (
  <div className="w-full h-32 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
);
const ChartSkeleton = () => (
  <div className="w-full h-96 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
);

export default function UserActivityPage() {
  const [filters, setFilters] = useState(getDefaultFilters());

  const {
    data: activityData,
    loading: activityLoading,
    error: activityError,
    refetch: refetchActivity,
  } = useUserActivity(filters);

  const kpis = useMemo(() => {
    if (!activityData?.kpis) return null;
    return {
      dau_today: activityData.kpis.dau_today ?? 0,
      wau_current_week: activityData.kpis.wau_current_week ?? 0,
      mau_current_month: activityData.kpis.mau_current_month ?? 0,
      stickiness_pct: activityData.kpis.stickiness_pct ?? 0,
      inactive_count: activityData.kpis.inactive_count ?? 0,
      avg_lifetime_days: activityData.kpis.avg_lifetime_days ?? 0,
    };
  }, [activityData?.kpis]);

  const handleApplyFilters = (f) => {
    setFilters(f);
  };

  return (
    <AppLayout pageTitle="Users Activity">
      <div className="space-y-6">
        {/* ── Header ────────────────────────────────────────── */}
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">
            Users Activity
          </h1>
          <p className="text-sm text-slate-400">
            Comprehensive analysis of engagement and activity
          </p>
        </div>

        {/* ── Filter Bar ────────────────────────────────────── */}
        <FilterBar
          onApply={handleApplyFilters}
          appliedFilters={filters}
          anchorDate={activityData?.data_anchor ?? null}
        />

        {/* ── Erreur analytics ──────────────────────────────── */}
        {activityError && (
          <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
            <p className="flex-1 text-sm text-red-200">{activityError}</p>
            <button
              onClick={refetchActivity}
              className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
            >
              <RotateCcw size={14} /> Réessayer
            </button>
          </div>
        )}

        {/* ── KPI Cards ─────────────────────────────────────── */}
        {!activityError && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {activityLoading ? (
              Array.from({ length: 6 }).map((_, i) => <KPISkeleton key={i} />)
            ) : kpis ? (
              <>
                <KPICard
                  title="DAU (Last 24h)"
                  value={kpis.dau_today.toLocaleString()}
                  subtitle="Unique active users in last 24h"
                  icon={Users}
                  iconColor="#7C3AED"
                  iconBg="bg-purple-500/10"
                  trend={0}
                  trendLabel="stable"
                />
                <KPICard
                  title="WAU (Last 7 days)"
                  value={kpis.wau_current_week.toLocaleString()}
                  subtitle="Active users in last 7 days"
                  icon={TrendingUp}
                  iconColor="#3B82F6"
                  iconBg="bg-blue-500/10"
                  trend={0}
                  trendLabel="stable"
                />
                <KPICard
                  title="MAU (Current month)"
                  value={kpis.mau_current_month.toLocaleString()}
                  subtitle="Unique active users in current month window"
                  icon={Calendar}
                  iconColor="#10B981"
                  iconBg="bg-green-500/10"
                  trend={0}
                  trendLabel="stable"
                />
                <KPICard
                  title="Stickiness"
                  value={`${kpis.stickiness_pct.toFixed(1)}%`}
                  subtitle="DAU / MAU × 100"
                  icon={Zap}
                  iconColor="#F59E0B"
                  iconBg="bg-amber-500/10"
                  trend={0}
                  trendLabel="stable"
                />
                <KPICard
                  title="Inactive users"
                  value={kpis.inactive_count.toLocaleString()}
                  subtitle="No activity for 7+ days"
                  icon={AlertTriangle}
                  iconColor="#EF4444"
                  iconBg="bg-red-500/10"
                  trend={0}
                  trendLabel="negative"
                  alert={kpis.inactive_count > 100}
                />
                <KPICard
                  title="Lifetime"
                  value={`${kpis.avg_lifetime_days.toFixed(0)}d`}
                  subtitle="Average subscription duration"
                  icon={Clock}
                  iconColor="#8B5CF6"
                  iconBg="bg-violet-500/10"
                  trend={0}
                  trendLabel="stable"
                />
              </>
            ) : null}
          </div>
        )}

        {/* ── DAU Trend Chart ───────────────────────────────── */}
        {!activityError && (
          <div>
            {activityLoading ? (
              <ChartSkeleton />
            ) : activityData?.dau_trend ? (
              <DAUTrendChart data={activityData.dau_trend} />
            ) : null}
          </div>
        )}

        {/* ── Service Activity & User Growth ────────────────── */}
        {!activityError && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {activityLoading ? (
              <>
                <ChartSkeleton />
                <ChartSkeleton />
              </>
            ) : (
              <>
                {activityData?.by_service && (
                  <ServiceActivityTable data={activityData.by_service} />
                )}
                <div>
                  <UserGrowthChart data={activityData?.user_growth ?? []} />
                  <UserDistributionByServiceChart
                    data={(activityData?.by_service ?? []).map((row) => ({
                      service_name: row.service_name,
                      subscriptions: Number(row.subscriptions || 0),
                    }))}
                  />
                </div>
              </>
            )}
          </div>
        )}

        {/* ── Activity Heatmap ──────────────────────────────── */}
        {!activityError && (
          <div>
            {activityLoading ? (
              <ChartSkeleton />
            ) : activityData?.activity_heatmap ? (
              <ActivityHeatmap data={activityData.activity_heatmap} />
            ) : null}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
