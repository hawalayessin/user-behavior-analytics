import { useMemo, useState } from "react";
import PropTypes from "prop-types";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const FALLBACK_DATA = [
  { service_name: "Esports by TT", subscriptions: 4200 },
  { service_name: "ElJournal by TT", subscriptions: 3100 },
  { service_name: "Tawer by TT", subscriptions: 1800 },
  { service_name: "Rafi9ni Plus", subscriptions: 950 },
];

const PIE_GRADIENTS = [
  ["#22c55e", "#16a34a"],
  ["#3b82f6", "#2563eb"],
  ["#a855f7", "#7e22ce"],
  ["#f59e0b", "#d97706"],
  ["#ef4444", "#dc2626"],
  ["#14b8a6", "#0f766e"],
];

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;

  const row = payload[0]?.payload;
  const metricLabel = row?.metric_label || "Subscriptions";
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 shadow-xl min-w-[180px]">
      <p className="text-xs text-slate-200 font-semibold mb-2">
        {row?.service_name}
      </p>
      <div className="space-y-1 text-xs">
        <div className="flex items-center justify-between gap-3">
          <span className="text-slate-400">{metricLabel}</span>
          <span className="text-slate-100 font-semibold">
            {Number(row?.subscriptions || 0).toLocaleString()}
          </span>
        </div>
        <div className="flex items-center justify-between gap-3">
          <span className="text-slate-400">Share</span>
          <span className="text-slate-100 font-semibold">
            {Number(row?.percent || 0).toFixed(1)}%
          </span>
        </div>
      </div>
    </div>
  );
}

