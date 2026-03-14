import { useMemo } from "react"
import PropTypes from "prop-types"
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ReferenceArea,
  Brush,
  ResponsiveContainer,
} from "recharts"

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload) return null

  const dateObj = new Date(label)
  const formattedDate = dateObj.toLocaleDateString("fr-FR", {
    month: "short",
    day: "numeric",
  })

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 shadow-xl">
      <p className="text-xs text-slate-300 font-semibold mb-2">{formattedDate}</p>
      {payload.map((entry) => (
        <div key={entry.name} className="text-xs flex items-center gap-2">
          <div
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-slate-300">{entry.name}:</span>
          <span className="font-semibold text-slate-100">
            {entry.value?.toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  )
}

function formatYAxis(value) {
  if (value >= 1000000) return `${(value / 1000000).toFixed(0)}M`
  if (value >= 1000) return `${(value / 1000).toFixed(0)}K`
  return value.toString()
}

export default function DAUTrendChart({ data }) {
  const chartData = useMemo(() => {
    if (!Array.isArray(data) || data.length === 0) return []

    // Calculate average DAU for reference line
    const dauValues = data.map((d) => d.dau || 0)
    const avgDAU = dauValues.reduce((a, b) => a + b, 0) / dauValues.length || 0

    // Detect spikes (DAU > avg + 20%)
    const spikeThreshold = avgDAU * 1.2

    return data.map((point, index) => ({
      ...point,
      date: point.date,
      dau: point.dau || 0,
      wau: point.wau || 0,
      mau: point.mau || 0,
      isPeak: (point.dau || 0) > spikeThreshold,
      avgDAU,
      spikeThreshold,
    }))
  }, [data])

  if (!chartData || chartData.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <p className="text-slate-400 text-center py-8">No data available</p>
      </div>
    )
  }

  const avgDAU = chartData[0]?.avgDAU || 0

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-slate-100 mb-4">DAU/WAU/MAU Trend</h3>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 0, bottom: 60 }}
        >
          <defs>
            <linearGradient id="mauGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={0.1} />
              <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#404854" vertical={false} />

          <XAxis
            dataKey="date"
            tickFormatter={(date) => {
              const d = new Date(date)
              return d.toLocaleDateString("fr-FR", { month: "short", day: "numeric" })
            }}
            tick={{ fontSize: 12, fill: "#9CA3AF" }}
            axisLine={{ stroke: "#404854" }}
          />

          <YAxis
            tickFormatter={formatYAxis}
            tick={{ fontSize: 12, fill: "#9CA3AF" }}
            axisLine={{ stroke: "#404854" }}
          />

          {/* Reference line for average DAU */}
          <ReferenceLine
            y={avgDAU}
            stroke="#7C3AED"
            strokeDasharray="5 5"
            opacity={0.5}
            label={{
              value: "Moy.",
              position: "left",
              fill: "#9CA3AF",
              fontSize: 12,
            }}
          />

          {/* Reference areas for detected peaks */}
          {chartData.map((point, index) => {
            if (point.isPeak && index > 0 && !chartData[index - 1]?.isPeak) {
              let endIndex = index
              while (
                endIndex < chartData.length &&
                chartData[endIndex]?.isPeak
              ) {
                endIndex++
              }
              return (
                <ReferenceArea
                  key={`peak-${index}`}
                  x1={point.date}
                  x2={chartData[endIndex - 1]?.date || point.date}
                  fill="#7C3AED"
                  fillOpacity={0.08}
                  label={{
                    value: "📈 Peak",
                    position: "top",
                    fill: "#7C3AED",
                    fontSize: 12,
                  }}
                />
              )
            }
            return null
          })}

          <Tooltip content={<CustomTooltip />} />

          {/* MAU as filled area */}
          <Area
            type="monotone"
            dataKey="mau"
            fill="url(#mauGradient)"
            stroke="none"
            name="MAU"
          />

          {/* DAU as line */}
          <Line
            type="monotone"
            dataKey="dau"
            stroke="#7C3AED"
            strokeWidth={2}
            dot={false}
            name="DAU"
            isAnimationActive={false}
          />

          {/* WAU as dashed line */}
          <Line
            type="monotone"
            dataKey="wau"
            stroke="#3B82F6"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="WAU"
            isAnimationActive={false}
          />

          <Legend
            wrapperStyle={{ paddingTop: "20px" }}
            contentStyle={{
              backgroundColor: "transparent",
              border: "none",
            }}
            iconType="line"
          />

          {/* Bottom brush for zoom */}
          <Brush
            dataKey="date"
            height={30}
            stroke="#404854"
            fill="#1A1D27"
            travellerWidth={8}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

DAUTrendChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      date: PropTypes.string.isRequired,
      dau: PropTypes.number,
      wau: PropTypes.number,
      mau: PropTypes.number,
    })
  ),
}
