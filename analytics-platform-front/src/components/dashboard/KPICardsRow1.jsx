import PropTypes from "prop-types";
import { Users, UserCheck, Wallet, TrendingDown } from "lucide-react";
import KPICard from "./KPICard";

export default function KPICardsRow1({ data, metrics }) {
  const total = data.subscriptions.total || 0;
  const monthlyRevenue = data.revenue?.mrr || 0;
  const churnRate = data.churn?.churn_rate_month_pct || 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <KPICard
        title="Total Users"
        value={(data.users?.total || 0).toLocaleString()}
        subtitle="All registered users"
        icon={Users}
        iconColor="#6366F1"
        iconBg="bg-violet-500/20"
      />
      <KPICard
        title="Active Subscriptions"
        value={(data.subscriptions.active || 0).toLocaleString()}
        subtitle={`${total > 0 ? Math.round(((data.subscriptions.active || 0) * 100) / total) : 0}% of confirmed subs`}
        icon={UserCheck}
        iconColor="#10B981"
        iconBg="bg-emerald-500/20"
      />
      <KPICard
        title="Monthly Revenue"
        value={`${monthlyRevenue.toLocaleString()} TND`}
        subtitle="Recurring monthly revenue (MRR)"
        icon={Wallet}
        iconColor="#10B981"
        iconBg="bg-emerald-500/20"
      />
      <KPICard
        title="Churn Rate"
        value={`${Number(churnRate).toFixed(1)}%`}
        subtitle="Monthly churn rate"
        icon={TrendingDown}
        iconColor="#EF4444"
        iconBg="bg-red-500/20"
      />
    </div>
  );
}

KPICardsRow1.propTypes = {
  data: PropTypes.object.isRequired,
  metrics: PropTypes.object.isRequired,
};
