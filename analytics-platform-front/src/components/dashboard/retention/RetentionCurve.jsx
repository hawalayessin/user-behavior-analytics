import PropTypes from "prop-types"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts"

const COLORS = ["#6366F1", "#10B981", "#F59E0B", "#EC4899", "#22C55E", "#3B82F6"]

export default function RetentionCurve({ data }) {
  if (!data?.length) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex items-center justify-center text-sm text-slate-500">
        No retention curve data
      </div>
    )
  }

  const chartData = data.map((row) => ({
    service: row.service,
    D0:  row.d0,
    D7:  row.d7,
    D14: row.d14,
    D30: row.d30,
  }))

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex flex-col">
      <h3 className="text-sm font-semibold text-slate-100 mb-4">
        Retention Curve by Service
      </h3>
      <div className="flex-1 min-h-[260px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 10, right: 20, bottom: 10, left: 0 }}
          >
            <XAxis dataKey="service" tick={{ fontSize: 11, fill: "#9CA3AF" }} />
            <YAxis
              tick={{ fontSize: 11, fill: "#9CA3AF" }}
              tickFormatter={(v) => `${v}%`}
              domain={[0, 100]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#020617",
                border: "1px solid #1f2937",
                borderRadius: "0.5rem",
                fontSize: "0.75rem",
                color: "#e5e7eb",
              }}
              formatter={(value, name) => [`${value.toFixed(1)}%`, name]}
            />
            <Legend
              wrapperStyle={{ fontSize: "0.75rem", color: "#9CA3AF" }}
            />
            <ReferenceLine
              y={40}
              stroke="#4B5563"
              strokeDasharray="4 4"
              label={{
                position: "right",
                value: "D7 target 40%",
                fill: "#9CA3AF",
                fontSize: 11,
              }}
            />
            {["D0", "D7", "D14", "D30"].map((key, idx) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={COLORS[idx]}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
                strokeWidth={2}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

RetentionCurve.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      service: PropTypes.string.isRequired,
      d0:      PropTypes.number.isRequired,
      d7:      PropTypes.number.isRequired,
      d14:     PropTypes.number.isRequired,
      d30:     PropTypes.number.isRequired,
    })
  ),
}

