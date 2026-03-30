import React, { useMemo } from "react"
import PropTypes from "prop-types"
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts"
import ChartContainer from "./ChartContainer"

function Card({ title, subtitle, children, right }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-start justify-between gap-3 mb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-100">{title}</h3>
          {subtitle && <p className="text-sm text-slate-400 mt-1">{subtitle}</p>}
        </div>
        {right}
      </div>
      {children}
    </div>
  )
}

export default function ChurnReasonsChart({ data = [], churnType = "ALL", onChangeType }) {
  const rows = useMemo(() => {
    const filtered = churnType === "ALL" ? data : data.filter((r) => r.churn_type === churnType)
    return filtered
      .map((r) => ({ reason: r.reason ?? "Unknown", count: Number(r.count ?? 0), churn_type: r.churn_type }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)
      .reverse()
  }, [data, churnType])

  return (
    <Card
      title="Churn Reasons"
      subtitle="Top reasons, by churn type"
      right={
        <select
          value={churnType}
          onChange={(e) => onChangeType?.(e.target.value)}
          className="px-3 py-2 text-xs bg-slate-800 border border-slate-700 rounded-lg text-slate-200 focus:outline-none"
        >
          <option value="ALL">All</option>
          <option value="VOLUNTARY">Voluntary</option>
          <option value="TECHNICAL">Technical</option>
        </select>
      }
    >
      <ChartContainer className="h-80 w-full min-w-0">
        <ResponsiveContainer width="100%" height="100%" minWidth="0" minHeight="0">
          <BarChart
            layout="vertical"
            data={rows}
            margin={{ top: 10, right: 18, left: 20, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.12)" />
            <XAxis type="number" stroke="rgba(148,163,184,0.8)" tick={{ fontSize: 12 }} />
            <YAxis
              type="category"
              dataKey="reason"
              width={160}
              stroke="rgba(148,163,184,0.8)"
              tick={{ fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{ background: "#0F172A", border: "1px solid rgba(148,163,184,0.2)", borderRadius: 12 }}
              labelStyle={{ color: "#E2E8F0" }}
              formatter={(v) => [Number(v ?? 0).toLocaleString(), "Count"]}
            />
            <Bar dataKey="count" fill="#F97316" radius={[8, 8, 8, 8]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartContainer>
    </Card>
  )
}

ChurnReasonsChart.propTypes = {
  data: PropTypes.array,
  churnType: PropTypes.oneOf(["ALL", "VOLUNTARY", "TECHNICAL"]),
  onChangeType: PropTypes.func,
}

