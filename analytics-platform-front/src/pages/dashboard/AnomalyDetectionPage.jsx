import React, { useMemo, useState } from "react";
import {
  AlertTriangle,
  Zap,
  Activity,
  Clock,
  Play,
  Download,
  ToggleRight,
} from "lucide-react";
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
  Scatter,
} from "recharts";

import AppLayout from "../../components/layout/AppLayout";
import FilterBar from "../../components/dashboard/FilterBar";
import { DEFAULT_ANALYTICS_FILTERS } from "../../constants/dateFilters";
import { useAnomalies } from "../../hooks/useAnomalies";

const THEME = {
  cardBg: "var(--color-bg-card)",
  border: "var(--color-border)",
  text: "var(--color-text-primary)",
  primary: "#3b82f6",
  green: "#22c55e",
  red: "#ef4444",
  orange: "#f97316",
  cyan: "#06b6d4",
  darkBg: "var(--color-bg-primary)",
};

const SEVERITY_COLORS = {
  critical: THEME.red,
  high: THEME.orange,
  medium: "#fbbf24",
};

const METRIC_COLORS = {
  dau: THEME.primary,
  churn_rate: THEME.red,
  revenue: THEME.green,
  renewals: THEME.cyan,
};

const METRIC_LABELS = {
  dau: "DAU",
  churn_rate: "Churn",
  revenue: "Revenue",
  renewals: "Renewals",
};

const DEFAULT_SEVERITY = ["critical", "high", "medium"];
const DEFAULT_METRICS = ["dau", "churn_rate", "revenue", "renewals"];

function toRelativeTime(value) {
  if (!value) return "—";
  const dt = new Date(value);
  if (Number.isNaN(dt.getTime())) return "—";
  const diffHours = Math.max(
    0,
    Math.floor((Date.now() - dt.getTime()) / 3600000),
  );
  if (diffHours < 1) return "<1h";
  if (diffHours < 24) return `${diffHours}h`;
  return `${Math.floor(diffHours / 24)}d`;
}

function formatMetricValue(metric, value) {
  const numeric = Number(value || 0);
  if (metric === "churn_rate") return `${numeric.toFixed(1)}%`;
  if (metric === "revenue")
    return `${Math.round(numeric).toLocaleString()} TND`;
  return Math.round(numeric).toLocaleString();
}

function severityBadgeStyle(severity) {
  const s = String(severity || "").toLowerCase();
  if (s === "critical") {
    return {
      bg: "rgba(239, 68, 68, 0.2)",
      color: THEME.red,
      label: "CRITICAL",
    };
  }
  if (s === "high") {
    return {
      bg: "rgba(249, 115, 22, 0.2)",
      color: THEME.orange,
      label: "HIGH",
    };
  }
  return {
    bg: "rgba(251, 191, 36, 0.2)",
    color: "#fbbf24",
    label: "MEDIUM",
  };
}

function getHeatmapColor(value) {
  if (value === 0) return "var(--color-bg-elevated)";
  if (value === 1) return "rgba(234, 179, 8, 0.28)";
  if (value === 2) return "rgba(249, 115, 22, 0.28)";
  return "rgba(239, 68, 68, 0.28)";
}

function getHeatmapLabel(value) {
  return "● ".repeat(value);
}

