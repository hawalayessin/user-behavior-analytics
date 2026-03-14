import { useState, useMemo } from "react"
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
import { ChevronUp, ChevronDown } from "lucide-react"

const COLORS = {
  active: "#10B981",
  trial: "#F59E0B",
  inactive: "#EF4444",
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload) return null
  const total = payload.reduce((sum, entry) => sum + entry.value, 0)

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 shadow-xl">
      <p className="text-xs text-slate-300 font-semibold mb-2">{label}</p>
      {payload.map((entry) => {
        const percentage = total > 0 ? ((entry.value / total) * 100).toFixed(0) : 0
        return (
          <div key={entry.name} className="text-xs flex items-center gap-2">
            <div
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-slate-300">{entry.name}:</span>
            <span className="font-semibold text-slate-100">
              {entry.value?.toLocaleString()} ({percentage}%)
            </span>
          </div>
        )
      })}
    </div>
  )
}

export default function ServiceActivityTable({ data }) {
  const [sortKey, setSortKey] = useState("active_users")
  const [sortOrder, setSortOrder] = useState("desc")

  const chartData = useMemo(() => {
    if (!Array.isArray(data)) return []

    return data
      .map((service) => ({
        name: service.service_name || "N/A",
        Active: service.active_users || 0,
        "On Trial": service.trial_users || 0,
        Inactive: service.inactive_7d || 0,
        stickiness_pct: service.stickiness_pct || 0,
        avg_lifetime_days: service.avg_lifetime_days || 0,
      }))
      .sort((a, b) => {
        if (a[sortKey] < b[sortKey]) return sortOrder === "asc" ? -1 : 1
        if (a[sortKey] > b[sortKey]) return sortOrder === "asc" ? 1 : -1
        return 0
      })
  }, [data, sortKey, sortOrder])

  const toggleSort = (key) => {
    if (sortKey === key) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc")
    } else {
      setSortKey(key)
      setSortOrder("desc")
    }
  }

  const totals = useMemo(() => {
    if (!Array.isArray(data)) return null

    return {
      active_users: data.reduce((sum, s) => sum + (s.active_users || 0), 0),
      trial_users: data.reduce((sum, s) => sum + (s.trial_users || 0), 0),
      inactive_7d: data.reduce((sum, s) => sum + (s.inactive_7d || 0), 0),
      avg_stickiness:
        data.length > 0
          ? data.reduce((sum, s) => sum + (s.stickiness_pct || 0), 0) / data.length
          : 0,
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
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
      <h3 className="text-lg font-semibold text-slate-100">Activity by Service</h3>

      {/* Chart */}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={chartData}
            margin={{ top: 20, right: 30, left: 120, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#404854" vertical={false} />
            <XAxis type="number" tick={{ fontSize: 12, fill: "#9CA3AF" }} />
            <YAxis
              dataKey="name"
              type="category"
              width={110}
              tick={{ fontSize: 11, fill: "#9CA3AF" }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: "10px" }}
              contentStyle={{ backgroundColor: "transparent", border: "none" }}
            />
            <Bar dataKey="Active" stackId="a" fill={COLORS.active} name="Active" />
            <Bar dataKey="On Trial" stackId="a" fill={COLORS.trial} name="On Trial" />
            <Bar dataKey="Inactive" stackId="a" fill={COLORS.inactive} name="Inactive" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left px-4 py-2 text-slate-300 font-semibold">
                <button
                  onClick={() => toggleSort("name")}
                  className="flex items-center gap-1 hover:text-slate-100 transition"
                >
                  Service Name
                  {sortKey === "name" && (
                    sortOrder === "asc" ? (
                      <ChevronUp size={14} />
                    ) : (
                      <ChevronDown size={14} />
                    )
                  )}
                </button>
              </th>
              <th className="text-right px-4 py-2 text-slate-300 font-semibold">
                <button
                  onClick={() => toggleSort("Active")}
                  className="flex items-center justify-end gap-1 hover:text-slate-100 transition w-full"
                >
                  Active
                  {sortKey === "Active" && (
                    sortOrder === "asc" ? (
                      <ChevronUp size={14} />
                    ) : (
                      <ChevronDown size={14} />
                    )
                  )}
                </button>
              </th>
              <th className="text-right px-4 py-2 text-slate-300 font-semibold">
                <button
                  onClick={() => toggleSort("inactive_7d")}
                  className="flex items-center justify-end gap-1 hover:text-slate-100 transition w-full"
                >
                  Inactive +7d
                  {sortKey === "inactive_7d" && (
                    sortOrder === "asc" ? (
                      <ChevronUp size={14} />
                    ) : (
                      <ChevronDown size={14} />
                    )
                  )}
                </button>
              </th>
              <th className="text-right px-4 py-2 text-slate-300 font-semibold">
                <button
                  onClick={() => toggleSort("avg_lifetime_days")}
                  className="flex items-center justify-end gap-1 hover:text-slate-100 transition w-full"
                >
                  Lifetime
                  {sortKey === "avg_lifetime_days" && (
                    sortOrder === "asc" ? (
                      <ChevronUp size={14} />
                    ) : (
                      <ChevronDown size={14} />
                    )
                  )}
                </button>
              </th>
              <th className="text-right px-4 py-2 text-slate-300 font-semibold">
                <button
                  onClick={() => toggleSort("stickiness_pct")}
                  className="flex items-center justify-end gap-1 hover:text-slate-100 transition w-full"
                >
                  Stickiness
                  {sortKey === "stickiness_pct" && (
                    sortOrder === "asc" ? (
                      <ChevronUp size={14} />
                    ) : (
                      <ChevronDown size={14} />
                    )
                  )}
                </button>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {chartData.map((row) => {
              const stickiness = row.stickiness_pct || 0
              const stickinessColor =
                stickiness > 20 ? "bg-emerald-500/20 text-emerald-300" : stickiness > 10
                  ? "bg-amber-500/20 text-amber-300"
                  : "bg-red-500/20 text-red-300"

              return (
                <tr key={row.name} className="hover:bg-slate-800/50 transition">
                  <td className="px-4 py-3 text-slate-200 font-medium">{row.name}</td>
                  <td className="px-4 py-3 text-right text-slate-300">
                    {row.Actifs?.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-300">
                    {row.Inactifs?.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-300">
                    <div className="flex items-center justify-end gap-2">
                      <div className="w-16 h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-violet-500"
                          style={{
                            width: `${Math.min((row["avg_lifetime_days"] / 90) * 100, 100)}%`,
                          }}
                        />
                      </div>
                      <span className="text-sm">{row["avg_lifetime_days"].toFixed(0)}j</span>
                    </div>
                  </td>
                  <td className={`px-4 py-3 text-right font-semibold rounded ${stickinessColor}`}>
                    {stickiness.toFixed(1)}%
                  </td>
                </tr>
              )
            })}
          </tbody>
          {totals && (
            <tfoot className="border-t border-slate-700">
              <tr className="bg-slate-900/80">
                <td className="px-4 py-3 text-slate-200 font-semibold">Total</td>
                <td className="px-4 py-3 text-right text-slate-100 font-semibold">
                  {totals.active_users?.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right text-slate-100 font-semibold">
                  {totals.inactive_7d?.toLocaleString()}
                </td>
                <td colSpan={2} />
              </tr>
            </tfoot>
          )}
        </table>
      </div>
    </div>
  )
}

ServiceActivityTable.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      service_name: PropTypes.string,
      active_users: PropTypes.number,
      trial_users: PropTypes.number,
      inactive_7d: PropTypes.number,
      inactive_30d: PropTypes.number,
      avg_lifetime_days: PropTypes.number,
      stickiness_pct: PropTypes.number,
    })
  ),
}
