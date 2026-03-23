import React, { useMemo, useState } from "react"
import PropTypes from "prop-types"
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts"

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

export default function ChurnCurveChart({ data = [] }) {
  const [showRetention, setShowRetention] = useState(true)

  const series = useMemo(() => {
    // Aggregate across services by month (keep UI simple and consistent)
    const byMonth = new Map()
    for (const r of data) {
      const key = r.month
      const cur = byMonth.get(key) ?? { month: key, churn_rate: 0, retention_rate: 0, new_subscriptions: 0, _n: 0 }
      cur.churn_rate += Number(r.churn_rate ?? 0)
      cur.retention_rate += Number(r.retention_rate ?? 0)
      cur.new_subscriptions += Number(r.new_subscriptions ?? 0)
      cur._n += 1
      byMonth.set(key, cur)
    }
    return Array.from(byMonth.values())
      .map((x) => ({
        month: x.month,
        churn_rate: x._n ? x.churn_rate / x._n : 0,
        retention_rate: x._n ? x.retention_rate / x._n : 0,
        new_subscriptions: x.new_subscriptions,
      }))
      .sort((a, b) => String(a.month).localeCompare(String(b.month)))
  }, [data])

  return (
    <Card
      title="Churn Over Time"
      subtitle="Monthly churn and retention rates"
      right={
        <button
          onClick={() => setShowRetention((v) => !v)}
          className="px-3 py-1.5 text-xs bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-lg transition"
        >
          {showRetention ? "Hide retention" : "Show retention"}
        </button>
      }
    >
      <div className="h-80 w-full min-w-0">
        <ResponsiveContainer width="100%" height="100%" minWidth="0" minHeight="0">
          <LineChart data={series} margin={{ top: 10, right: 18, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.12)" />
            <XAxis dataKey="month" stroke="rgba(148,163,184,0.8)" tick={{ fontSize: 12 }} />
            <YAxis
              yAxisId="left"
              stroke="rgba(148,163,184,0.8)"
              tick={{ fontSize: 12 }}
              domain={[0, 100]}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip
              contentStyle={{ background: "#0F172A", border: "1px solid rgba(148,163,184,0.2)", borderRadius: 12 }}
              labelStyle={{ color: "#E2E8F0" }}
              formatter={(value, name) => {
                if (name === "New subscriptions") return [Number(value ?? 0).toLocaleString(), name]
                return [`${Number(value ?? 0).toFixed(2)}%`, name]
              }}
            />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="churn_rate"
              name="Churn rate"
              stroke="#F97316"
              strokeWidth={2}
              dot={false}
            />
            {showRetention && (
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="retention_rate"
                name="Retention rate"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={false}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}

ChurnCurveChart.propTypes = {
  data: PropTypes.array,
}

