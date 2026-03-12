import PropTypes from "prop-types"
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts"

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null

  const { name, value } = payload[0] ?? {}

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs">
      <p className="text-slate-100 font-semibold">{name}</p>
      <p className="text-slate-400">{(value ?? 0).toLocaleString()} subscribers</p>
    </div>
  )
}

export default function SubscriptionDonutChart({ data }) {

  // ✅ SAFE fallback
  const safeData = data ?? []

  // ✅ calcul total ici (plus jamais undefined)
  const total = safeData.reduce((sum, item) => sum + (item.value ?? 0), 0)

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex-[2]">
      <h3 className="text-sm font-semibold text-slate-100 mb-4">
        Subscription Status Breakdown
      </h3>

      <div className="relative flex justify-center">
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={safeData}
              cx="50%"
              cy="50%"
              innerRadius={70}
              outerRadius={100}
              dataKey="value"
              paddingAngle={2}
            >
              {safeData.map((entry, i) => (
                <Cell key={i} fill={entry.fill} />
              ))}
            </Pie>

            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>

        {/* Center label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-bold text-slate-100">
            {total.toLocaleString()}
          </span>
          <span className="text-xs text-slate-500">Total Subs</span>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 space-y-2">
        {safeData.map((item) => {
          const pct = total > 0 ? Math.round((item.value / total) * 1000) / 10 : 0

          return (
            <div key={item.name} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: item.fill }} />
                <span className="text-slate-400">{item.name}</span>
              </div>

              <div className="flex items-center gap-3">
                <span className="text-slate-300 font-medium">
                  {(item.value ?? 0).toLocaleString()}
                </span>
                <span className="text-slate-500 w-10 text-right">{pct}%</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

SubscriptionDonutChart.propTypes = {
  data: PropTypes.array,
}

CustomTooltip.propTypes = {
  active: PropTypes.bool,
  payload: PropTypes.array,
}