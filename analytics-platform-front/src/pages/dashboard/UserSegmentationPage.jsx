import React, { useState, useMemo } from "react";
import { AlertCircle, RotateCcw, Download } from "lucide-react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  Radar,
  PolarAngleAxis,
  PolarGrid,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LabelList,
} from "recharts";

import FilterBar from "../../components/dashboard/FilterBar";
import KPICard from "../../components/dashboard/KPICard";
import BIInsightsPanel from "../../components/dashboard/BIInsightsPanel";
import { useSegmentationKPIs } from "../../hooks/useSegmentationKPIs";
import { useSegmentationClusters } from "../../hooks/useSegmentationClusters";
import { useSegmentationProfiles } from "../../hooks/useSegmentationProfiles";
import { DEFAULT_ANALYTICS_FILTERS } from "../../constants/dateFilters";

const SEGMENT_COLORS = {
  "Power Users": "#3b82f6",
  "Regular Loyals": "#22c55e",
  "Occasional Users": "#f97316",
  "Trial Only": "#ef4444",
};

const SEGMENT_ALIASES = {
  "Power Users": "Power",
  "Regular Loyals": "Regular",
  "Occasional Users": "Occasional",
  "Trial Only": "Trial",
};

const SEGMENT_FALLBACK_POSITIONS = {
  "Power Users": { x: 0.74, y: 0.78 },
  "Regular Loyals": { x: 0.56, y: 0.5 },
  "Occasional Users": { x: 0.2, y: 0.52 },
  "Trial Only": { x: 0.2, y: 0.3 },
};

const SEGMENT_LABEL_OFFSETS = {
  "Power Users": { dx: 36, dy: -38 },
  "Regular Loyals": { dx: 34, dy: 8 },
  "Occasional Users": { dx: 30, dy: -36 },
  "Trial Only": { dx: 34, dy: 40 },
};