function ServiceLegendList({ rows }) {
  if (!rows?.length) return null;

  const metricLabel = rows[0]?.metric_label || "subscriptions";

  return (
    <div className="w-full">
      <div className="space-y-1.5">
        {rows.map((row, index) => {
          const [start, end] = PIE_GRADIENTS[index % PIE_GRADIENTS.length];
          return (
            <div
              key={row.service_name}
              className="flex items-center justify-between gap-3 py-2.5 border-b border-slate-800/80 last:border-b-0"
            >
              <div className="min-w-0 flex items-center gap-2.5">
                <span
                  className="h-2.5 w-2.5 rounded-full flex-shrink-0"
                  style={{
                    background: `linear-gradient(135deg, ${start} 0%, ${end} 100%)`,
                  }}
                />
                <span
                  className="text-sm font-medium text-slate-100 leading-5 break-words"
                  title={row.service_name}
                >
                  {row.service_name}
                </span>
              </div>
              <div className="text-right flex-shrink-0 tabular-nums">
                <p className="text-sm text-slate-200 font-medium">
                  {row.subscriptions.toLocaleString()}{" "}
                  {metricLabel.toLowerCase()}
                </p>
                <p className="text-xs text-slate-400">
                  {row.percent.toFixed(1)}%
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function UserDistributionByServiceChart({ data }) {
  const [subscriptionMode, setSubscriptionMode] = useState("all");

  const normalized = useMemo(
    () =>
      (data?.length ? data : FALLBACK_DATA).map((item) => {
        const total = Number(item.subscriptions || 0);
        const active = Number(item.active_subscriptions || 0);
        return {
          service_name: item.service_name,
          total_subscriptions: total,
          active_subscriptions: Math.max(0, Math.min(active, total)),
          non_active_subscriptions: Math.max(total - active, 0),
        };
      }),
    [data],
  );

  const metricKey =
    subscriptionMode === "active"
      ? "active_subscriptions"
      : subscriptionMode === "inactive"
        ? "non_active_subscriptions"
        : "total_subscriptions";

  const metricLabel =
    subscriptionMode === "active"
      ? "Active Subscriptions"
      : subscriptionMode === "inactive"
        ? "Non-active Subscriptions"
        : "Total Subscriptions";

  const filtered = normalized
    .map((item) => ({
      service_name: item.service_name,
      subscriptions: Number(item[metricKey] || 0),
    }))
    .filter((item) => item.subscriptions > 0);

  const totalSubscriptions = filtered.reduce(
    (sum, item) => sum + item.subscriptions,
    0,
  );

  const chartData = filtered.map((item) => ({
    ...item,
    metric_label: metricLabel,
    percent:
      totalSubscriptions > 0
        ? (item.subscriptions * 100) / totalSubscriptions
        : 0,
  }));

  const topService = chartData[0]?.service_name;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 mt-4">
      <div className="flex items-center justify-between gap-4 mb-5">
        <div className="min-w-0">
          <h3 className="text-lg font-semibold text-slate-100">
            Subscription Distribution by Service
          </h3>
          <p className="text-sm text-slate-400 mt-1">
            Share of {metricLabel.toLowerCase()} by service
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setSubscriptionMode("all")}
            className={`px-2.5 py-1.5 rounded-md text-xs border transition ${
              subscriptionMode === "all"
                ? "bg-slate-700 border-slate-500 text-slate-100"
                : "bg-slate-800/70 border-slate-700 text-slate-300 hover:bg-slate-700/70"
            }`}
          >
            All
          </button>
          <button
            type="button"
            onClick={() => setSubscriptionMode("active")}
            className={`px-2.5 py-1.5 rounded-md text-xs border transition ${
              subscriptionMode === "active"
                ? "bg-green-900/60 border-green-600 text-green-100"
                : "bg-slate-800/70 border-slate-700 text-slate-300 hover:bg-slate-700/70"
            }`}
          >
            Active
          </button>
          <button
            type="button"
            onClick={() => setSubscriptionMode("inactive")}
            className={`px-2.5 py-1.5 rounded-md text-xs border transition ${
              subscriptionMode === "inactive"
                ? "bg-amber-900/50 border-amber-600 text-amber-100"
                : "bg-slate-800/70 border-slate-700 text-slate-300 hover:bg-slate-700/70"
            }`}
          >
            Non-active
          </button>
        </div>
        <div className="px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-800/60 text-right flex-shrink-0">
          <p className="text-[11px] uppercase tracking-wide text-slate-400">
            Services Active
          </p>
          <p className="text-lg leading-none font-semibold text-slate-100 mt-1">
            {chartData.length}
          </p>
          <p className="text-[11px] text-slate-400 mt-1.5">
            {metricLabel}: {totalSubscriptions.toLocaleString()}
          </p>
          {topService && (
            <p className="text-[11px] text-slate-500 mt-1.5">
              Top Service: {topService}
            </p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[42%_58%] gap-5 items-center">
        <div className="w-full h-[260px] sm:h-[280px] xl:h-[300px] flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <defs>
                {chartData.map((_, index) => {
                  const [start, end] =
                    PIE_GRADIENTS[index % PIE_GRADIENTS.length];
                  return (
                    <linearGradient
                      key={`pieGradient-${index}`}
                      id={`pieGradient${index}`}
                      x1="0"
                      y1="0"
                      x2="1"
                      y2="1"
                    >
                      <stop offset="0%" stopColor={start} stopOpacity={1} />
                      <stop offset="100%" stopColor={end} stopOpacity={0.85} />
                    </linearGradient>
                  );
                })}
              </defs>

              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={58}
                outerRadius={86}
                paddingAngle={3}
                dataKey="subscriptions"
                nameKey="service_name"
                stroke="var(--color-bg-primary)"
                strokeWidth={1.5}
              >
                {chartData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={`url(#pieGradient${index})`}
                  />
                ))}
              </Pie>

              <text
                x="50%"
                y="48%"
                textAnchor="middle"
                dominantBaseline="middle"
                className="fill-slate-400 text-xs"
              >
                {metricLabel}
              </text>
              <text
                x="50%"
                y="56%"
                textAnchor="middle"
                dominantBaseline="middle"
                className="fill-slate-100 text-base font-semibold"
              >
                {totalSubscriptions.toLocaleString()}
              </text>

              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="w-full xl:pl-1">
          <ServiceLegendList rows={chartData} />
        </div>
      </div>
    </div>
  );
}

ServiceLegendList.propTypes = {
  rows: PropTypes.arrayOf(
    PropTypes.shape({
      service_name: PropTypes.string,
      subscriptions: PropTypes.number,
      percent: PropTypes.number,
      metric_label: PropTypes.string,
    }),
  ),
};

UserDistributionByServiceChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      service_name: PropTypes.string,
      subscriptions: PropTypes.number,
      active_subscriptions: PropTypes.number,
    }),
  ),
};
