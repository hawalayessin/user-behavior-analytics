import PropTypes from "prop-types"
import { useNavigate } from "react-router-dom"

const RANK_EMOJI = { 1: "🥇", 2: "🥈", 3: "🥉" }

function HealthBadge({ pct }) {
  if (pct < 5)  return (
    <span className="px-2 py-0.5 rounded-full text-xs border bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
      Healthy
    </span>
  )
  if (pct <= 10) return (
    <span className="px-2 py-0.5 rounded-full text-xs border bg-amber-500/20 text-amber-400 border-amber-500/30">
      At Risk
    </span>
  )
  return (
    <span className="px-2 py-0.5 rounded-full text-xs border bg-red-500/20 text-red-400 border-red-500/30">
      Critical
    </span>
  )
}

function churnColor(pct) {
  if (pct < 5)  return "text-emerald-400"
  if (pct <= 10) return "text-amber-400"
  return "text-red-400"
}

export default function TopServicesTable({ services }) {
  const navigate = useNavigate()

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-5 py-4">
        <h3 className="text-sm font-semibold text-slate-100">Top Services Performance</h3>
        <button
          onClick={() => navigate("/management/services")}
          className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
        >
          View All Services →
        </button>
      </div>

      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-950/50 border-b border-slate-800">
            {["Rank", "Service Name", "Active Subs", "Churned", "Churn Rate", "Health Score"].map((h) => (
              <th key={h} className="px-5 py-3 text-left text-xs uppercase tracking-widest text-slate-500 font-medium">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {services.map((svc, i) => (
            <tr
              key={svc.name}
              className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors"
            >
              <td className="px-5 py-3">
                {RANK_EMOJI[i + 1] ?? (
                  <span className="text-slate-500">#{i + 1}</span>
                )}
              </td>
              <td className="px-5 py-3 text-slate-200 font-medium">{svc.name}</td>
              <td className="px-5 py-3 text-slate-300">{svc.active_subs.toLocaleString()}</td>
              <td className="px-5 py-3 text-slate-400">{svc.churned_subs.toLocaleString()}</td>
              <td className={`px-5 py-3 font-semibold ${churnColor(svc.churn_rate_pct)}`}>
                {svc.churn_rate_pct}%
              </td>
              <td className="px-5 py-3">
                <HealthBadge pct={svc.churn_rate_pct} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

TopServicesTable.propTypes = {
  services: PropTypes.arrayOf(
    PropTypes.shape({
      name:           PropTypes.string.isRequired,
      active_subs:    PropTypes.number.isRequired,
      churned_subs:   PropTypes.number.isRequired,
      churn_rate_pct: PropTypes.number.isRequired,
    })
  ).isRequired,
}

HealthBadge.propTypes = { pct: PropTypes.number.isRequired }