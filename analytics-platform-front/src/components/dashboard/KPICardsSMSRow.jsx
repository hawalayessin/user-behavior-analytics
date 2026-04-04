import PropTypes from "prop-types";
import { KeyRound, Send, MessageSquare } from "lucide-react";
import KPICard from "./KPICard";

export default function KPICardsSMSRow({ data }) {
  const sms = data?.sms ?? {};
  const templatesPerService = Number(sms.templates_per_service ?? 0);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <KPICard
        title="OTP Templates"
        value={`${Number(sms.otp_templates_pct ?? 0).toFixed(1)}%`}
        subtitle="Templates with OTP code"
        icon={KeyRound}
        iconColor="#F59E0B"
        iconBg="bg-amber-500/20"
        trend={Number(sms.otp_rate_trend_pct ?? 0)}
        trendLabel="vs previous period"
      />
      <KPICard
        title="Activation Templates"
        value={`${Number(sms.activation_templates_pct ?? 0).toFixed(1)}%`}
        subtitle="Templates flagged as activation"
        icon={Send}
        iconColor="#10B981"
        iconBg="bg-emerald-500/20"
        trend={Number(sms.activation_rate_trend_pct ?? 0)}
        trendLabel="vs previous period"
      />
      <KPICard
        title="Templates per Service"
        value={templatesPerService.toFixed(1)}
        subtitle="Average across services"
        icon={MessageSquare}
        iconColor="#6366F1"
        iconBg="bg-indigo-500/20"
      />
    </div>
  );
}

KPICardsSMSRow.propTypes = {
  data: PropTypes.object.isRequired,
};
