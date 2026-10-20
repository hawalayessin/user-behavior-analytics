import PropTypes from "prop-types";
import { Zap, ArrowRightLeft } from "lucide-react";
import KPICard from "./KPICard";

export default function KPICardsRow2({ data, metrics, filters }) {
  const isAllTime = !filters?.start_date && !filters?.end_date;
  const dauValue = isAllTime
    ? (data.engagement.max_dau_period ?? data.engagement.dau_today ?? 0)
    : (data.engagement.dau_today ?? 0);
  const dauTitle = isAllTime ? "Peak DAU" : "DAU Today";
  const dauSubtitle = isAllTime
    ? `Max daily active users in DB - Avg: ${Math.round(data.engagement.avg_dau_period ?? 0).toLocaleString()}`
    : `WAU: ${data.engagement.wau_current_week} - MAU: ${data.engagement.mau_current_month}`;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <KPICard
        title={dauTitle}
        value={dauValue.toLocaleString()}
        subtitle={dauSubtitle}
        icon={Zap}
        iconColor="#6366F1"
        iconBg="bg-indigo-500/20"
      />
      <KPICard
        title="Trial Conversion Rate"
        value={`${data.subscriptions.conversion_rate_pct}%`}
        subtitle={
          metrics.isConversionBelowBM
            ? "Below benchmark (18-25%) - action needed"
            : "Above benchmark (18-25%)"
        }
        subtitleColor={
          metrics.isConversionBelowBM ? "text-red-400" : "text-emerald-400"
        }
        icon={ArrowRightLeft}
        iconColor="#10B981"
        iconBg="bg-emerald-500/20"
        alert={metrics.isConversionBelowBM}
      />
    </div>
  );
}

KPICardsRow2.propTypes = {
  data: PropTypes.object.isRequired,
  metrics: PropTypes.object.isRequired,
  filters: PropTypes.object,
};
