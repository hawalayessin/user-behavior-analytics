import React, { useState } from "react";
import { AlertCircle, RotateCcw } from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import AppLayout from "../../components/layout/AppLayout";
import FilterBar from "../../components/dashboard/FilterBar";
import KPICard from "../../components/dashboard/KPICard";
import { useChurnDashboard } from "../../hooks/useChurnDashboard";
import { useReactivationKPIs } from "../../hooks/useReactivationKPIs";
import { useReactivationByService } from "../../hooks/useReactivationByService";
import { DEFAULT_ANALYTICS_FILTERS } from "../../constants/dateFilters";

const COLORS = {
  churn: "#a12c7b",
  new: "#01696f",
  neutral: "#7a7974",
  warning: "#964219",
  palette: ["#01696f", "#a12c7b", "#964219", "#7a7974"],
};

const KPISkeleton = () => (
  <div className="w-full h-28 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
);
const ChartSkeleton = () => (
  <div className="w-full h-80 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
);

export default function ChurnAnalysisPage() {
  const [filters, setFilters] = useState(DEFAULT_ANALYTICS_FILTERS);

  const { data, isLoading, error, refetch } = useChurnDashboard(filters);
  const {
    data: reactivationKpis,
    isLoading: reactivationKpisLoading,
    error: reactivationKpisError,
  } = useReactivationKPIs(filters);
  const {
    data: reactivationByService,
    isLoading: reactivationByServiceLoading,
    error: reactivationByServiceError,
  } = useReactivationByService(filters);

  const dashboard = data || {};
  const { kpis, charts, meta } = dashboard;
  const reactivationRate = Number(reactivationKpis?.reactivation_rate ?? 0);
  const reactivationRateLabel =
    reactivationRate > 0 && reactivationRate < 1
      ? `${reactivationRate.toFixed(2)}%`
      : `${reactivationRate.toFixed(1)}%`;
  const reactivationChartData = [...(reactivationByService || [])]
    .sort((a, b) => (b.reactivated_users || 0) - (a.reactivated_users || 0))
    .slice(0, 10);

  return (
    <AppLayout pageTitle="Churn Analysis">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">
            Churn Analysis
          </h1>
          <p className="text-sm text-slate-400">
            {meta
              ? `Period: ${meta.period_start?.slice(0, 10)} → ${meta.period_end?.slice(0, 10)}`
              : "Understand why users leave"}
          </p>
        </div>

        <FilterBar
          onApply={(f) => setFilters(f)}
          defaultPeriod="all"
          appliedFilters={filters}
        />

        {error && (
          <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
            <p className="flex-1 text-sm text-red-200">
              {error?.message || error}
            </p>
            <button
              onClick={() => refetch()}
              className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
            >
              <RotateCcw size={14} /> Retry
            </button>
          </div>
        )}

        {/* KPI Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {isLoading
            ? Array.from({ length: 4 }).map((_, i) => <KPISkeleton key={i} />)
            : kpis && (
                <>
                  <KPICard
                    title="Global Churn Rate"
                    value={`${kpis.global_churn_rate?.rate ?? 0}%`}
                    subtitle={`${kpis.global_churn_rate?.churned || 0} / ${kpis.global_churn_rate?.total || 0}`}
                    icon={RotateCcw}
                    iconColor="#a12c7b"
                    iconBg="bg-red-500/10"
                  />
                  <KPICard
                    title="Monthly Churn"
                    value={`${kpis.monthly_churn_rate?.rate ?? 0}%`}
                    subtitle={`${kpis.monthly_churn_rate?.churned || 0} in period`}
                    icon={RotateCcw}
                    iconColor="#964219"
                    iconBg="bg-orange-500/10"
                  />
                  <KPICard
                    title="Avg Lifetime"
                    value={`${kpis.avg_lifetime_days?.avg_days ?? 0}d`}
                    subtitle={`Min: ${kpis.avg_lifetime_days?.min_days || 0}d`}
                    icon={RotateCcw}
                    iconColor="#01696f"
                    iconBg="bg-teal-500/10"
                  />
                  <KPICard
                    title="Voluntary Churn"
                    value={`${kpis.churn_breakdown?.voluntary?.rate ?? 0}%`}
                    subtitle={`Tech: ${kpis.churn_breakdown?.technical?.rate || 0}%`}
                    icon={RotateCcw}
                    iconColor="#7a7974"
                    iconBg="bg-slate-500/10"
                  />
                </>
              )}
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* Trend Chart */}
          <div className="rounded-xl border border-slate-700 bg-[#121820] p-6">
            <h2 className="text-sm font-semibold text-slate-100 mb-4">
              Daily Churn vs New
            </h2>
            {isLoading ? (
              <ChartSkeleton />
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={charts?.daily_trend || []}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="var(--color-border)"
                  />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="new_subs"
                    stroke={COLORS.new}
                    name="New"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="churned"
                    stroke={COLORS.churn}
                    name="Churned"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Voluntary vs Technical */}
          <div className="rounded-xl border border-slate-700 bg-[#121820] p-6">
            <h2 className="text-sm font-semibold text-slate-100 mb-4">
              Churn Type
            </h2>
            {isLoading ? (
              <ChartSkeleton />
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={[
                      {
                        name: "Voluntary",
                        value: kpis?.churn_breakdown?.voluntary?.count || 0,
                      },
                      {
                        name: "Technical",
                        value: kpis?.churn_breakdown?.technical?.count || 0,
                      },
                    ]}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    dataKey="value"
                    label={({ name, percent }) =>
                      `${name} ${(percent * 100).toFixed(1)}%`
                    }
                  >
                    <Cell fill={COLORS.churn} />
                    <Cell fill={COLORS.warning} />
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Reactivation after Churn */}
        <div className="space-y-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-100">
              Reactivation after Churn
            </h2>
            <p className="text-sm text-slate-400">
              Users who subscribed again after churn, overall and by service
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {reactivationKpisLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <KPISkeleton key={`reactivation-kpi-${i}`} />
              ))
            ) : (
              <>
                <KPICard
                  title="Reactivated Users"
                  value={(
                    reactivationKpis?.reactivated_users ?? 0
                  ).toLocaleString()}
                  subtitle="Unique churned users re-subscribed"
                  icon={RotateCcw}
                  iconColor="#01696f"
                  iconBg="bg-teal-500/10"
                />
                <KPICard
                  title="Reactivation Rate"
                  value={reactivationRateLabel}
                  subtitle="Reactivated / churned users"
                  icon={RotateCcw}
                  iconColor="#a12c7b"
                  iconBg="bg-red-500/10"
                />
                <KPICard
                  title="Avg Days to Re-subscribe"
                  value={`${Number(reactivationKpis?.avg_days_to_resubscribe ?? 0).toFixed(1)}d`}
                  subtitle="Delay between churn and resubscription"
                  icon={RotateCcw}
                  iconColor="#964219"
                  iconBg="bg-orange-500/10"
                />
                <KPICard
                  title="Recovered Revenue"
                  value={`$${Number(reactivationKpis?.recovered_revenue ?? 0).toLocaleString()}`}
                  subtitle="Post-reactivation successful billing"
                  icon={RotateCcw}
                  iconColor="#7a7974"
                  iconBg="bg-slate-500/10"
                />
              </>
            )}
          </div>

          {reactivationKpisError && (
            <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <AlertCircle size={18} className="text-red-400 flex-shrink-0" />
              <p className="text-sm text-red-200">{reactivationKpisError}</p>
            </div>
          )}

          <div className="rounded-xl border border-slate-700 bg-[#121820] p-6">
            <h3 className="text-sm font-semibold text-slate-100 mb-4">
              Reactivation by Service
            </h3>

            {reactivationByServiceLoading ? (
              <ChartSkeleton />
            ) : reactivationByServiceError ? (
              <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                <AlertCircle size={18} className="text-red-400 flex-shrink-0" />
                <p className="text-sm text-red-200">
                  {reactivationByServiceError}
                </p>
              </div>
            ) : reactivationChartData.length === 0 ? (
              <div className="h-56 flex items-center justify-center text-slate-400 text-sm border border-slate-800 rounded-lg">
                No reactivation data available for the selected period
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={reactivationChartData}
                  layout="vertical"
                  margin={{ top: 6, right: 24, left: 120, bottom: 6 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="var(--color-border)"
                  />
                  <XAxis
                    type="number"
                    tick={{ fontSize: 11, fill: "#94A3B8" }}
                  />
                  <YAxis
                    type="category"
                    dataKey="service_name"
                    width={120}
                    tick={{ fontSize: 11, fill: "#94A3B8" }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1E293B",
                      border: "1px solid #334155",
                      borderRadius: 8,
                    }}
                    formatter={(value, name, item) => {
                      if (name === "reactivated_users") {
                        const rate = Number(
                          item?.payload?.reactivation_rate ?? 0,
                        );
                        const rateLabel =
                          rate > 0 && rate < 1
                            ? rate.toFixed(2)
                            : rate.toFixed(1);
                        return [`${value}`, `Reactivated (${rateLabel}%)`];
                      }
                      return [value, name];
                    }}
                  />
                  <Bar
                    dataKey="reactivated_users"
                    fill={COLORS.new}
                    radius={[0, 6, 6, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            )}

            <p className="mt-3 text-xs text-slate-500">
              A reactivated user is a churned user who later subscribed again to
              the same service.
            </p>
          </div>
        </div>

        {/* Services & Distribution */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* By Service */}
          <div className="rounded-xl border border-slate-700 bg-[#121820] p-6">
            <h2 className="text-sm font-semibold text-slate-100 mb-4">
              Churn by Service
            </h2>
            {isLoading ? (
              <ChartSkeleton />
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart
                  data={charts?.by_service || []}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="var(--color-border)"
                  />
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis
                    dataKey="service_name"
                    type="category"
                    tick={{ fontSize: 11 }}
                  />
                  <Tooltip />
                  <Bar dataKey="churned" fill={COLORS.churn} name="Churned" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Distribution */}
          <div className="rounded-xl border border-slate-700 bg-[#121820] p-6">
            <h2 className="text-sm font-semibold text-slate-100 mb-4">
              Lifetime Distribution
            </h2>
            {isLoading ? (
              <ChartSkeleton />
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={charts?.lifetime_distribution || []}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="var(--color-border)"
                  />
                  <XAxis dataKey="bucket" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill={COLORS.new} name="Count" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Retention Table */}
        <div className="rounded-xl border border-slate-700 bg-[#121820] p-6">
          <h2 className="text-sm font-semibold text-slate-100 mb-4">
            Retention by Cohort
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400">
                    Cohort
                  </th>
                  <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400">
                    Users
                  </th>
                  <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400">
                    D+7
                  </th>
                  <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400">
                    D+14
                  </th>
                  <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400">
                    D+30
                  </th>
                </tr>
              </thead>
              <tbody>
                {(charts?.retention_cohort || []).map((row, i) => (
                  <tr
                    key={i}
                    className="border-b border-slate-700/50 hover:bg-slate-800/30"
                  >
                    <td className="py-3 px-4 text-slate-300">{row.cohort}</td>
                    <td className="text-right py-3 px-4 text-slate-300">
                      {(row.total || 0).toLocaleString()}
                    </td>
                    <td className="text-right py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${row.d7_rate >= 50 ? "bg-green-500/20 text-green-300" : row.d7_rate >= 25 ? "bg-yellow-500/20 text-yellow-300" : "bg-red-500/20 text-red-300"}`}
                      >
                        {row.d7_rate}%
                      </span>
                    </td>
                    <td className="text-right py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${row.d14_rate >= 50 ? "bg-green-500/20 text-green-300" : row.d14_rate >= 25 ? "bg-yellow-500/20 text-yellow-300" : "bg-red-500/20 text-red-300"}`}
                      >
                        {row.d14_rate}%
                      </span>
                    </td>
                    <td className="text-right py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${row.d30_rate >= 50 ? "bg-green-500/20 text-green-300" : row.d30_rate >= 25 ? "bg-yellow-500/20 text-yellow-300" : "bg-red-500/20 text-red-300"}`}
                      >
                        {row.d30_rate}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
