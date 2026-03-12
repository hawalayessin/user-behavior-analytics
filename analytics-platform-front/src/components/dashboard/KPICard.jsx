import PropTypes from "prop-types"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"

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
  const TrendIcon   = trend > 0 ? TrendingUp : trend < 0 ? TrendingDown : Minus
  const trendColor  = trend > 0 ? "text-emerald-400" : trend < 0 ? "text-red-400" : "text-slate-500"
  const trendSign   = trend > 0 ? "+" : ""

  return (
    <div
      className={`
        bg-slate-900 rounded-xl border p-5 h-full flex flex-col gap-3
        ${alert ? "border-red-500/50 bg-red-500/5" : "border-slate-800"}
      `}
    >
      <div className="flex items-start justify-between">
        <p className="text-sm text-slate-400 font-medium">{title}</p>
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${iconBg}`}>
          <Icon size={20} style={{ color: iconColor }} />
        </div>
      </div>

      <p className="text-2xl font-bold text-slate-100 tracking-tight">{value}</p>

      <p className={`text-xs ${subtitleColor ?? "text-slate-500"}`}>{subtitle}</p>

      {trend !== undefined && (
        <div className={`flex items-center gap-1 text-xs ${trendColor}`}>
          <TrendIcon size={13} />
          <span>{trendSign}{trend}%</span>
          {trendLabel && <span className="text-slate-500 ml-1">{trendLabel}</span>}
        </div>
      )}
    </div>
  )
}

KPICard.propTypes = {
  title:         PropTypes.string.isRequired,
  value:         PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  subtitle:      PropTypes.string,
  icon:          PropTypes.elementType.isRequired,
  iconColor:     PropTypes.string.isRequired,
  iconBg:        PropTypes.string.isRequired,
  trend:         PropTypes.number,
  trendLabel:    PropTypes.string,
  alert:         PropTypes.bool,
  subtitleColor: PropTypes.string,
}