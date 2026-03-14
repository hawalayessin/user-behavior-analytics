import PropTypes from "prop-types"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"

const GROWTH_DATA = [
  { month: "Sep", nouveaux: 1800, churnés: 640 },
  { month: "Oct", nouveaux: 2060, churnés: 680 },
  { month: "Nov", nouveaux: 1920, churnés: 580 },
  { month: "Dec", nouveaux: 2280, churnés: 760 },
  { month: "Jan", nouveaux: 2100, churnés: 630 },
  { month: "Feb", nouveaux: 1220, churnés: 500 },
]

function CustomTooltip({ active, payload }) {
  if (!active || !payload) return null

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 shadow-xl">
      <p className="text-xs text-slate-300 font-semibold mb-2">{payload[0]?.payload?.month}</p>
      {payload.map((entry) => (
        <div key={entry.name} className="text-xs flex items-center gap-2">
          <div
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-slate-300">{entry.name}:</span>
          <span className="font-semibold text-slate-100">{entry.value?.toLocaleString()}</span>
        </div>
      ))}
    </div>
  )
}

export default function UserGrowthChart() {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-slate-100 mb-4">User Growth</h3>
      <ResponsiveContainer width="100%" height={350}>
        <BarChart
          data={GROWTH_DATA}
          margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
        >
          <defs>
            <linearGradient id="colorNouveaux" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={1} />
              <stop offset="95%" stopColor="#10B981" stopOpacity={0.8} />
            </linearGradient>
            <linearGradient id="colorChurnés" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#EF4444" stopOpacity={1} />
              <stop offset="95%" stopColor="#EF4444" stopOpacity={0.8} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#404854" vertical={false} />

          <XAxis
            dataKey="month"
            tick={{ fontSize: 12, fill: "#9CA3AF" }}
            axisLine={{ stroke: "#404854" }}
          />

          <YAxis
            tick={{ fontSize: 12, fill: "#9CA3AF" }}
            axisLine={{ stroke: "#404854" }}
            label={{ value: "Number of Users", angle: -90, position: "insideLeft" }}
          />

          <Tooltip content={<CustomTooltip />} />

          <Legend
            wrapperStyle={{ paddingTop: "15px" }}
            contentStyle={{ backgroundColor: "transparent", border: "none" }}
            iconType="square"
          />

          <Bar
            dataKey="nouveaux"
            fill="url(#colorNouveaux)"
            name="New"
            radius={[8, 8, 0, 0]}
          />

          <Bar
            dataKey="churnés"
            fill="url(#colorChurnés)"
            name="Churned"
            radius={[8, 8, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

UserGrowthChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      month: PropTypes.string.isRequired,
      nouveaux: PropTypes.number,
      churnés: PropTypes.number,
    })
  ),
}
