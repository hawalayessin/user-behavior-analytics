import PropTypes from "prop-types";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export default function KPICard({
  title,
  value,
  subtitle,
  icon: Icon,
  iconColor,
  iconBg,
  trend,
  trendLabel,
  alert = false,
  subtitleColor,
}) {
  const TrendIcon = trend > 0 ? TrendingUp : trend < 0 ? TrendingDown : Minus;
  const trendColor =
    trend > 0
      ? "text-emerald-400"
      : trend < 0
        ? "text-red-400"
        : "text-slate-500";
  const trendSign = trend > 0 ? "+" : "";

  return (
    <div
      className={`
        rounded-xl p-5 h-full flex flex-col gap-3
        ${alert ? "border-red-500/50" : ""}
      `}
      style={{
        backgroundColor: alert
          ? "var(--color-danger-bg)"
          : "var(--color-bg-card)",
        border: `1px solid ${alert ? "var(--color-danger)" : "var(--color-border)"}`,
        boxShadow: "var(--color-card-shadow)",
      }}
    >
      <div className="flex items-start justify-between">
        <p
          className="text-sm font-medium"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {title}
        </p>
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center ${iconBg}`}
        >
          <Icon size={20} style={{ color: iconColor }} />
        </div>
      </div>

      <p
        className="text-2xl font-bold tracking-tight"
        style={{ color: "var(--color-text-primary)" }}
      >
        {value}
      </p>

      <p
        className={`text-xs ${subtitleColor ?? ""}`}
        style={{ color: subtitleColor ? undefined : "var(--color-text-muted)" }}
      >
        {subtitle}
      </p>

      {trend !== undefined && (
        <div className={`flex items-center gap-1 text-xs ${trendColor}`}>
          <TrendIcon size={13} />
          <span>
            {trendSign}
            {trend}%
          </span>
          {trendLabel && (
            <span className="ml-1" style={{ color: "var(--color-text-muted)" }}>
              {trendLabel}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

KPICard.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  subtitle: PropTypes.string,
  icon: PropTypes.elementType.isRequired,
  iconColor: PropTypes.string.isRequired,
  iconBg: PropTypes.string.isRequired,
  trend: PropTypes.number,
  trendLabel: PropTypes.string,
  alert: PropTypes.bool,
  subtitleColor: PropTypes.string,
};
