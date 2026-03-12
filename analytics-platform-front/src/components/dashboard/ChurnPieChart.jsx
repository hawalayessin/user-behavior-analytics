import PropTypes from "prop-types"
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts"

const COLORS = ["#EF4444", "#F59E0B"]

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null

  const { name, value } = payload[0] ?? {}

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs">
      <p className="text-slate-100 font-semibold">{name}</p>
      <p className="text-slate-400">{(value ?? 0).toLocaleString()}%</p>
    </div>
  )
}

export default function ChurnPieChart({ data }) {

  // ✅ SAFE fallback (plus jamais undefined)
  const churn = data ?? {}

  const pieData = [
    { name: "Voluntary", value: churn.voluntary ?? 0 },
    { name: "Technical", value: churn.technical ?? 0 },
  ]

  const total = pieData.reduce((sum, item) => sum + item.value, 0)

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">

      <h3 className="text-sm font-semibold text-slate-100 mb-4">
        Churn Breakdown
      </h3>

      <div className="relative flex justify-center">
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={65}
              outerRadius={95}
              dataKey="value"
            >
              {pieData.map((entry, i) => (
                <Cell key={i} fill={COLORS[i]} />
              ))}
            </Pie>

            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>

        {/* center */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-xl font-bold text-slate-100">
            {total.toLocaleString()}%
          </span>
          <span className="text-xs text-slate-500">Total Churn</span>
        </div>
      </div>

    </div>
  )
}

ChurnPieChart.propTypes = {
  data: PropTypes.object,
}

CustomTooltip.propTypes = {
  active: PropTypes.bool,
  payload: PropTypes.array,
}