import React, { useMemo } from "react";
import PropTypes from "prop-types";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import ChartContainer from "./ChartContainer";

function Card({ title, subtitle, children }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-slate-100">{title}</h3>
        {subtitle && <p className="text-sm text-slate-400 mt-1">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}

const BUCKETS = [
  "0-3 days",
  "4-7 days",
  "8-30 days",
  "31-90 days",
  "90+ days",
  "Unknown",
];

export default function TimeToChurnChart({ data = [] }) {
  const rows = useMemo(() => {
    // Collapse across services: show stacked distribution per bucket
    const byBucket = new Map();
    for (const b of BUCKETS)
      byBucket.set(b, { bucket: b, VOLUNTARY: 0, TECHNICAL: 0 });
    for (const r of data) {
      const key = r.bucket ?? "Unknown";
      const cur = byBucket.get(key) ?? {
        bucket: key,
        VOLUNTARY: 0,
        TECHNICAL: 0,
      };
      const t = r.churn_type;
      if (t === "VOLUNTARY" || t === "TECHNICAL")
        cur[t] += Number(r.count ?? 0);
      byBucket.set(key, cur);
    }
    return BUCKETS.map((b) => byBucket.get(b)).filter(Boolean);
  }, [data]);

  return (
    <Card
      title="Time-to-Churn Distribution"
      subtitle="How fast users churn after subscribing"
    >
      <ChartContainer className="h-80 w-full min-w-0">
        <ResponsiveContainer
          width="100%"
          height="100%"
          minWidth="0"
          minHeight="0"
        >
          <BarChart
            data={rows}
            margin={{ top: 10, right: 18, left: 0, bottom: 0 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(148,163,184,0.12)"
            />
            <XAxis
              dataKey="bucket"
              stroke="rgba(148,163,184,0.8)"
              tick={{ fontSize: 12 }}
            />
            <YAxis stroke="rgba(148,163,184,0.8)" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                background: "var(--chart-tooltip-bg)",
                border: "1px solid rgba(148,163,184,0.2)",
                borderRadius: 12,
              }}
              labelStyle={{ color: "#E2E8F0" }}
              formatter={(v, name) => [Number(v ?? 0).toLocaleString(), name]}
            />
            <Legend />
            <Bar
              dataKey="VOLUNTARY"
              name="Voluntary"
              stackId="a"
              fill="#F97316"
            />
            <Bar
              dataKey="TECHNICAL"
              name="Technical"
              stackId="a"
              fill="#EF4444"
            />
          </BarChart>
        </ResponsiveContainer>
      </ChartContainer>
    </Card>
  );
}

TimeToChurnChart.propTypes = {
  data: PropTypes.array,
};
