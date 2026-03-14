import { useMemo } from "react"
import PropTypes from "prop-types"
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts"

const BUCKET_CONFIG = {
  "1-7j": { color: "#FBBF24", label: "1-7j" },
  "8-14j": { color: "#F97316", label: "8-14j" },
  "15-30j": { color: "#FB923C", label: "15-30j" },
  "+30j": { color: "#EF4444", label: "+30j" },
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload || !payload[0]) return null
  const { name, value, percent } = payload[0].payload

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 shadow-xl">
      <p className="text-xs text-slate-300 font-semibold">{name}</p>
      <p className="text-sm font-bold text-slate-100">{value?.toLocaleString()}</p>
      <p className="text-xs text-slate-400">{(percent * 100).toFixed(1)}%</p>
    </div>
  )
}

export default function InactivityAnalysis({ data, inactive_count }) {
  const { pieData, barData, critical } = useMemo(() => {
    if (!Array.isArray(data) || data.length === 0) {
      return { pieData: [], barData: [], critical: null }
    }

    // Process bucket data
    const buckets = {}
    let total = 0

    data.forEach((entry) => {
      const bucket = entry.bucket || "unknown"
      buckets[bucket] = (buckets[bucket] || 0) + (entry.count || 0)
      total += entry.count || 0
    })

    // Map to pie chart format
    const pieData = []
    const barData = []

    Object.entries(BUCKET_CONFIG).forEach(([key, config]) => {
      const count = buckets[key] || 0
      if (count > 0 || key === "+30j") {
        pieData.push({
          name: config.label,
          value: count,
          percent: total > 0 ? count / total : 0,
        })
        barData.push({
          label: config.label,
          count,
          percentage: total > 0 ? ((count / total) * 100).toFixed(1) : 0,
          color: config.color,
        })
      }
    })

    // Determine criticality
    const criticalCount = buckets["+30j"] || 0
    const isCritical = criticalCount > 0

    return {
      pieData,
      barData,
      critical: isCritical ? { count: criticalCount, percentage: ((criticalCount / total) * 100).toFixed(1) } : null,
    }
  }, [data])

  if (!data || data.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <p className="text-slate-400 text-center py-8">No data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-slate-100 mb-6">Inactivity Analysis</h3>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 items-stretch">
          {/* Pie Chart */}
          <div className="lg:col-span-2 flex items-center justify-center">
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    label={false}
                  >
                    {pieData.map((entry, index) => {
                      const config = Object.values(BUCKET_CONFIG)[index]
                      return (
                        <Cell
                          key={`cell-${index}`}
                          fill={config?.color || "#9CA3AF"}
                        />
                      )
                    })}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <text
                    x="50%"
                    y="50%"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="text-2xl font-bold fill-slate-100"
                  >
                    {inactive_count?.toLocaleString() || "0"}
                  </text>
                </PieChart>
              </ResponsiveContainer>
            ) : null}
          </div>

          {/* Horizontal Bars */}
          <div className="lg:col-span-3 space-y-4">
            {barData.map((bar) => (
              <div key={bar.label} className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-300">{bar.label}</span>
                  <div className="text-sm font-semibold text-slate-200">
                    {bar.count?.toLocaleString()} ({bar.percentage}%)
                  </div>
                </div>
                <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full transition-all"
                    style={{
                      backgroundColor: bar.color,
                      width: `${bar.percentage}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Critical Alert */}
      {critical && critical.count > 0 && (
        <div className="border-l-4 border-orange-500 bg-slate-900/50 p-4 rounded-r-lg">
          <p className="text-sm text-slate-200 leading-relaxed">
            <span className="mr-2">⚠️</span>
            <span className="font-semibold">
              {critical.count?.toLocaleString()} utilisateurs inactifs depuis +30j
            </span>
            <span className="text-slate-400 ml-1">
              → risque churn définitif. Recommandation : campagne de réactivation SMS ciblée.
            </span>
          </p>
        </div>
      )}
    </div>
  )
}

InactivityAnalysis.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      bucket: PropTypes.string.isRequired,
      count: PropTypes.number,
    })
  ),
  inactive_count: PropTypes.number,
}
