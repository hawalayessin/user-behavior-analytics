import { useState, useMemo } from "react";
import { AlertCircle, RotateCcw } from "lucide-react";
import FilterBar from "../components/dashboard/FilterBar";
import KPICard from "../components/dashboard/KPICard";
import DAUTrendChart from "../components/dashboard/userActivity/DAUTrendChart";
import ServiceActivityTable from "../components/dashboard/userActivity/ServiceActivityTable";
import UserGrowthChart from "../components/dashboard/userActivity/UserGrowthChart";
import UserDistributionByServiceChart from "../components/dashboard/userActivity/UserDistributionByServiceChart";
import ActivityHeatmap from "../components/dashboard/userActivity/ActivityHeatmap";
import PeakEvidenceCard from "../components/dashboard/PeakEvidenceCard";
import { useUserActivity } from "../hooks/useUserActivity";
import { useOverview } from "../hooks/useOverview";
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

function formatDisplayDate(value) {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

const KPISkeleton = () => (
  <div className="w-full h-32 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
);
const ChartSkeleton = () => (
  <div className="w-full h-96 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
);

const DAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export default function UserActivityPage() {
  const [filters, setFilters] = useState(getDefaultFilters());

  const {
    data: activityData,
    loading: activityLoading,
    error: activityError,
    refetch: refetchActivity,
  } = useUserActivity(filters);

  const { data: overviewData } = useOverview(filters);

  const subscriptionDistributionData = useMemo(() => {
    const fromOverview = (overviewData?.top_services ?? [])
      .map((row) => ({
        service_name: row?.name,
        subscriptions: Number(row?.total || 0),
        active_subscriptions: Number(row?.active_subs || 0),
      }))
      .filter((row) => row.service_name && row.subscriptions > 0);

    if (fromOverview.length > 0) return fromOverview;

    return (activityData?.by_service ?? []).map((row) => ({
      service_name: row.service_name,
      subscriptions: Number(row.subscriptions || 0),
      active_subscriptions: Number(row.active_users || 0),
    }));
  }, [activityData?.by_service, overviewData?.top_services]);

  const kpis = useMemo(() => {
    if (!activityData?.kpis) return null;
    return {
      active_users_period: activityData.kpis.active_users_period ?? 0,
      avg_dau_period:
        activityData.kpis.avg_dau_period ?? activityData.kpis.dau_today ?? 0,
      avg_wau_period:
        activityData.kpis.avg_wau_period ??
        activityData.kpis.wau_current_week ??
        0,
      avg_mau_period:
        activityData.kpis.avg_mau_period ??
        activityData.kpis.mau_current_month ??
        0,
      period_stickiness_pct:
        activityData.kpis.period_stickiness_pct ??
        activityData.kpis.stickiness_pct ??
        0,
      dau_today: activityData.kpis.dau_today ?? 0,
      wau_current_week: activityData.kpis.wau_current_week ?? 0,
      mau_current_month: activityData.kpis.mau_current_month ?? 0,
      stickiness_pct: activityData.kpis.stickiness_pct ?? 0,
      inactive_count: activityData.kpis.inactive_count ?? 0,
      avg_lifetime_days: activityData.kpis.avg_lifetime_days ?? 0,
    };
  }, [activityData]);

  const periodLabel = useMemo(() => {
    const start = formatDisplayDate(activityData?.filters_applied?.start_date);
    const end = formatDisplayDate(activityData?.filters_applied?.end_date);
    if (!start || !end) return "selected period";
    return `${start} - ${end}`;
  }, [activityData?.filters_applied?.end_date, activityData?.filters_applied?.start_date]);

  const kpiAnchorLabel = formatDisplayDate(activityData?.kpi_anchor ?? activityData?.data_anchor);

  const peakInsights = useMemo(() => {
    const trend = activityData?.dau_trend ?? [];
    const peakDau = trend.reduce(
      (max, row) => (Number(row.dau ?? 0) > Number(max?.dau ?? -1) ? row : max),
      null,
    );
    const peakWau = trend.reduce(
      (max, row) => (Number(row.wau ?? 0) > Number(max?.wau ?? -1) ? row : max),
      null,
    );
    const heatmap = activityData?.activity_heatmap ?? [];
    const peakHour = heatmap.reduce(
      (max, row) => (Number(row.count ?? 0) > Number(max?.count ?? -1) ? row : max),
      null,
    );

    return { peakDau, peakWau, peakHour };
  }, [activityData?.activity_heatmap, activityData?.dau_trend]);

  const handleApplyFilters = (f) => {
    setFilters(f);
  };

  return (
      <div className="space-y-6">
        {/* ── Header ────────────────────────────────────────── */}
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">
            Users Activity
          </h1>
          <p className="text-sm text-slate-400">
            Comprehensive analysis of engagement and activity
          </p>
          {kpiAnchorLabel && (
            <p className="mt-1 text-xs text-slate-500">
              Period: {periodLabel} · Data anchor: {kpiAnchorLabel}
            </p>
          )}
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
                  title="Avg DAU (Period)"
                  value={Math.round(kpis.avg_dau_period).toLocaleString()}
                  subtitle={`Average daily active users · ${periodLabel}`}
                  icon={Users}
                  iconColor="#7C3AED"
                  iconBg="bg-purple-500/10"
                  trend={0}
                  trendLabel="stable"
                />
                <KPICard
                  title="Avg WAU (Period)"
                  value={Math.round(kpis.avg_wau_period).toLocaleString()}
                  subtitle="Average weekly active users in selected period"
                  icon={TrendingUp}
                  iconColor="#3B82F6"
                  iconBg="bg-blue-500/10"
                  trend={0}
                  trendLabel="stable"
                />
                <KPICard
                  title="Avg MAU (Period)"
                  value={Math.round(kpis.avg_mau_period).toLocaleString()}
                  subtitle="Average monthly active users across the period"
                  icon={Calendar}
                  iconColor="#10B981"
                  iconBg="bg-green-500/10"
                  trend={0}
                  trendLabel="stable"
                />
                <KPICard
                  title="Stickiness"
                  value={`${kpis.period_stickiness_pct.toFixed(1)}%`}
                  subtitle="Avg DAU / Avg MAU × 100"
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
        {!activityError && !activityLoading && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <PeakEvidenceCard
              title="Peak DAU"
              value={(peakInsights.peakDau?.dau ?? 0).toLocaleString()}
              subtitle={formatDisplayDate(peakInsights.peakDau?.date) ?? periodLabel}
              icon={Users}
              accent="cyan"
            />
            <PeakEvidenceCard
              title="Peak WAU"
              value={(peakInsights.peakWau?.wau ?? 0).toLocaleString()}
              subtitle={formatDisplayDate(peakInsights.peakWau?.date) ?? periodLabel}
              icon={TrendingUp}
              accent="emerald"
            />
            <PeakEvidenceCard
              title="Peak Hour"
              value={(peakInsights.peakHour?.count ?? 0).toLocaleString()}
              subtitle={
                peakInsights.peakHour
                  ? `${DAYS_EN[peakInsights.peakHour.day] ?? "Day"} ${peakInsights.peakHour.hour}:00`
                  : "No activity peak"
              }
              icon={Clock}
              accent="amber"
            />
          </div>
        )}

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
                    data={subscriptionDistributionData}
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

  );
}
