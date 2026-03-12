import PropTypes from "prop-types"
import { Zap, ArrowRightLeft, AlertCircle } from "lucide-react"
import KPICard from "./KPICard"

export default function KPICardsRow2({ data, metrics }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <KPICard
        title="DAU Today"
        value={data.engagement.dau_today.toLocaleString()}
        subtitle={`WAU: ${data.engagement.wau_current_week} · MAU: ${data.engagement.mau_current_month}`}
        icon={Zap}
        iconColor="#6366F1"
        iconBg="bg-indigo-500/20"
      />
      <KPICard
        title="Trial Conversion Rate"
        value={`${data.subscriptions.conversion_rate_pct}%`}
        subtitle={
          metrics.isConversionBelowBM
            ? "↓ Below benchmark (18–25%) — action needed"
            : "✓ Above benchmark (18–25%)"
        }
        subtitleColor={metrics.isConversionBelowBM ? "text-red-400" : "text-emerald-400"}
        icon={ArrowRightLeft}
        iconColor="#10B981"
        iconBg="bg-emerald-500/20"
        alert={metrics.isConversionBelowBM}
      />
      <KPICard
        title="Billing Failure Rate"
        value={`${data.revenue.failed_pct}%`}
        subtitle={`${data.revenue.billing_failed} failed / ${data.revenue.billing_success} success`}
        icon={AlertCircle}
        iconColor="#EF4444"
        iconBg="bg-red-500/20"
        alert={metrics.isBillingAlert}
        trend={-0.4}
      />
    </div>
  )
}

KPICardsRow2.propTypes = {
  data:    PropTypes.object.isRequired,
  metrics: PropTypes.object.isRequired,
}