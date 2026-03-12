import PropTypes from "prop-types"
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from "recharts"
import SubscriptionDonutChart from "../SubscriptionDonutChart"
import { useDashboardMetrics } from "../../../hooks/useDashboardMetrics"

const TOOLTIP_STYLE = {
  contentStyle: { backgroundColor: "#1E293B", border: "1px solid #334155", borderRadius: 8 },
  labelStyle:   { color: "#94A3B8" },
  itemStyle:    { color: "#F1F5F9" },
}

export default function RevenueTab({ data }) {
  const metrics = useDashboardMetrics(data)
  if (!metrics) return null

  const { revenue, subscriptions } = data

  const billingData = [
    { label: "Facturation", success: revenue.billing_success, failed: revenue.billing_failed },
  ]

  return (
    <div className="space-y-6">
      {/* KPI Row */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "ARPU",                  value: `${revenue.arpu_current_month ?? 0} DT`,    color: "text-violet-400" },
          { label: "MRR",                   value: `${revenue.mrr ?? 0} DT`,                   color: "text-emerald-400" },
          { label: "Paiements réussis",     value: revenue.billing_success.toLocaleString(),   color: "text-emerald-400" },
          { label: "Paiements échoués",     value: revenue.billing_failed.toLocaleString(),    color: "text-red-400"     },
        ].map((kpi) => (
          <div key={kpi.label} className="bg-[#1A1D27] border border-slate-800 rounded-xl p-5">
            <p className="text-xs text-slate-500 mb-1">{kpi.label}</p>
            <p className={`text-xl font-bold ${kpi.color}`}>{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Donut + Billing bar */}
      <div className="flex gap-4">
        <SubscriptionDonutChart
          data={metrics.subscriptionPieData}
          total={subscriptions.total}
        />

        <div className="bg-[#1A1D27] border border-slate-800 rounded-xl p-5 flex-1">
          <h3 className="text-sm font-semibold text-slate-100 mb-4">
            Billing — Succès vs Échecs
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={billingData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
              <XAxis dataKey="label" tick={{ fill: "#94A3B8", fontSize: 12 }} />
              <YAxis tick={{ fill: "#94A3B8", fontSize: 12 }} />
              <Tooltip {...TOOLTIP_STYLE} />
              <Legend wrapperStyle={{ color: "#94A3B8", fontSize: 12 }} />
              <Bar dataKey="success" name="Succès"  fill="#10B981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="failed"  name="Échecs"  fill="#EF4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}

RevenueTab.propTypes = {
  data:    PropTypes.object.isRequired,
  filters: PropTypes.object.isRequired,
}