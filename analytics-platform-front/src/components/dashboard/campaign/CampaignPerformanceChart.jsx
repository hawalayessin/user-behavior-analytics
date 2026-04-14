import { useMemo, useState } from "react";
import PropTypes from "prop-types";
import {
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

function clampLabel(s, max = 18) {
  if (!s) return "";
  return s.length > max ? `${s.slice(0, max)}…` : s;
}

export default function CampaignPerformanceChart({ data }) {
  const [sortBy, setSortBy] = useState("conv_rate"); // conv_rate | avg_d7

  const sorted = useMemo(() => {
    const list = Array.isArray(data) ? [...data] : [];
    list.sort((a, b) => Number(b?.[sortBy] ?? 0) - Number(a?.[sortBy] ?? 0));
    return list;
  }, [data, sortBy]);

  const visible = sorted.slice(0, 8);

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-100">
            Campaign Performance
          </h3>
          <p className="text-sm text-slate-400">
            Conversion rate vs D7 retention (top 8)
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setSortBy("conv_rate")}
            className={`px-3 py-1.5 rounded-lg text-xs border transition ${
              sortBy === "conv_rate"
                ? "bg-violet-600/20 border-violet-500/40 text-violet-200"
                : "bg-slate-900/30 border-slate-700/50 text-slate-300 hover:bg-slate-900/60"
            }`}
          >
            Sort: Conv%
          </button>
          <button
            onClick={() => setSortBy("avg_d7")}
            className={`px-3 py-1.5 rounded-lg text-xs border transition ${
              sortBy === "avg_d7"
                ? "bg-emerald-600/20 border-emerald-500/40 text-emerald-200"
                : "bg-slate-900/30 border-slate-700/50 text-slate-300 hover:bg-slate-900/60"
            }`}
          >
            Sort: D7%
          </button>
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={visible}
            margin={{ top: 10, right: 20, left: 0, bottom: 10 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(148,163,184,0.15)"
            />
            <XAxis
              dataKey="name"
              tick={{ fill: "#94A3B8", fontSize: 11 }}
              tickFormatter={(v) => clampLabel(String(v))}
              interval={0}
              angle={-10}
              height={50}
            />
            <YAxis tick={{ fill: "#94A3B8", fontSize: 11 }} />
            <Tooltip
              contentStyle={{
                background: "var(--chart-tooltip-bg)",
                border: "1px solid rgba(148,163,184,0.25)",
                borderRadius: 12,
              }}
              labelStyle={{ color: "#E2E8F0" }}
              formatter={(value, key, payload) => {
                const v = Number(value ?? 0);
                if (key === "conv_rate") return [`${v.toFixed(2)}%`, "Conv%"];
                if (key === "avg_d7") return [`${v.toFixed(2)}%`, "D7%"];
                return [String(value), String(key)];
              }}
              labelFormatter={(label, payload) => {
                const row = payload?.[0]?.payload;
                if (!row) return String(label);
                return `${row.name} — ${row.service_name}`;
              }}
            />
            <Legend />
            <Bar
              dataKey="conv_rate"
              name="Conv%"
              fill="#6366F1"
              radius={[6, 6, 0, 0]}
            />
            <Bar
              dataKey="avg_d7"
              name="D7%"
              fill="#10B981"
              radius={[6, 6, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {sorted.length > 8 && (
        <p className="text-xs text-slate-500">
          Showing top 8 campaigns. Use table below for full list.
        </p>
      )}
    </div>
  );
}

CampaignPerformanceChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      campaign_id: PropTypes.string,
      name: PropTypes.string,
      service_name: PropTypes.string,
      target_size: PropTypes.number,
      total_subs: PropTypes.number,
      active_subs: PropTypes.number,
      conv_rate: PropTypes.number,
      avg_d7: PropTypes.number,
    }),
  ),
};
