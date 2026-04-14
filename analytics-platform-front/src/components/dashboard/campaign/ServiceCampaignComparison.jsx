import PropTypes from "prop-types"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
                background: "var(--chart-tooltip-bg)",
} from "recharts"

export default function ServiceCampaignComparison({ data }) {
  const chartData = (data ?? []).map((d) => ({
    ...d,
    avg_conversion: Number(d.avg_conversion ?? 0),
  }))

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
      <div>
        <h3 className="text-lg font-bold text-slate-100">Service Comparison</h3>
        <p className="text-sm text-slate-400">Average conversion rate by service</p>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 10, right: 30, left: 10, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.15)" />
            <XAxis type="number" tick={{ fill: "#94A3B8", fontSize: 11 }} domain={[0, "dataMax + 5"]} />
            <YAxis
              type="category"
              dataKey="service"
              tick={{ fill: "#94A3B8", fontSize: 11 }}
              width={110}
            />
            <Tooltip
              contentStyle={{
                background: "var(--chart-tooltip-bg)",
                border: "1px solid rgba(148,163,184,0.25)",
                borderRadius: 12,
              }}
              labelStyle={{ color: "#E2E8F0" }}
              formatter={(value, key, payload) => {
                const row = payload?.payload
                if (!row) return [value, key]
                if (key === "avg_conversion") return [`${Number(value).toFixed(2)}%`, "Avg conversion"]
                return [value, key]
              }}
            />
            <Bar dataKey="avg_conversion" fill="#F59E0B" radius={[0, 8, 8, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {(chartData ?? []).slice(0, 3).map((r) => (
          <div key={r.service} className="bg-slate-900/40 border border-slate-700/40 rounded-lg p-3">
            <p className="text-xs text-slate-400">{r.service}</p>
            <p className="text-sm text-slate-100 font-semibold">{(r.avg_conversion ?? 0).toFixed(2)}%</p>
            <p className="text-[11px] text-slate-500">
              {r.total_campaigns ?? 0} campaigns • {r.total_subs ?? 0} subs • D7 {(r.avg_d7 ?? 0).toFixed(2)}%
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

ServiceCampaignComparison.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      service: PropTypes.string.isRequired,
      total_campaigns: PropTypes.number,
      total_subs: PropTypes.number,
      avg_conversion: PropTypes.number,
      avg_d7: PropTypes.number,
    })
  ),
}

