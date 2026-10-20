import React, { useState } from "react";
import { AlertCircle, RotateCcw, TrendingDown } from "lucide-react";
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

import FilterBar from "../../components/dashboard/FilterBar";
import KPICard from "../../components/dashboard/KPICard";
import PeakEvidenceCard from "../../components/dashboard/PeakEvidenceCard";
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
  <div
    className="w-full h-28 animate-pulse rounded-xl"
    style={{
      backgroundColor: "var(--color-bg-elevated)",
      border: "1px solid var(--color-border)",
    }}
  />
);
const ChartSkeleton = () => (
  <div
    className="w-full h-80 animate-pulse rounded-xl"
    style={{
      backgroundColor: "var(--color-bg-elevated)",
      border: "1px solid var(--color-border)",
    }}
  />
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
  const peakInsights = React.useMemo(() => {
    const dailyPeak = (charts?.daily_trend ?? []).reduce(
      (max, row) => (Number(row.churned ?? 0) > Number(max?.churned ?? -1) ? row : max),
      null,
    );
    const servicePeak = (charts?.by_service ?? []).reduce(
      (max, row) => (Number(row.churned ?? 0) > Number(max?.churned ?? -1) ? row : max),
      null,
    );
    const curvePeak = (charts?.churn_curve ?? []).reduce(
      (max, row) => (Number(row.trial ?? 0) > Number(max?.trial ?? -1) ? row : max),
      null,
    );
    return { dailyPeak, servicePeak, curvePeak };
  }, [charts?.by_service, charts?.churn_curve, charts?.daily_trend]);

  return (
    <div className="space-y-6">
      <div>
        <h1
          className="text-3xl font-bold mb-2"
          style={{ color: "var(--color-text-primary)" }}
        >
          Churn Analysis
        </h1>
        <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
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
          <p
            className="flex-1 text-sm"
            style={{ color: "var(--color-danger-text)" }}
          >
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
	      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4">
        {isLoading
          ? Array.from({ length: 5 }).map((_, i) => <KPISkeleton key={i} />)
          : kpis && (
              <>
                <KPICard
                  title="Historical Churn Rate"
                  value={`${Number(kpis.global_churn_rate?.rate ?? 0).toFixed(2)}%`}
                  subtitle={`${(kpis.global_churn_rate?.churned || 0).toLocaleString()} cancelled/expired / ${(kpis.global_churn_rate?.total || 0).toLocaleString()} total subs`}
                  icon={RotateCcw}
                  iconColor="#a12c7b"
                  iconBg="bg-red-500/10"
                />
                <KPICard
                  title="30-Day Churn Rate"
                  value={`${Number(kpis.monthly_churn_rate?.rate ?? 0).toFixed(1)}%`}
                  subtitle={`${(kpis.monthly_churn_rate?.churned || 0).toLocaleString()} churned / ${(kpis.monthly_churn_rate?.total || 0).toLocaleString()} exposed subs`}
                  icon={RotateCcw}
                  iconColor="#a12c7b"
                  iconBg="bg-red-500/10"
                />
                <KPICard
                  title="Trial Share of Churn"
                  value={`${Number(kpis.trial_churn?.rate ?? 0).toFixed(1)}%`}
                  subtitle={`${(kpis.trial_churn?.count || 0).toLocaleString()} trial churns / ${(kpis.trial_churn?.total || 0).toLocaleString()} churns`}
                  icon={RotateCcw}
                  iconColor="#964219"
                  iconBg="bg-orange-500/10"
                  alert={(kpis.trial_churn?.rate ?? 0) >= 40}
                />
                <KPICard
                  title="AVG TIME TO CHURN"
                  value={`${kpis.avg_lifetime_days?.avg_days ?? 0}d`}
                  subtitle="Average duration before churn"
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
                  iconBg="bg-gray-500/10"
                />
              </>
	            )}
	      </div>

	      {!isLoading && kpis && (
	        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
	          <PeakEvidenceCard
	            title="Peak Churn Day"
	            value={(peakInsights.dailyPeak?.churned ?? 0).toLocaleString()}
	            subtitle={peakInsights.dailyPeak?.date ?? "Selected period"}
	            icon={TrendingDown}
	            accent="rose"
	          />
	          <PeakEvidenceCard
	            title="Most Affected Service"
	            value={(peakInsights.servicePeak?.churned ?? 0).toLocaleString()}
	            subtitle={peakInsights.servicePeak?.service_name ?? "No service data"}
	            icon={RotateCcw}
	            accent="amber"
	          />
	          <PeakEvidenceCard
	            title="Peak Trial Churn Curve"
	            value={`${Number(peakInsights.curvePeak?.trial ?? 0).toFixed(1)}%`}
	            subtitle={`Day ${peakInsights.curvePeak?.day ?? "?"}`}
	            icon={TrendingDown}
	            accent="violet"
	          />
	        </div>
	      )}

	      {/* Charts Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Trend Chart */}
        <div
          className="rounded-xl p-6"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            boxShadow: "var(--color-card-shadow)",
          }}
        >
          <h2
            className="text-sm font-semibold mb-4"
            style={{ color: "var(--color-text-primary)" }}
          >
            Churn Curve
          </h2>
          {isLoading ? (
            <ChartSkeleton />
          ) : (
            <>
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={charts?.churn_curve || []}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="var(--color-border)"
                  />
                  <XAxis
                    dataKey="label"
                    tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
                    axisLine={{ stroke: "var(--chart-grid)" }}
                    tickLine={{ stroke: "var(--chart-grid)" }}
                  />
                  <YAxis
                    domain={[0, 100]}
                    tickFormatter={(v) => `${v}%`}
                    tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
                    axisLine={{ stroke: "var(--chart-grid)" }}
                    tickLine={{ stroke: "var(--chart-grid)" }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "var(--chart-tooltip-bg)",
                      border: "1px solid var(--chart-tooltip-border)",
                      borderRadius: "8px",
                      color: "var(--color-text-primary)",
                    }}
                    labelStyle={{ color: "var(--color-text-secondary)" }}
                    itemStyle={{ color: "var(--color-text-muted)" }}
                  />
                  <Legend
                    formatter={(value) => (
                      <span style={{ color: "var(--color-text-muted)" }}>
                        {value}
                      </span>
                    )}
                  />
                  <Line
                    type="monotone"
                    dataKey="trial"
                    stroke="#f2a9a0"
                    name="Trial"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="paid"
                    stroke="#efb37a"
                    name="Paid"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
              <p
                className="text-xs italic mt-3"
                style={{ color: "var(--color-text-muted)" }}
              >
                {charts?.churn_curve_note ||
                  "Cumulative churn split between Trial and Paid users."}
              </p>
            </>
          )}
        </div>

        {/* Voluntary vs Technical */}
        <div
          className="rounded-xl p-6"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            boxShadow: "var(--color-card-shadow)",
          }}
        >
          <h2
            className="text-sm font-semibold mb-4"
            style={{ color: "var(--color-text-primary)" }}
          >
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
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--chart-tooltip-bg)",
                    border: "1px solid var(--chart-tooltip-border)",
                    borderRadius: "8px",
                    color: "var(--color-text-primary)",
                  }}
                  labelStyle={{ color: "var(--color-text-secondary)" }}
                  itemStyle={{ color: "var(--color-text-muted)" }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Reactivation after Churn */}
      <div className="space-y-4">
        <div>
          <h2
            className="text-lg font-semibold"
            style={{ color: "var(--color-text-primary)" }}
          >
            Reactivation after Churn
          </h2>
          <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
            Same-service reactivation: users who churned then subscribed again to
            the identical service (not cross-service migration)
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
                subtitle="Unique users who re-subscribed to the same service"
                icon={RotateCcw}
                iconColor="#01696f"
                iconBg="bg-teal-500/10"
              />
              <KPICard
                title="Reactivation Rate"
                value={reactivationRateLabel}
                subtitle="Same-service reactivated / churned users in period"
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
                value={`${Number(reactivationKpis?.recovered_revenue ?? 0).toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })} TND`}
                subtitle="Successful billing on the reactivation subscription"
                icon={RotateCcw}
                iconColor="#7a7974"
                iconBg="bg-gray-500/10"
              />
            </>
          )}
        </div>

        {reactivationKpisError && (
          <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle size={18} className="text-red-400 flex-shrink-0" />
            <p
              className="text-sm"
              style={{ color: "var(--color-danger-text)" }}
            >
              {reactivationKpisError}
            </p>
          </div>
        )}

        <div
          className="rounded-xl p-6"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            boxShadow: "var(--color-card-shadow)",
          }}
        >
          <h3
            className="text-sm font-semibold mb-4"
            style={{ color: "var(--color-text-primary)" }}
          >
            Reactivation by Service
          </h3>

          {reactivationByServiceLoading ? (
            <ChartSkeleton />
          ) : reactivationByServiceError ? (
            <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <AlertCircle size={18} className="text-red-400 flex-shrink-0" />
              <p
                className="text-sm"
                style={{ color: "var(--color-danger-text)" }}
              >
                {reactivationByServiceError}
              </p>
            </div>
          ) : reactivationChartData.length === 0 ? (
            <div
              className="h-56 flex items-center justify-center text-sm rounded-lg"
              style={{
                color: "var(--color-text-muted)",
                border: "1px solid var(--color-border)",
              }}
            >
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
                  tick={{ fontSize: 11, fill: "var(--chart-axis-text)" }}
                  axisLine={{ stroke: "var(--chart-grid)" }}
                  tickLine={{ stroke: "var(--chart-grid)" }}
                />
                <YAxis
                  type="category"
                  dataKey="service_name"
                  width={120}
                  tick={{ fontSize: 11, fill: "var(--chart-axis-text)" }}
                  axisLine={{ stroke: "var(--chart-grid)" }}
                  tickLine={{ stroke: "var(--chart-grid)" }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--chart-tooltip-bg)",
                    border: "1px solid var(--chart-tooltip-border)",
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

          <p
            className="mt-3 text-xs"
            style={{ color: "var(--color-text-muted)" }}
          >
            A reactivated user churned in the selected period, then started a
            new subscription to the same service (distinct from cross-service
            migration paths).
          </p>
        </div>
      </div>

      {/* Services & Distribution */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* By Service */}
        <div
          className="rounded-xl p-6"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            boxShadow: "var(--color-card-shadow)",
          }}
        >
          <h2
            className="text-sm font-semibold mb-4"
            style={{ color: "var(--color-text-primary)" }}
          >
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
                <XAxis
                  type="number"
                  tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
                  axisLine={{ stroke: "var(--chart-grid)" }}
                  tickLine={{ stroke: "var(--chart-grid)" }}
                />
                <YAxis
                  dataKey="service_name"
                  type="category"
                  tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
                  axisLine={{ stroke: "var(--chart-grid)" }}
                  tickLine={{ stroke: "var(--chart-grid)" }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--chart-tooltip-bg)",
                    border: "1px solid var(--chart-tooltip-border)",
                    borderRadius: "8px",
                    color: "var(--color-text-primary)",
                  }}
                  labelStyle={{ color: "var(--color-text-secondary)" }}
                  itemStyle={{ color: "var(--color-text-muted)" }}
                />
                <Bar dataKey="churned" fill={COLORS.churn} name="Churned" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Distribution */}
        <div
          className="rounded-xl p-6"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            boxShadow: "var(--color-card-shadow)",
          }}
        >
          <h2
            className="text-sm font-semibold mb-4"
            style={{ color: "var(--color-text-primary)" }}
          >
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
                <XAxis
                  dataKey="bucket"
                  tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
                  axisLine={{ stroke: "var(--chart-grid)" }}
                  tickLine={{ stroke: "var(--chart-grid)" }}
                />
                <YAxis
                  tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
                  axisLine={{ stroke: "var(--chart-grid)" }}
                  tickLine={{ stroke: "var(--chart-grid)" }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--chart-tooltip-bg)",
                    border: "1px solid var(--chart-tooltip-border)",
                    borderRadius: "8px",
                    color: "var(--color-text-primary)",
                  }}
                  labelStyle={{ color: "var(--color-text-secondary)" }}
                  itemStyle={{ color: "var(--color-text-muted)" }}
                />
                <Bar dataKey="count" fill={COLORS.new} name="Count" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

    </div>
  );
}
