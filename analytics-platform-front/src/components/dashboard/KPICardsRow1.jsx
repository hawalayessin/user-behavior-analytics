import PropTypes from "prop-types"
import { Users, UserCheck, DollarSign, UserMinus } from "lucide-react"
import KPICard from "./KPICard"

export default function KPICardsRow1({ data, metrics }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <KPICard
        title="Total Users"
        value={data.users.total.toLocaleString()}
        subtitle={`+${data.users.new_last_30_days} new this month`}
        icon={Users}
        iconColor="#6366F1"
        iconBg="bg-indigo-500/20"
        trend={5.2}
        trendLabel="vs last month"
      />
      <KPICard
        title="Active Subscribers"
        value={data.subscriptions.active.toLocaleString()}
        subtitle={`${data.subscriptions.trial} in free trial`}
        icon={UserCheck}
        iconColor="#10B981"
        iconBg="bg-emerald-500/20"
        trend={3.1}
      />
      <KPICard
        title="Monthly Revenue (MRR)"
        value={`${data.revenue.mrr.toLocaleString()} DT`}
        subtitle={`ARPU: ${data.revenue.arpu_current_month} DT/user`}
        icon={DollarSign}
        iconColor="#8B5CF6"
        iconBg="bg-violet-500/20"
        trend={8.4}
      />
      <KPICard
        title="Monthly Churn Rate"
        value={`${data.churn.churn_rate_month_pct}%`}
        subtitle={`${data.churn.total} total unsubscriptions`}
        icon={UserMinus}
        iconColor="#EF4444"
        iconBg="bg-red-500/20"
        trend={-0.5}
        alert={metrics.isChurnCritical}
      />
    </div>
  )
}

KPICardsRow1.propTypes = {
  data:    PropTypes.object.isRequired,
  metrics: PropTypes.object.isRequired,
}