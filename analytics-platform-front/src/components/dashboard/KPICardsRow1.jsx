import PropTypes from "prop-types";
import { Users, UserCheck, AlertTriangle, Clock3 } from "lucide-react";
import KPICard from "./KPICard";

export default function KPICardsRow1({ data, metrics }) {
  const total = data.subscriptions.total || 0;
  const pending = data.subscriptions.pending || 0;
  const totalWithPending = data.subscriptions.total_with_pending || total;

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
        title="At Risk (Billing)"
        value={(data.subscriptions.billing_failed || 0).toLocaleString()}
        subtitle={`${(data.subscriptions.at_risk_users || 0).toLocaleString()} users at risk`}
        icon={AlertTriangle}
        iconColor="#F59E0B"
        iconBg="bg-amber-500/20"
      />
      <KPICard
        title="Pending OTP"
        value={pending.toLocaleString()}
        subtitle={`${totalWithPending > 0 ? Math.round((pending * 100) / totalWithPending) : 0}% of total pipeline`}
        icon={Clock3}
        iconColor="#94A3B8"
        iconBg="bg-slate-500/20"
      />
    </div>
  );
}

KPICardsRow1.propTypes = {
  data: PropTypes.object.isRequired,
  metrics: PropTypes.object.isRequired,
};
