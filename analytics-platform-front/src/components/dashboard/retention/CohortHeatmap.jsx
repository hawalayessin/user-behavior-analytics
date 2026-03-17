import PropTypes from "prop-types"

function getCellClasses(value) {
  if (value >= 50) return "bg-emerald-500/30 text-emerald-300"
  if (value >= 30) return "bg-yellow-500/30 text-yellow-300"
  if (value > 0)   return "bg-red-500/30 text-red-300"
  return "bg-slate-800/60 text-slate-500"
}

export default function CohortHeatmap({ data }) {
  if (!data?.length) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex items-center justify-center text-sm text-slate-500">
        No cohort data available
      </div>
    )
  }

  const rows = data

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex flex-col">
      <h3 className="text-sm font-semibold text-slate-100 mb-4">
        Cohort Retention Heatmap
      </h3>
      <div className="overflow-auto">
        <table className="w-full text-xs text-center border-collapse">
          <thead>
            <tr>
              <th className="px-3 py-2 text-left text-slate-400">Cohort</th>
              <th className="px-3 py-2 text-left text-slate-400">Service</th>
              <th className="px-2 py-2 text-slate-400">D7</th>
              <th className="px-2 py-2 text-slate-400">D14</th>
              <th className="px-2 py-2 text-slate-400">D30</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={`${row.cohort}-${row.service}-${idx}`} className="border-t border-slate-800/60">
                <td className="px-3 py-2 text-left text-slate-300 whitespace-nowrap">
                  {row.cohort}
                </td>
                <td className="px-3 py-2 text-left text-slate-400 whitespace-nowrap">
                  {row.service}
                </td>
                {["d7", "d14", "d30"].map((k) => (
                  <td key={k} className="px-1 py-1">
                    <div
                      className={`relative group rounded-md px-2 py-1 text-[11px] font-medium ${getCellClasses(row[k])}`}
                    >
                      <span>{row[k].toFixed(1)}%</span>
                      <div className="pointer-events-none absolute -top-1 left-1/2 -translate-x-1/2 -translate-y-full opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="px-2 py-1 text-[10px] rounded bg-slate-900 border border-slate-700 shadow-lg whitespace-nowrap">
                          {row.service} — {row.cohort} · {k.toUpperCase()} {row[k].toFixed(1)}% · {row.total_users} users
                        </div>
                      </div>
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

CohortHeatmap.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      cohort:      PropTypes.string.isRequired,
      service:     PropTypes.string.isRequired,
      total_users: PropTypes.number.isRequired,
      d7:          PropTypes.number.isRequired,
      d14:         PropTypes.number.isRequired,
      d30:         PropTypes.number.isRequired,
    })
  ),
}

