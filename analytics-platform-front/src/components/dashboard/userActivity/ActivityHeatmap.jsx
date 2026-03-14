import { useMemo, useState } from "react"
import PropTypes from "prop-types"

const DAYS_FR = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

function getColorForCount(count, maxCount) {
  if (count === 0) return "#1A1D27"
  if (count < 100) return "#4C1D95"
  if (count < 300) return "#7C3AED"
  if (count < maxCount) return "#A855F7"
  return "#E879F9"
}

function detectPeakInsight(data) {
  if (!Array.isArray(data) || data.length === 0) return null

  let maxEntry = data[0]
  data.forEach((entry) => {
    if ((entry.count || 0) > (maxEntry.count || 0)) {
      maxEntry = entry
    }
  })

  if (!maxEntry || maxEntry.count === 0) return null

  // Group by day and hour to find peak period
  const dayHourMap = {}
  data.forEach((entry) => {
    const key = `${entry.day}_${entry.hour}`
    if (!dayHourMap[key] || entry.count > dayHourMap[key].count) {
      dayHourMap[key] = entry
    }
  })

  const peakDayHour = Object.values(dayHourMap).reduce((max, curr) =>
    (curr.count || 0) > (max.count || 0) ? curr : max
  )

  const dayName = DAYS_FR[peakDayHour.day] || "?"
  const hours = `${peakDayHour.hour}h-${peakDayHour.hour + 3}h`

  return {
    dayName,
    hours,
    count: peakDayHour.count,
  }
}

export default function ActivityHeatmap({ data }) {
  const [hoveredCell, setHoveredCell] = useState(null)

  const { grid, maxCount, peak } = useMemo(() => {
    if (!Array.isArray(data) || data.length === 0) {
      return { grid: {}, maxCount: 0, peak: null }
    }

    const grid = {}
    let maxCount = 0

    data.forEach((entry) => {
      const key = `${entry.day}_${entry.hour}`
      grid[key] = entry.count || 0
      maxCount = Math.max(maxCount, entry.count || 0)
    })

    return {
      grid,
      maxCount: maxCount || 1,
      peak: detectPeakInsight(data),
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
        <h3 className="text-lg font-semibold text-slate-100 mb-6">
          Activity Heatmap (Day × Hour)
        </h3>

        {/* Heatmap Grid */}
        <div className="overflow-x-auto">
          <div className="inline-block">
            {/* Hour Labels */}
            <div className="flex">
              <div className="w-12" />
              {Array.from({ length: 24 }).map((_, hour) => (
                <div key={`hour-${hour}`} className="w-10 text-center text-xs text-slate-500">
                  {[0, 6, 12, 18, 23].includes(hour) ? hour : ""}
                </div>
              ))}
            </div>

            {/* Heatmap Grid */}
            {Array.from({ length: 7 }).map((_, dayIndex) => (
              <div key={`row-${dayIndex}`} className="flex">
                {/* Day Label */}
                <div className="w-12 flex items-center justify-center text-xs font-medium text-slate-400">
                  {DAYS_FR[dayIndex]}
                </div>

                {/* Cells */}
                {Array.from({ length: 24 }).map((_, hour) => {
                  const key = `${dayIndex}_${hour}`
                  const count = grid[key] || 0
                  const color = getColorForCount(count, maxCount)
                  const isHovered = hoveredCell === key

                  return (
                    <div key={key} className="relative">
                      <div
                        className={`w-10 h-10 cursor-pointer transition-all ${
                          isHovered ? "ring-2 ring-offset-2 ring-slate-300" : ""
                        }`}
                        style={{ backgroundColor: color }}
                        onMouseEnter={() => setHoveredCell(key)}
                        onMouseLeave={() => setHoveredCell(null)}
                        title={`${DAYS_FR[dayIndex]} ${hour}h — ${count} users`}
                      />

                      {/* Hover Tooltip */}
                      {isHovered && (
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 z-50 bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-slate-100 whitespace-nowrap">
                          {DAYS_FR[dayIndex]} {hour}h — {count} utilisateurs
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            ))}
          </div>
        </div>

        {/* Legend */}
        <div className="mt-8 space-y-2">
          <p className="text-xs font-semibold text-slate-400 uppercase">Légende</p>
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6" style={{ backgroundColor: "#1A1D27" }} />
              <span className="text-xs text-slate-400">0</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6" style={{ backgroundColor: "#4C1D95" }} />
              <span className="text-xs text-slate-400">&lt;100</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6" style={{ backgroundColor: "#7C3AED" }} />
              <span className="text-xs text-slate-400">100-300</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6" style={{ backgroundColor: "#A855F7" }} />
              <span className="text-xs text-slate-400">&gt;300</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6" style={{ backgroundColor: "#E879F9" }} />
              <span className="text-xs text-slate-400">Max</span>
            </div>
          </div>
        </div>
      </div>

      {/* Peak Insight */}
      {peak && (
        <div className="border-l-4 border-purple-500 bg-slate-900/50 p-4 rounded-r-lg">
          <p className="text-sm text-slate-200">
            <span className="mr-2">💡</span>
            <span className="font-semibold">Pic détecté :</span>
            <span className="text-slate-400 ml-1">
              {peak.dayName} {peak.hours} → Créneau optimal pour campagnes SMS
            </span>
          </p>
        </div>
      )}
    </div>
  )
}

ActivityHeatmap.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      day: PropTypes.number.isRequired,
      hour: PropTypes.number.isRequired,
      count: PropTypes.number,
    })
  ),
}
