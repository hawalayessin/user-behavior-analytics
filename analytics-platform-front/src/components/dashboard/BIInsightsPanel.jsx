import PropTypes from "prop-types"

const SEVERITY_STYLES = {
  red:   "bg-red-500/10 border-red-500/20 text-red-200",
  amber: "bg-amber-500/10 border-amber-500/20 text-amber-200",
  green: "bg-emerald-500/10 border-emerald-500/20 text-emerald-200",
}

function InsightCard({ icon, title, message, severity }) {
  return (
    <div className={`rounded-xl border p-4 ${SEVERITY_STYLES[severity]}`}>
      <p className="font-semibold text-sm mb-1">{icon} {title}</p>
      <p className="text-xs leading-relaxed opacity-90">{message}</p>
    </div>
  )
}

export default function BIInsightsPanel({ insights }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-slate-100">🔍 Automated BI Insights</h3>
        <p className="text-xs text-slate-500 mt-0.5">
          Real-time findings based on current platform data
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {insights.map((insight) => (
          <InsightCard key={insight.id} {...insight} />
        ))}
      </div>
    </div>
  )
}

BIInsightsPanel.propTypes = {
  insights: PropTypes.arrayOf(
    PropTypes.shape({
      id:       PropTypes.string.isRequired,
      severity: PropTypes.oneOf(["red", "amber", "green"]).isRequired,
      icon:     PropTypes.string.isRequired,
      title:    PropTypes.string.isRequired,
      message:  PropTypes.string.isRequired,
    })
  ).isRequired,
}

InsightCard.propTypes = {
  icon:     PropTypes.string.isRequired,
  title:    PropTypes.string.isRequired,
  message:  PropTypes.string.isRequired,
  severity: PropTypes.oneOf(["red", "amber", "green"]).isRequired,
}