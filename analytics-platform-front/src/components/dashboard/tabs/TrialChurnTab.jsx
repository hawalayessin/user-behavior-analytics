import PropTypes from "prop-types"
import ChurnPieChart     from "../ChurnPieChart"
import TrialDropoffChart from "../TrialDropoffChart"
import { useDashboardMetrics } from "../../../hooks/useDashboardMetrics"
import { useTrialDropoffByDay } from "../../../hooks/useTrialDropoffByDay"
import { useChurnBreakdown } from "../../../hooks/useChurnBreakdown"

export default function TrialChurnTab({ data, filters }) {
  const metrics = useDashboardMetrics(data)
  if (!metrics) return null

  const { churn, subscriptions } = data

  const { data: dropoff } = useTrialDropoffByDay(filters)
  const { data: churnBreakdown } = useChurnBreakdown(filters)

  const dropoffBarData = dropoff
    ? [
        { label: "Jour 1\n0–24h",     value: dropoff.day1 ?? 0, fill: "#6366F1" },
        { label: "Jour 2\n24–48h",    value: dropoff.day2 ?? 0, fill: "#F59E0B" },
        { label: "Jour 3\n48–72h ⚠", value: dropoff.day3 ?? 0, fill: "#EF4444" },
      ]
    : metrics.dropoffBarData

  const churnPieData = churnBreakdown
    ? [
        { name: "Volontaire", value: churnBreakdown.voluntary_pct ?? 0, fill: "#EF4444" },
        { name: "Technique",  value: churnBreakdown.technical_pct ?? 0, fill: "#F59E0B" },
      ]
    : metrics.churnPieData

  return (
    <div className="space-y-6">
      {/* KPI Row */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Conversion essai → payant", value: `${subscriptions.conversion_rate_pct}%`, color: "text-emerald-400" },
          { label: "Churn mensuel",             value: `${churn.churn_rate_month_pct}%`,         color: "text-red-400"     },
          { label: "Churn volontaire",          value: `${churn.voluntary_pct}%`,                color: "text-violet-400"  },
        ].map((kpi) => (
          <div key={kpi.label} className="bg-[#1A1D27] border border-slate-800 rounded-xl p-5">
            <p className="text-xs text-slate-500 mb-1">{kpi.label}</p>
            <p className={`text-2xl font-bold ${kpi.color}`}>{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Churn Pie + Trial Dropoff */}
      <div className="flex gap-4">
        <ChurnPieChart data={churnPieData} />
        <TrialDropoffChart data={dropoffBarData} />
      </div>

      {/* Critical zone alert */}
      <div className="bg-amber-500/10 border border-amber-500/20 text-amber-300 text-sm p-4 rounded-xl">
        ⚠️ <strong>Zone Critique 48-72h</strong> — Les utilisateurs qui ne convertissent pas
        avant 72h montrent ~94% de probabilité de churn. Concentrez les efforts de rétention
        sur les 3 premiers jours d'essai.
      </div>
    </div>
  )
}

TrialChurnTab.propTypes = {
  data:    PropTypes.object.isRequired,
  filters: PropTypes.object.isRequired,
}