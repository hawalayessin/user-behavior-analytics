import PropTypes from "prop-types"
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend,
  ResponsiveContainer,
  Tooltip,
} from "recharts"

const RADAR_METRICS = ["D7", "D14", "D30", "Users", "Cohorts"]

export default function ServiceRetentionRadar({ data }) {
  if (!data?.length) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex items-center justify-center text-sm text-slate-500">
        No service radar data
      </div>
    )
  }

  const maxUsers    = Math.max(...data.map((d) => d.total_users || 0), 1)
  const maxCohorts  = Math.max(...data.map((d) => d.cohort_count || 0), 1)

  const chartData = RADAR_METRICS.map((metric) => ({
    metric,
    ...Object.fromEntries(
      data.map((s) => {
        if (metric === "D7")  return [s.service, s.d7]
        if (metric === "D14") return [s.service, s.d14]
        if (metric === "D30") return [s.service, s.d30]
        if (metric === "Users") {
          const norm = (s.total_users || 0) / maxUsers * 100
          return [s.service, norm]
        }
        if (metric === "Cohorts") {
          const norm = (s.cohort_count || 0) / maxCohorts * 100
          return [s.service, norm]
        }
        return [s.service, 0]
      })
    ),
  }))

  const colors = ["#6366F1", "#10B981", "#F59E0B", "#EC4899", "#22C55E", "#3B82F6"]

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex flex-col">
      <h3 className="text-sm font-semibold text-slate-100 mb-4">
        Service Retention Radar
      </h3>
      <div className="flex-1 min-h-[260px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
            <PolarGrid stroke="#1f2937" />
            <PolarAngleAxis
              dataKey="metric"
              tick={{ fill: "#9CA3AF", fontSize: 11 }}
            />
            <PolarRadiusAxis
              angle={30}
              tick={{ fill: "#6B7280", fontSize: 10 }}
              tickFormatter={(v) => `${v}%`}
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
            {data.map((s, idx) => (
              <Radar
                key={s.service}
                name={s.service}
                dataKey={s.service}
                stroke={colors[idx % colors.length]}
                fill={colors[idx % colors.length]}
                fillOpacity={0.25}
              />
            ))}
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

ServiceRetentionRadar.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      service:      PropTypes.string.isRequired,
      d7:           PropTypes.number.isRequired,
      d14:          PropTypes.number.isRequired,
      d30:          PropTypes.number.isRequired,
      total_users:  PropTypes.number,
      cohort_count: PropTypes.number,
    })
  ),
}