function TimelineTooltip({ active, payload, label }) {
  if (!active) return null;
  const row = payload?.[0]?.payload;

  return (
    <div
      className="rounded-lg p-3"
      style={{
        backgroundColor: THEME.darkBg,
        border: `1px solid ${THEME.border}`,
        minWidth: 240,
      }}
    >
      <p className="text-xs font-semibold mb-2" style={{ color: THEME.text }}>
        {label}
      </p>
      <div className="space-y-1">
        {(payload || [])
          .filter((p) => ["dau", "churn_rate", "revenue"].includes(p.dataKey))
          .map((entry) => (
            <div
              key={entry.dataKey}
              className="flex items-center justify-between text-xs"
            >
              <span style={{ color: "var(--color-text-muted)" }}>
                {METRIC_LABELS[entry.dataKey] || entry.name}
              </span>
              <span style={{ color: entry.color, fontWeight: 600 }}>
                {formatMetricValue(entry.dataKey, entry.value)}
              </span>
            </div>
          ))}
      </div>

      {(row?.anomalies || []).length > 0 && (
        <div
          className="mt-3 pt-2 border-t"
          style={{ borderColor: THEME.border }}
        >
          <p
            className="text-xs font-semibold mb-1"
            style={{ color: THEME.text }}
          >
            Anomalies
          </p>
          <div className="space-y-1">
            {row.anomalies.map((a) => (
              <p
                key={`${a.metric}-${a.z_score}-${a.date}`}
                className="text-[11px]"
                style={{ color: "var(--color-text-secondary)" }}
              >
                {a.service_name} • {METRIC_LABELS[a.metric] || a.metric} •{" "}
                {a.severity.toUpperCase()} • observed{" "}
                {formatMetricValue(a.metric, a.observed_value)} vs expected{" "}
                {formatMetricValue(a.metric, a.expected_value)} • z={a.z_score}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function AnomalyDetectionPage() {
  const [filters, setFilters] = useState(DEFAULT_ANALYTICS_FILTERS);
  const [showAutoRefresh, setShowAutoRefresh] = useState(true);
  const [expandedInsight, setExpandedInsight] = useState(null);
  const [page, setPage] = useState(1);
  const limit = 10;

  const selectedSeverity = DEFAULT_SEVERITY;
  const selectedMetrics = DEFAULT_METRICS;

  const {
    summary,
    timeline,
    distribution,
    heatmap,
    details,
    insights,
    errors,
    summaryLoading,
    timelineLoading,
    distributionLoading,
    heatmapLoading,
    detailsLoading,
    insightsLoading,
    runDetectionLoading,
    runDetection,
  } = useAnomalies({
    filters,
    severity: selectedSeverity,
    metrics: selectedMetrics,
    limit,
    offset: (page - 1) * limit,
  });

  const timelineRows = useMemo(() => {
    const map = new Map();
    (timeline?.series || []).forEach((serie) => {
      (serie.points || []).forEach((point) => {
        if (!map.has(point.date))
          map.set(point.date, { date: point.date, anomalies: [] });
        map.get(point.date)[serie.metric] = Number(point.value || 0);
      });
    });
    (timeline?.anomalies || []).forEach((anomaly) => {
      if (!map.has(anomaly.date))
        map.set(anomaly.date, { date: anomaly.date, anomalies: [] });
      map.get(anomaly.date).anomalies.push(anomaly);
    });

    return Array.from(map.values()).sort(
      (a, b) => new Date(a.date) - new Date(b.date),
    );
  }, [timeline]);

  const leftAnomalyPoints = useMemo(() => {
    return (timeline?.anomalies || [])
      .filter((a) => a.metric === "dau" || a.metric === "churn_rate")
      .map((a) => ({ ...a, y: Number(a.observed_value || 0) }));
  }, [timeline]);

  const rightAnomalyPoints = useMemo(() => {
    return (timeline?.anomalies || [])
      .filter((a) => a.metric === "revenue")
      .map((a) => ({ ...a, y: Number(a.observed_value || 0) }));
  }, [timeline]);

  const severityData = useMemo(() => {
    const sev = distribution?.severity_distribution || {};
    const total =
      Number(sev.critical || 0) +
      Number(sev.high || 0) +
      Number(sev.medium || 0);
    if (total === 0) return [];
    return [
      {
        name: "Critical",
        value: Math.round((Number(sev.critical || 0) * 1000) / total) / 10,
        fill: THEME.red,
      },
      {
        name: "High",
        value: Math.round((Number(sev.high || 0) * 1000) / total) / 10,
        fill: THEME.orange,
      },
      {
        name: "Medium",
        value: Math.round((Number(sev.medium || 0) * 1000) / total) / 10,
        fill: "#fbbf24",
      },
    ];
  }, [distribution]);

  const metricBarsData = useMemo(() => {
    const m = distribution?.metric_distribution || {};
    return [
      { metric: "DAU", count: Number(m.dau || 0), fill: THEME.primary },
      { metric: "Churn", count: Number(m.churn_rate || 0), fill: THEME.red },
      { metric: "Revenue", count: Number(m.revenue || 0), fill: THEME.green },
      { metric: "Renewals", count: Number(m.renewals || 0), fill: THEME.cyan },
    ];
  }, [distribution]);

  const maxMetricBar = Math.max(1, ...metricBarsData.map((i) => i.count || 0));
  const totalDetailsPages = Math.max(
    1,
    Math.ceil(Number(details?.total || 0) / limit),
  );

  const handleRunDetection = async () => {
    try {
      await runDetection();
    } catch {
      // section-level error is already handled by hook reloads
    }
  };

  return (
    <AppLayout pageTitle="Anomaly Detection — AI">
      <div className="space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold" style={{ color: THEME.text }}>
                Anomaly Detection — AI
              </h1>
              <span
                className="px-3 py-1 rounded-full text-xs font-semibold text-white"
                style={{ backgroundColor: THEME.cyan, color: "#000" }}
              >
                Z-Score + Isolation Forest
              </span>
            </div>
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              Z-Score + Isolation Forest detection (14-day rolling window)
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleRunDetection}
              disabled={runDetectionLoading}
              className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-white transition disabled:opacity-60"
              style={{ backgroundColor: THEME.primary }}
            >
              <Play size={16} />
              {runDetectionLoading ? "Running..." : "Run Detection"}
            </button>
            <button
              className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium border transition"
              style={{
                borderColor: THEME.border,
                color: THEME.text,
                backgroundColor: "transparent",
              }}
            >
              <Download size={16} />
              Export Report
            </button>
            <button
              onClick={() => setShowAutoRefresh(!showAutoRefresh)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition"
              style={{
                color: showAutoRefresh ? "white" : "var(--color-text-muted)",
                backgroundColor: showAutoRefresh
                  ? THEME.primary
                  : "transparent",
                borderColor: THEME.border,
                border: showAutoRefresh ? "none" : `1px solid ${THEME.border}`,
              }}
            >
              <ToggleRight size={16} />
              Auto-refresh: {showAutoRefresh ? "ON" : "OFF"}
            </button>
          </div>
        </div>

        <FilterBar
          onApply={(f) => {
            setPage(1);
            setFilters(f);
          }}
          defaultPeriod="all"
          appliedFilters={filters}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div
            className="p-5 rounded-lg border"
            style={{ backgroundColor: THEME.cardBg, borderColor: THEME.border }}
          >
            <div className="flex items-start justify-between mb-3">
              <h3
                className="text-sm font-semibold"
                style={{ color: "var(--color-text-muted)" }}
              >
                Anomalies Detected
              </h3>
              <div
                className="p-2 rounded-lg"
                style={{ backgroundColor: "rgba(239, 68, 68, 0.1)" }}
              >
                <AlertTriangle size={20} color={THEME.red} />
              </div>
            </div>
            {summaryLoading ? (
              <p
                className="text-lg"
                style={{ color: "var(--color-text-muted)" }}
              >
                Loading...
              </p>
            ) : (
              <>
                <p
                  className="text-3xl font-bold mb-1"
                  style={{ color: THEME.text }}
                >
                  {Number(summary?.anomalies_detected || 0)}
                </p>
                <p className="text-xs" style={{ color: THEME.red }}>
                  ({Number(summary?.trend_vs_previous || 0) >= 0 ? "+" : ""}
                  {Number(summary?.trend_vs_previous || 0)} vs last period)
                </p>
              </>
            )}
          </div>

          <div
            className="p-5 rounded-lg border"
            style={{ backgroundColor: THEME.cardBg, borderColor: THEME.border }}
          >
            <div className="flex items-start justify-between mb-3">
              <h3
                className="text-sm font-semibold"
                style={{ color: "var(--color-text-muted)" }}
              >
                Critical Alerts
              </h3>
              <div
                className="p-2 rounded-lg animate-pulse"
                style={{ backgroundColor: "rgba(239, 68, 68, 0.1)" }}
              >
                <Zap size={20} color={THEME.red} />
              </div>
            </div>
            {summaryLoading ? (
              <p
                className="text-lg"
                style={{ color: "var(--color-text-muted)" }}
              >
                Loading...
              </p>
            ) : (
              <>
                <p
                  className="text-3xl font-bold mb-1"
                  style={{ color: THEME.text }}
                >
                  {Number(summary?.critical_alerts || 0)}
                </p>
                <p
                  className="text-xs"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  ({Number(summary?.unresolved || 0)} unresolved)
                </p>
              </>
            )}
          </div>

          <div
            className="p-5 rounded-lg border"
            style={{ backgroundColor: THEME.cardBg, borderColor: THEME.border }}
          >
            <div className="flex items-start justify-between mb-3">
              <h3
                className="text-sm font-semibold"
                style={{ color: "var(--color-text-muted)" }}
              >
                Most Affected
              </h3>
              <div
                className="p-2 rounded-lg"
                style={{ backgroundColor: "rgba(249, 115, 22, 0.1)" }}
              >
                <Activity size={20} color={THEME.orange} />
              </div>
            </div>
            {summaryLoading ? (
              <p
                className="text-lg"
                style={{ color: "var(--color-text-muted)" }}
              >
                Loading...
              </p>
            ) : (
              <>
                <p
                  className="text-2xl font-bold mb-1 truncate"
                  style={{ color: THEME.text }}
                >
                  {summary?.most_affected_service?.name || "N/A"}
                </p>
                <p
                  className="text-xs"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  {Number(summary?.most_affected_service?.anomaly_count || 0)}{" "}
                  anomalies
                </p>
                <p
                  className="text-xs mt-1"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  Next: {summary?.last_detection?.next_run ? "24h" : "—"}
                </p>
              </>
            )}
          </div>

          <div
            className="p-5 rounded-lg border"
            style={{ backgroundColor: THEME.cardBg, borderColor: THEME.border }}
          >
            <div className="flex items-start justify-between mb-3">
              <h3
                className="text-sm font-semibold"
                style={{ color: "var(--color-text-muted)" }}
              >
                Last Detection
              </h3>
              <div
                className="p-2 rounded-lg"
                style={{ backgroundColor: "rgba(6, 182, 212, 0.1)" }}
              >
                <Clock size={20} color={THEME.cyan} />
              </div>
            </div>
            {summaryLoading ? (
              <p
                className="text-lg"
                style={{ color: "var(--color-text-muted)" }}
              >
                Loading...
              </p>
            ) : (
              <>
                <p
                  className="text-3xl font-bold mb-1"
                  style={{ color: THEME.text }}
                >
                  {toRelativeTime(summary?.last_detection?.run_at)}
                </p>
                <p
                  className="text-xs"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  ago
                </p>
              </>
            )}
          </div>
        </div>

        <div
          className="p-6 rounded-lg border"
          style={{ backgroundColor: THEME.cardBg, borderColor: THEME.border }}
        >
          <h2
            className="text-sm font-semibold mb-4"
            style={{ color: THEME.text }}
          >
            Anomaly Timeline — DAU, Churn, Revenue
          </h2>
          {errors.timeline ? (
            <p className="text-sm text-red-400">Unable to load anomaly data</p>
          ) : timelineLoading ? (
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              Loading timeline...
            </p>
          ) : timelineRows.length === 0 ? (
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              No anomalies detected for the selected filters
            </p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timelineRows}>
                <CartesianGrid strokeDasharray="3 3" stroke={THEME.border} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11, fill: THEME.text }}
                  stroke={THEME.border}
                />
                <YAxis
                  yAxisId="left"
                  tick={{ fontSize: 11, fill: THEME.text }}
                  stroke={THEME.border}
                />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  tick={{ fontSize: 11, fill: THEME.text }}
                  stroke={THEME.border}
                />
                <Tooltip content={<TimelineTooltip />} />
                <Legend
                  wrapperStyle={{ paddingTop: "20px", color: THEME.text }}
                />

                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="dau"
                  stroke={THEME.primary}
                  name="DAU"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="churn_rate"
                  stroke={THEME.red}
                  name="Churn %"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="revenue"
                  stroke={THEME.green}
                  name="Revenue"
                  strokeWidth={2}
                  dot={false}
                />

                <Scatter
                  yAxisId="left"
                  data={leftAnomalyPoints}
                  dataKey="y"
                  name="Anomalies"
                  shape="diamond"
                  fill={THEME.orange}
                >
                  {leftAnomalyPoints.map((a, idx) => (
                    <Cell
                      key={`la-${idx}`}
                      fill={SEVERITY_COLORS[a.severity] || THEME.orange}
                    />
                  ))}
                </Scatter>
                <Scatter
                  yAxisId="right"
                  data={rightAnomalyPoints}
                  dataKey="y"
                  shape="diamond"
                  fill={THEME.orange}
                >
                  {rightAnomalyPoints.map((a, idx) => (
                    <Cell
                      key={`ra-${idx}`}
                      fill={SEVERITY_COLORS[a.severity] || THEME.orange}
                    />
                  ))}
                </Scatter>
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div
            className="lg:col-span-2 p-6 rounded-lg border"
            style={{ backgroundColor: THEME.cardBg, borderColor: THEME.border }}
          >
            <h2
              className="text-sm font-semibold mb-4"
              style={{ color: THEME.text }}
            >
              Anomalies Heatmap — Service / Week
            </h2>
            {errors.heatmap ? (
              <p className="text-sm text-red-400">
                Unable to load anomaly data
              </p>
            ) : heatmapLoading ? (
              <p
                className="text-sm"
                style={{ color: "var(--color-text-muted)" }}
              >
                Loading heatmap...
              </p>
            ) : (heatmap?.services || []).length === 0 ? (
              <p
                className="text-sm"
                style={{ color: "var(--color-text-muted)" }}
              >
                No anomalies detected for the selected filters
              </p>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr style={{ borderBottomColor: THEME.border }}>
                        <th
                          className="text-left py-3 px-2 font-semibold"
                          style={{ color: "var(--color-text-muted)" }}
                        >
                          Service
                        </th>
                        {(heatmap.weeks || []).map((w) => (
                          <th
                            key={w}
                            className="text-center py-3 px-2 font-semibold"
                            style={{ color: "var(--color-text-muted)" }}
                          >
                            {w}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(heatmap.services || []).map((row) => {
                        const cellByWeek = new Map(
                          (row.cells || []).map((c) => [c.week, c]),
                        );
                        return (
                          <tr
                            key={row.service_name}
                            style={{ borderBottomColor: THEME.border }}
                          >
                            <td
                              className="py-3 px-2 font-medium"
                              style={{ color: THEME.text }}
                            >
                              {row.service_name}
                            </td>
                            {(heatmap.weeks || []).map((w) => {
                              const cell = cellByWeek.get(w) || {
                                severity_score: 0,
                                count: 0,
                              };
                              return (
                                <td
                                  key={`${row.service_name}-${w}`}
                                  className="text-center py-3 px-2 rounded"
                                  style={{
                                    color: THEME.text,
                                    backgroundColor: getHeatmapColor(
                                      cell.severity_score,
                                    ),
                                  }}
                                  title={`${cell.count} anomalies`}
                                >
                                  {getHeatmapLabel(cell.severity_score)}
                                </td>
                              );
                            })}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                <p
                  className="text-xs mt-4"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  ● = Medium | ●● = High | ●●● = Critical
                </p>
              </>
            )}
          </div>

          <div className="space-y-6">
            <div
              className="p-6 rounded-lg border"
              style={{
                backgroundColor: THEME.cardBg,
                borderColor: THEME.border,
              }}
            >
              <h3
                className="text-sm font-semibold mb-4"
                style={{ color: THEME.text }}
              >
                Severity Distribution
              </h3>
              {errors.distribution ? (
                <p className="text-sm text-red-400">
                  Unable to load anomaly data
                </p>
              ) : distributionLoading ? (
                <p
                  className="text-sm"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  Loading distribution...
                </p>
              ) : severityData.length === 0 ? (
                <p
                  className="text-sm"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  No anomalies detected for the selected filters
                </p>
              ) : (
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={severityData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value }) => `${name} ${value}%`}
                    >
                      {severityData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: THEME.darkBg,
                        borderColor: THEME.border,
                      }}
                      labelStyle={{ color: THEME.text }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>

            <div
              className="p-6 rounded-lg border"
              style={{
                backgroundColor: THEME.cardBg,
                borderColor: THEME.border,
              }}
            >
              <h3
                className="text-sm font-semibold mb-4"
                style={{ color: THEME.text }}
              >
                Anomalies by Metric
              </h3>
              {errors.distribution ? (
                <p className="text-sm text-red-400">
                  Unable to load anomaly data
                </p>
              ) : distributionLoading ? (
                <p
                  className="text-sm"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  Loading metrics...
                </p>
              ) : (
                <div className="space-y-3">
                  {metricBarsData.map((item) => (
                    <div key={item.metric}>
                      <div className="flex justify-between mb-1">
                        <span
                          className="text-xs font-medium"
                          style={{ color: "var(--color-text-muted)" }}
                        >
                          {item.metric}
                        </span>
                        <span
                          className="text-xs font-semibold"
                          style={{ color: item.fill }}
                        >
                          {item.count}
                        </span>
                      </div>
                      <div
                        className="w-full h-2 rounded"
                        style={{ backgroundColor: THEME.border }}
                      >
                        <div
                          className="h-full rounded transition-all"
                          style={{
                            width: `${(item.count / maxMetricBar) * 100}%`,
                            backgroundColor: item.fill,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <div
          className="p-6 rounded-lg border"
          style={{ backgroundColor: THEME.cardBg, borderColor: THEME.border }}
        >
          <h2
            className="text-sm font-semibold mb-4"
            style={{ color: THEME.text }}
          >
            Detected Anomalies
          </h2>
          {errors.details ? (
            <p className="text-sm text-red-400">Unable to load anomaly data</p>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr style={{ borderBottomColor: THEME.border }}>
                      <th
                        className="text-left py-3 px-4 font-semibold"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        Severity
                      </th>
                      <th
                        className="text-left py-3 px-4 font-semibold"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        Date
                      </th>
                      <th
                        className="text-left py-3 px-4 font-semibold"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        Service
                      </th>
                      <th
                        className="text-left py-3 px-4 font-semibold"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        Metric
                      </th>
                      <th
                        className="text-left py-3 px-4 font-semibold"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        Observed
                      </th>
                      <th
                        className="text-left py-3 px-4 font-semibold"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        Expected
                      </th>
                      <th
                        className="text-left py-3 px-4 font-semibold"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        Z-Score
                      </th>
                      <th
                        className="text-left py-3 px-4 font-semibold"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        Status
                      </th>
                      <th
                        className="text-left py-3 px-4 font-semibold"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        Action
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {detailsLoading ? (
                      <tr>
                        <td
                          colSpan={9}
                          className="py-8 px-4"
                          style={{ color: "var(--color-text-muted)" }}
                        >
                          Loading anomalies...
                        </td>
                      </tr>
                    ) : (details?.items || []).length === 0 ? (
                      <tr>
                        <td
                          colSpan={9}
                          className="py-8 px-4"
                          style={{ color: "var(--color-text-muted)" }}
                        >
                          No anomalies detected for the selected filters
                        </td>
                      </tr>
                    ) : (
                      (details.items || []).map((row, idx) => {
                        const sev = severityBadgeStyle(row.severity);
                        const statusNorm = String(
                          row.status || "open",
                        ).toLowerCase();
                        const statusColor =
                          statusNorm === "open"
                            ? THEME.red
                            : statusNorm.includes("invest")
                              ? THEME.orange
                              : THEME.green;
                        const statusBg =
                          statusNorm === "open"
                            ? "rgba(239, 68, 68, 0.1)"
                            : statusNorm.includes("invest")
                              ? "rgba(249, 115, 22, 0.1)"
                              : "rgba(34, 197, 94, 0.1)";

                        return (
                          <tr
                            key={row.id}
                            style={{
                              borderBottomColor: THEME.border,
                              backgroundColor:
                                idx % 2
                                  ? "transparent"
                                  : "var(--color-bg-elevated)",
                            }}
                          >
                            <td className="py-3 px-4">
                              <span
                                className="px-2 py-1 rounded text-xs font-semibold"
                                style={{
                                  backgroundColor: sev.bg,
                                  color: sev.color,
                                }}
                              >
                                {sev.label === "CRITICAL" && (
                                  <Zap size={12} className="inline mr-1" />
                                )}
                                {sev.label}
                              </span>
                            </td>
                            <td
                              className="py-3 px-4"
                              style={{ color: THEME.text }}
                            >
                              {row.detection_date}
                            </td>
                            <td
                              className="py-3 px-4"
                              style={{ color: THEME.text }}
                            >
                              {row.service_name}
                            </td>
                            <td
                              className="py-3 px-4"
                              style={{ color: THEME.text }}
                            >
                              {METRIC_LABELS[row.metric] || row.metric}
                            </td>
                            <td
                              className="py-3 px-4"
                              style={{ color: THEME.red }}
                            >
                              {formatMetricValue(
                                row.metric,
                                row.observed_value,
                              )}
                            </td>
                            <td
                              className="py-3 px-4"
                              style={{ color: THEME.green }}
                            >
                              {formatMetricValue(
                                row.metric,
                                row.expected_value,
                              )}
                            </td>
                            <td
                              className="py-3 px-4"
                              style={{ color: THEME.cyan }}
                            >
                              {Number(row.z_score || 0) > 0 ? "↑" : "↓"}{" "}
                              {Math.abs(Number(row.z_score || 0)).toFixed(2)}
                            </td>
                            <td className="py-3 px-4">
                              <span
                                className="px-2 py-1 rounded text-xs font-medium"
                                style={{
                                  backgroundColor: statusBg,
                                  color: statusColor,
                                }}
                              >
                                {String(row.status || "open")}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <button
                                className="px-3 py-1 rounded text-xs font-medium border transition hover:opacity-80"
                                style={{
                                  borderColor: THEME.primary,
                                  color: THEME.primary,
                                  backgroundColor: "transparent",
                                }}
                              >
                                Analyze
                              </button>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>

              <div className="flex items-center justify-between mt-4">
                <p
                  className="text-xs"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  Total: {Number(details?.total || 0)} anomalies
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page <= 1}
                    className="px-3 py-1 rounded border text-xs disabled:opacity-50"
                    style={{ borderColor: THEME.border, color: THEME.text }}
                  >
                    Prev
                  </button>
                  <span
                    className="text-xs"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    {page} / {totalDetailsPages}
                  </span>
                  <button
                    onClick={() =>
                      setPage((p) => Math.min(totalDetailsPages, p + 1))
                    }
                    disabled={page >= totalDetailsPages}
                    className="px-3 py-1 rounded border text-xs disabled:opacity-50"
                    style={{ borderColor: THEME.border, color: THEME.text }}
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          )}
        </div>

        <div>
          <h2
            className="text-sm font-semibold mb-4"
            style={{ color: THEME.text }}
          >
            AI Insights & Recommendations
          </h2>
          {errors.insights ? (
            <p className="text-sm text-red-400">Unable to load anomaly data</p>
          ) : insightsLoading ? (
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              Loading insights...
            </p>
          ) : (insights?.items || []).length === 0 ? (
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
              No anomalies detected for the selected filters
            </p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {(insights.items || []).map((insight, idx) => {
                const color =
                  insight.type === "critical"
                    ? THEME.red
                    : insight.type === "warning"
                      ? THEME.orange
                      : THEME.primary;
                const Icon = insight.type === "info" ? Activity : AlertTriangle;
                const id = idx + 1;
                return (
                  <div
                    key={id}
                    className="p-4 rounded-lg border cursor-pointer transition"
                    style={{
                      backgroundColor: THEME.cardBg,
                      borderColor: THEME.border,
                      borderLeftWidth: "4px",
                      borderLeftColor: color,
                    }}
                    onClick={() =>
                      setExpandedInsight(expandedInsight === id ? null : id)
                    }
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className="p-2 rounded-lg flex-shrink-0"
                        style={{ backgroundColor: `${color}20` }}
                      >
                        <Icon size={16} color={color} />
                      </div>
                      <div className="flex-1">
                        <h3
                          className="text-sm font-semibold mb-1"
                          style={{ color }}
                        >
                          {insight.title}
                        </h3>
                        <p
                          className="text-xs"
                          style={{ color: "var(--color-text-muted)" }}
                        >
                          {insight.body}
                        </p>
                        {expandedInsight === id && insight.action_label && (
                          <p
                            className="text-xs mt-2"
                            style={{ color: "var(--color-accent)" }}
                          >
                            {insight.action_label}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div
          className="text-center py-8 text-sm"
          style={{ color: "var(--color-text-muted)" }}
        >
          💡 Tip: Use "Run Detection" to refresh anomaly analysis with latest
          data
        </div>
      </div>
    </AppLayout>
  );
}