const formatCompactNumber = (value) => {
  const number = Number(value || 0);
  if (number >= 1_000_000) return `${(number / 1_000_000).toFixed(1)}M`;
  if (number >= 1_000) return `${Math.round(number / 1_000)}K`;
  return number.toLocaleString();
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

const ChartContainerCard = ({
  title,
  children,
  demoData = false,
  loading = false,
}) => (
  <div
    className="rounded-xl p-6"
    style={{
      border: "1px solid var(--color-border)",
      backgroundColor: "var(--color-bg-card)",
      boxShadow: "var(--color-card-shadow)",
    }}
  >
    <div className="flex items-center justify-between mb-4">
      <h2
        className="text-sm font-semibold"
        style={{ color: "var(--color-text-primary)" }}
      >
        {title}
      </h2>
      {demoData && (
        <span
          className="text-xs italic"
          style={{ color: "var(--color-text-muted)" }}
        >
          Demo Data
        </span>
      )}
    </div>
    {loading ? <ChartSkeleton /> : children}
  </div>
);

export default function UserSegmentationPage() {
  const [filters, setFilters] = useState(DEFAULT_ANALYTICS_FILTERS);

  const {
    data: kpiData,
    loading: kpiLoading,
    error: kpiError,
    refetch: refetchKPIs,
  } = useSegmentationKPIs(filters);
  const {
    data: clusterData,
    loading: clusterLoading,
    error: clusterError,
    refetch: refetchClusters,
  } = useSegmentationClusters(filters);
  const {
    data: profileData,
    loading: profileLoading,
    error: profileError,
    refetch: refetchProfiles,
  } = useSegmentationProfiles(filters);

  const kpis = useMemo(() => {
    return (
      kpiData ?? {
        total_segments: 0,
        dominant_segment: "—",
        dominant_pct: 0,
        high_value_segment: "—",
        arpu_premium: 0,
        risk_segment: "—",
        risk_churn_rate: 0,
      }
    );
  }, [kpiData]);

  const clusterPoints = useMemo(() => {
    return clusterData?.clusters ?? [];
  }, [clusterData]);

  const clusterPointsBySegment = useMemo(() => {
    const grouped = {
      "Power Users": [],
      "Regular Loyals": [],
      "Occasional Users": [],
      "Trial Only": [],
    };
    for (const point of clusterPoints) {
      const segment = point?.segment;
      if (grouped[segment]) grouped[segment].push(point);
    }
    return grouped;
  }, [clusterPoints]);

  const distribution = useMemo(() => {
    return clusterData?.distribution ?? [];
  }, [clusterData]);

  const profiles = useMemo(() => {
    return profileData?.profiles ?? [];
  }, [profileData]);

  const handleExport = () => {
    const data = {
      kpis,
      distribution,
      profiles,
      timestamp: new Date().toISOString(),
    };
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `segmentation_${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const totalUsers = distribution.reduce((sum, d) => sum + (d.count || 0), 0);

  const segmentMappingModel = useMemo(() => {
    const area = {
      minX: 88,
      maxX: 610,
      minY: 46,
      maxY: 310,
    };

    const distributionBySegment = Object.fromEntries(
      distribution.map((d) => [
        d.name,
        {
          count: Number(d.count || 0),
          percentage: Number(d.percentage || 0),
        },
      ]),
    );

    return Object.keys(SEGMENT_COLORS).map((segment) => {
      const points = clusterPointsBySegment[segment] || [];
      const fallback = SEGMENT_FALLBACK_POSITIONS[segment] || {
        x: 0.5,
        y: 0.5,
      };

      const meanX =
        points.length > 0
          ? points.reduce((sum, p) => sum + Number(p.x || 0), 0) / points.length
          : fallback.x;
      const meanY =
        points.length > 0
          ? points.reduce((sum, p) => sum + Number(p.y || 0), 0) / points.length
          : fallback.y;

      const cx =
        area.minX + Math.max(0, Math.min(1, meanX)) * (area.maxX - area.minX);
      const cy =
        area.maxY - Math.max(0, Math.min(1, meanY)) * (area.maxY - area.minY);

      const metrics = distributionBySegment[segment] || {
        count: 0,
        percentage: 0,
      };
      const pct = Number(metrics.percentage || 0);
      const rx = Math.max(46, Math.min(108, 42 + pct * 1.1));
      const ry = Math.max(30, Math.min(72, 26 + pct * 0.65));
      const labelOffset = SEGMENT_LABEL_OFFSETS[segment] || { dx: 32, dy: -32 };
      const labelX = Math.max(98, Math.min(548, cx + labelOffset.dx));
      const labelY = Math.max(42, Math.min(292, cy + labelOffset.dy));

      const sample = points.slice(0, 10);
      const dots =
        sample.length > 0
          ? sample.map((p, idx) => {
              const dx = (Number(p.x || meanX) - meanX) * 110;
              const dy = (Number(p.y || meanY) - meanY) * 90;
              return {
                key: `${segment}-dot-${idx}`,
                x: Math.max(area.minX + 6, Math.min(area.maxX - 6, cx + dx)),
                y: Math.max(area.minY + 6, Math.min(area.maxY - 6, cy - dy)),
              };
            })
          : pct > 0
            ? [
                { key: `${segment}-dot-a`, x: cx - 16, y: cy + 8 },
                { key: `${segment}-dot-b`, x: cx + 10, y: cy - 6 },
              ]
            : [];

      return {
        segment,
        alias: SEGMENT_ALIASES[segment] || segment,
        color: SEGMENT_COLORS[segment],
        cx,
        cy,
        rx,
        ry,
        pct,
        count: metrics.count,
        labelX,
        labelY,
        dots,
      };
    });
  }, [clusterPointsBySegment, distribution]);

  // Radar data for behavioral profile
  const radarData = [
    { metric: "Activity", "Power Users": 95, "Trial Only": 10 },
    { metric: "ARPU", "Power Users": 90, "Trial Only": 0 },
    { metric: "Retention", "Power Users": 88, "Trial Only": 15 },
    { metric: "Loyalty", "Power Users": 85, "Trial Only": 5 },
    { metric: "Engagement", "Power Users": 92, "Trial Only": 8 },
  ];

  // AI Insights
  const insights = [
    {
      id: "1",
      type: "warning",
      severity: "red",
      icon: "⚠️",
      title: "Trial Only — Critical Churn Risk",
      message:
        "42.4% churn rate detected. Launch a targeted SMS re-engagement campaign within 72 hours of trial expiration to recover at-risk users.",
    },
    {
      id: "2",
      type: "success",
      severity: "green",
      icon: "✨",
      title: "Power Users — Upsell Opportunity",
      message:
        "18% of subscribers generate 45% of revenue. Consider offering premium bundles or multi-service packages to this high-value segment.",
    },
    {
      id: "3",
      type: "info",
      severity: "amber",
      icon: "ðŸ’¡",
      title: "Occasional Users — Conversion Potential",
      message:
        "25% of the base with low ARPU (2.1 TND). An automated weekly re-engagement SMS could increase engagement by 15–20%.",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1
            className="text-2xl font-bold"
            style={{ color: "var(--color-text-primary)" }}
          >
            User Segmentation — AI
          </h1>
          <p
            className="mt-1 text-sm"
            style={{ color: "var(--color-text-muted)" }}
          >
            Advanced behavioral analysis using AI clustering (K-Means) to
            optimize SMS subscription service performance.
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 rounded-lg transition text-sm font-medium"
            style={{
              backgroundColor: "var(--color-bg-elevated)",
              border: "1px solid var(--color-border)",
              color: "var(--color-text-secondary)",
            }}
          >
            <Download size={16} /> Export
          </button>
        </div>
      </div>

      <FilterBar
        onApply={(f) => setFilters(f)}
        defaultPeriod="all"
        appliedFilters={filters}
      />

      {(kpiError || clusterError || profileError) && (
        <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
          <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
          <p
            className="flex-1 text-sm"
            style={{ color: "var(--color-danger-text)" }}
          >
            {kpiError || clusterError || profileError}
          </p>
          <button
            onClick={() => {
              refetchKPIs();
              refetchClusters();
              refetchProfiles();
            }}
            className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
          >
            <RotateCcw size={14} /> Retry
          </button>
        </div>
      )}

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiLoading ? (
          Array.from({ length: 4 }).map((_, i) => <KPISkeleton key={i} />)
        ) : (
          <>
            <KPICard
              title="Identified Segments"
              value={kpis.total_segments}
              subtitle="Stable K-Means model"
              icon={RotateCcw}
              iconColor="#3b82f6"
              iconBg="bg-blue-500/10"
            />
            <KPICard
              title="Dominant Segment"
              value={kpis.dominant_segment}
              subtitle={`${kpis.dominant_pct}% of active base`}
              icon={RotateCcw}
              iconColor="#22c55e"
              iconBg="bg-green-500/10"
            />
            <KPICard
              title="High Value Segment"
              value={kpis.high_value_segment}
              subtitle={`+${kpis.arpu_premium}% ARPU vs average`}
              icon={RotateCcw}
              iconColor="#f59e0b"
              iconBg="bg-amber-500/10"
            />
            <KPICard
              title="At-Risk Segment"
              value={kpis.risk_segment}
              subtitle="Critical churn rate"
              icon={RotateCcw}
              iconColor="#ef4444"
              iconBg="bg-red-500/10"
              trend={kpis.risk_churn_rate}
              trendLabel="churn rate"
            />
          </>
        )}
      </div>

      {/* Charts Grid - Row 1: Scatter + Right Column (2 stacked) */}
      <div className="grid grid-cols-1 xl:grid-cols-7 gap-6">
        {/* LEFT: Clustering Map */}
        <div className="xl:col-span-4">
          <ChartContainerCard
            title="Segment Mapping"
            demoData={!clusterData}
            loading={clusterLoading}
          >
            <div className="mb-3 flex flex-wrap gap-2">
              {segmentMappingModel.map((cluster) => (
                <span
                  key={cluster.segment}
                  className="inline-flex items-center gap-2 rounded-full px-2 py-1 text-[11px]"
                  style={{
                    color: "var(--color-text-secondary)",
                    border: "1px solid var(--color-border)",
                    backgroundColor: "var(--color-bg-elevated)",
                  }}
                >
                  <span
                    className="h-2 w-2 rounded-full"
                    style={{ backgroundColor: cluster.color }}
                  />
                  {cluster.alias}
                </span>
              ))}
            </div>

            <div className="h-[420px] w-full">
              <svg
                viewBox="0 0 680 400"
                className="h-full w-full"
                role="img"
                aria-label="Segment mapping by activity and customer lifetime value"
              >
                <defs>
                  <clipPath id="segment-map-clip">
                    <rect x="66" y="24" width="578" height="322" rx="6" />
                  </clipPath>
                  <filter id="segment-soft-shadow" x="-20%" y="-20%" width="140%" height="140%">
                    <feDropShadow
                      dx="0"
                      dy="8"
                      stdDeviation="8"
                      floodColor="#020617"
                      floodOpacity="0.22"
                    />
                  </filter>
                </defs>

                <rect
                  x="66"
                  y="24"
                  width="578"
                  height="322"
                  rx="6"
                  fill="var(--color-bg-elevated)"
                  opacity="0.42"
                />

                {[0, 1, 2, 3, 4].map((step) => {
                  const x = 66 + step * 144.5;
                  return (
                    <line
                      key={`grid-x-${step}`}
                      x1={x}
                      y1="24"
                      x2={x}
                      y2="346"
                      stroke="var(--chart-grid)"
                      strokeDasharray={step === 0 ? "0" : "4 6"}
                      strokeOpacity={step === 0 ? 0.9 : 0.55}
                    />
                  );
                })}
                {[0, 1, 2, 3, 4].map((step) => {
                  const y = 24 + step * 80.5;
                  return (
                    <line
                      key={`grid-y-${step}`}
                      x1="66"
                      y1={y}
                      x2="644"
                      y2={y}
                      stroke="var(--chart-grid)"
                      strokeDasharray={step === 4 ? "0" : "4 6"}
                      strokeOpacity={step === 4 ? 0.9 : 0.55}
                    />
                  );
                })}

                <line
                  x1="355"
                  y1="24"
                  x2="355"
                  y2="346"
                  stroke="var(--chart-grid)"
                  strokeDasharray="8 8"
                  strokeOpacity="0.9"
                />
                <line
                  x1="66"
                  y1="185"
                  x2="644"
                  y2="185"
                  stroke="var(--chart-grid)"
                  strokeDasharray="8 8"
                  strokeOpacity="0.9"
                />

                <text x="84" y="44" fontSize="10" fill="var(--chart-axis-text)">
                  High value
                </text>
                <text x="84" y="204" fontSize="10" fill="var(--chart-axis-text)">
                  Low value
                </text>
                <text x="530" y="333" fontSize="10" fill="var(--chart-axis-text)">
                  High activity
                </text>
                <text x="80" y="333" fontSize="10" fill="var(--chart-axis-text)">
                  Low activity
                </text>

                <g clipPath="url(#segment-map-clip)">
                  {segmentMappingModel.map((cluster) => (
                    <g key={cluster.segment} filter="url(#segment-soft-shadow)">
                      <ellipse
                        cx={cluster.cx}
                        cy={cluster.cy}
                        rx={cluster.rx}
                        ry={cluster.ry}
                        fill={cluster.color}
                        fillOpacity="0.14"
                        stroke={cluster.color}
                        strokeOpacity="0.68"
                        strokeWidth="2"
                      />
                      {cluster.dots.map((dot) => (
                        <circle
                          key={dot.key}
                          cx={dot.x}
                          cy={dot.y}
                          r="3.8"
                          fill={cluster.color}
                          fillOpacity="0.92"
                          stroke="#ffffff"
                          strokeOpacity="0.42"
                          strokeWidth="1"
                        />
                      ))}
                    </g>
                  ))}
                </g>

                {segmentMappingModel.map((cluster) => (
                  <g key={`${cluster.segment}-label`}>
                    <line
                      x1={cluster.cx}
                      y1={cluster.cy}
                      x2={cluster.labelX}
                      y2={cluster.labelY}
                      stroke={cluster.color}
                      strokeOpacity="0.38"
                      strokeWidth="1"
                    />
                    <rect
                      x={cluster.labelX - 4}
                      y={cluster.labelY - 17}
                      width="118"
                      height="39"
                      rx="6"
                      fill="var(--color-bg-card)"
                      stroke={cluster.color}
                      strokeOpacity="0.38"
                    />
                    <circle
                      cx={cluster.labelX + 8}
                      cy={cluster.labelY - 4}
                      r="4"
                      fill={cluster.color}
                    />
                    <text
                      x={cluster.labelX + 17}
                      y={cluster.labelY}
                      fontSize="11"
                      fontWeight="700"
                      fill="var(--color-text-primary)"
                    >
                      {cluster.segment}
                    </text>
                    <text
                      x={cluster.labelX + 17}
                      y={cluster.labelY + 15}
                      fontSize="10"
                      fill="var(--color-text-muted)"
                    >
                      {cluster.pct.toFixed(1)}% - {formatCompactNumber(cluster.count)}
                    </text>
                  </g>
                ))}

                <text
                  x="355"
                  y="386"
                  textAnchor="middle"
                  fontSize="11"
                  fill="var(--chart-axis-text)"
                  style={{ letterSpacing: "0.08em" }}
                >
                  USAGE ACTIVITY FREQUENCY
                </text>
                <text
                  x="20"
                  y="185"
                  textAnchor="middle"
                  transform="rotate(-90, 20, 185)"
                  fontSize="11"
                  fill="var(--chart-axis-text)"
                  style={{ letterSpacing: "0.08em" }}
                >
                  CUSTOMER LIFETIME VALUE
                </text>
              </svg>
            </div>
          </ChartContainerCard>
        </div>

        {/* RIGHT COLUMN: 2 stacked cards */}
        <div className="xl:col-span-3 space-y-6">
          {/* Segment Size Distribution */}
          <ChartContainerCard
            title="Segment Size Distribution"
            demoData={!clusterData}
            loading={clusterLoading}
          >
            <ResponsiveContainer width="100%" height={180}>
              <BarChart layout="vertical" data={distribution}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="var(--chart-grid)"
                />
                <XAxis
                  type="number"
                  domain={[0, 100]}
                  tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
                  tickFormatter={(v) => `${v}%`}
                  axisLine={{ stroke: "var(--chart-grid)" }}
                  tickLine={{ stroke: "var(--chart-grid)" }}
                />
                <YAxis
                  dataKey="name"
                  type="category"
                  width={150}
                  tick={{ fill: "var(--chart-axis-text)", fontSize: 10 }}
                  axisLine={{ stroke: "var(--chart-grid)" }}
                  tickLine={{ stroke: "var(--chart-grid)" }}
                />
                <Tooltip
                  formatter={(v) => `${v}%`}
                  contentStyle={{
                    backgroundColor: "var(--chart-tooltip-bg)",
                    border: "1px solid var(--chart-tooltip-border)",
                  }}
                />
                <Bar dataKey="percentage" radius={[0, 4, 4, 0]}>
                  <LabelList
                    dataKey="percentage"
                    position="right"
                    formatter={(v) => `${v}%`}
                  />
                  {distribution.map((item, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={SEGMENT_COLORS[item.name] || "#94a3b8"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartContainerCard>

          {/* User Distribution */}
          <ChartContainerCard
            title="User Distribution"
            demoData={!clusterData}
            loading={clusterLoading}
          >
            <div className="flex items-center justify-between gap-6">
              <ResponsiveContainer width={160} height={160}>
                <PieChart>
                  <Pie
                    data={distribution}
                    cx={80}
                    cy={80}
                    innerRadius={50}
                    outerRadius={70}
                    paddingAngle={3}
                    dataKey="percentage"
                    isAnimationActive={false}
                  >
                    {distribution.map((item, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={SEGMENT_COLORS[item.name] || "#94a3b8"}
                      />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>

              <div className="flex-1 space-y-3">
                <div className="text-center mb-3">
                  <p
                    className="text-2xl font-bold"
                    style={{ color: "var(--color-text-primary)" }}
                  >
                    {Number(totalUsers || 0).toLocaleString()}
                  </p>
                  <p
                    className="text-xs"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    users
                  </p>
                </div>
                <div className="space-y-2 text-xs">
                  {distribution.map((item) => (
                    <div key={item.name} className="flex items-center gap-2">
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: SEGMENT_COLORS[item.name] }}
                      />
                      <span style={{ color: "var(--color-text-secondary)" }}>
                        {item.name}
                      </span>
                      <span
                        className="ml-auto"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        {item.percentage}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </ChartContainerCard>
        </div>
      </div>

      {/* Charts Grid - Row 2: Radar + Detailed Profiles */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
        {/* Behavioral Profile Comparison */}
        <div className="xl:col-span-2">
          <ChartContainerCard
            title="Behavioral Profile Comparison"
            demoData={false}
            loading={profileLoading}
          >
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="var(--chart-grid)" />
                <PolarAngleAxis
                  dataKey="metric"
                  tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
                />
                <Radar
                  name="Power Users"
                  dataKey="Power Users"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.3}
                />
                <Radar
                  name="Trial Only"
                  dataKey="Trial Only"
                  stroke="#ef4444"
                  fill="#ef4444"
                  fillOpacity={0.2}
                />
                <Legend
                  formatter={(value) => (
                    <span style={{ color: "var(--color-text-muted)" }}>
                      {value}
                    </span>
                  )}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--chart-tooltip-bg)",
                    border: "1px solid var(--chart-tooltip-border)",
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </ChartContainerCard>
        </div>

        {/* Detailed Segment Profiles */}
        <div className="xl:col-span-3">
          <ChartContainerCard
            title="Detailed Segment Profiles"
            demoData={!profileData}
            loading={profileLoading}
          >
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr
                    style={{ borderBottom: "1px solid var(--color-border)" }}
                  >
                    <th
                      className="px-4 py-3 text-left text-xs font-semibold"
                      style={{ color: "var(--color-text-muted)" }}
                    >
                      Segment
                    </th>
                    <th
                      className="px-4 py-3 text-left text-xs font-semibold"
                      style={{ color: "var(--color-text-muted)" }}
                    >
                      Activity (30d)
                    </th>
                    <th
                      className="px-4 py-3 text-right text-xs font-semibold"
                      style={{ color: "var(--color-text-muted)" }}
                    >
                      ARPU (TND)
                    </th>
                    <th
                      className="px-4 py-3 text-right text-xs font-semibold"
                      style={{ color: "var(--color-text-muted)" }}
                    >
                      Churn Rate
                    </th>
                    <th
                      className="px-4 py-3 text-center text-xs font-semibold"
                      style={{ color: "var(--color-text-muted)" }}
                    >
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {profiles.map((row, i) => {
                    const churnBgClass =
                      row.churn_rate < 5
                        ? "bg-green-500/20 text-green-300"
                        : row.churn_rate < 20
                          ? "bg-orange-500/20 text-orange-300"
                          : "bg-red-500/20 text-red-300";

                    return (
                      <tr
                        key={i}
                        className="transition"
                        style={{
                          borderBottom:
                            "1px solid var(--color-border-subtle)",
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor =
                            "var(--color-bg-elevated)";
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor =
                            "transparent";
                        }}
                      >
                        <td
                          className="px-4 py-3"
                          style={{ color: "var(--color-text-secondary)" }}
                        >
                          <div className="flex items-center gap-2">
                            <div
                              className="w-2 h-2 rounded-full"
                              style={{
                                backgroundColor: SEGMENT_COLORS[row.segment],
                              }}
                            />
                            {row.segment}
                          </div>
                        </td>
                        <td
                          className="px-4 py-3"
                          style={{ color: "var(--color-text-secondary)" }}
                        >
                          {Number(row.active_days_30d ?? 0).toFixed(1)}d /30d{" "}
                          <span style={{ color: "var(--color-text-muted)" }}>
                            ({Number(row.activity_ratio_30d ?? 0).toFixed(1)}%)
                          </span>
                        </td>
                        <td
                          className="px-4 py-3 text-right font-mono"
                          style={{ color: "var(--color-text-secondary)" }}
                        >
                          {row.arpu.toFixed(1)}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <span
                            className={`inline-block px-2 py-1 rounded text-xs font-medium ${churnBgClass}`}
                          >
                            {row.churn_rate.toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <button
                            className="text-xs font-medium transition"
                            style={{ color: "var(--color-accent)" }}
                          >
                            Details
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </ChartContainerCard>
        </div>
      </div>

      {/* AI Insights */}
      <BIInsightsPanel insights={insights} />
    </div>
  );
}
