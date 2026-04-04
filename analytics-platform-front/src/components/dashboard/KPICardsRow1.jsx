import PropTypes from "prop-types";
import { Users, UserCheck } from "lucide-react";
import KPICard from "./KPICard";

export default function KPICardsRow1({ data, metrics }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-2 gap-4">
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
    </div>
  );
}

KPICardsRow1.propTypes = {
  data: PropTypes.object.isRequired,
  metrics: PropTypes.object.isRequired,
};
