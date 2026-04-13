import PropTypes from "prop-types";
import { Info, TrendingUp, TrendingDown, Minus } from "lucide-react";
import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  XAxis,
  YAxis,
} from "recharts";

const TOOLTIP_TEXT =
  "NRR measures how much of last month's revenue was retained this month from existing subscribers. 100% = perfect retention. >100% = revenue growth. <100% = revenue loss from existing users.";

function currency(value) {
  return `$${Number(value || 0).toLocaleString()}`;
}

function getStatus(nrrPercent) {
  if (nrrPercent > 200) {
    return {
      label: "Check Data",
      className: "bg-amber-500/20 text-amber-300 border-amber-500/40",
      dot: "⚠️",
    };
  }
  if (nrrPercent >= 110) {
    return {
      label: "Strong Growth",
      className: "bg-sky-500/20 text-sky-300 border-sky-500/40",
      dot: "🔵",
    };
  }
  if (nrrPercent >= 90) {
    return {
      label: "Healthy",
      className: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
      dot: "🟢",
    };
  }
  if (nrrPercent >= 70) {
    return {
      label: "At Risk",
      className: "bg-orange-500/20 text-orange-300 border-orange-500/40",
      dot: "🟠",
    };
  }
  return {
    label: "Critical",
    className: "bg-red-500/20 text-red-300 border-red-500/40",
    dot: "🔴",
  };
}

function BreakdownTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const item = payload[0]?.payload;
  return (
    <div className="rounded-md border border-slate-600 bg-slate-800 px-2 py-1 text-xs text-slate-100 shadow-lg">
      <div className="font-semibold">{item?.label}</div>
      <div>{currency(item?.value)}</div>
    </div>
  );
}

BreakdownTooltip.propTypes = {
  active: PropTypes.bool,
  payload: PropTypes.array,
};

export default function NRRCard({ data, loading, error, size = "compact" }) {
  const isExpanded = size === "expanded";

  if (loading) {
    return (
      <div
        className={`bg-slate-900 rounded-xl border border-slate-800 h-full animate-pulse ${isExpanded ? "p-6" : "p-4"}`}
      >
        <div
          className={`bg-slate-800 rounded w-2/3 ${isExpanded ? "h-5 mb-4" : "h-4 mb-3"}`}
        />
        <div
          className={`bg-slate-800 rounded w-1/3 ${isExpanded ? "h-10 mb-4" : "h-7 mb-3"}`}
        />
        <div className="h-2 bg-slate-800 rounded w-full mb-2" />
        <div
          className={`bg-slate-800 rounded w-full mb-2 ${isExpanded ? "h-28" : "h-16"}`}
        />
        <div
          className={`bg-slate-800 rounded w-1/2 ${isExpanded ? "h-5" : "h-4"}`}
        />
      </div>
    );
  }

  const nrr = Number(data?.nrr_percent ?? 0);
  const delta = Number((nrr - 100).toFixed(1));
  const clampedNrr = Math.min(Math.max(nrr, 0), 150);
  const cursorPosition = (clampedNrr / 150) * 100;
  const status = getStatus(nrr);

  const trendIcon = delta > 0 ? TrendingUp : delta < 0 ? TrendingDown : Minus;
  const TrendIcon = trendIcon;
  const trendColor =
    delta > 0
      ? "text-emerald-300"
      : delta < 0
        ? "text-red-300"
        : "text-slate-300";
  const trendSign = delta > 0 ? "+" : "";

  const breakdownData = [
    {
      label: "Last Month",
      value: Number(data?.revenue_start ?? 0),
      fill: "#6366F1",
    },
    {
      label: "Renewed",
      value: Number(data?.revenue_renewed ?? 0),
      fill: "#22C55E",
    },
    {
      label: "Churned",
      value: Math.abs(Number(data?.revenue_churned ?? 0)),
      fill: "#EF4444",
    },
  ];
  const maxValue = Math.max(1, ...breakdownData.map((d) => d.value));

  return (
    <div
      className={`bg-slate-900 rounded-xl border border-slate-800 h-full ${isExpanded ? "p-6 space-y-5" : "p-4 space-y-3"}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3
              className={`${isExpanded ? "text-sm" : "text-xs"} text-slate-300 font-semibold`}
            >
              📊 Net Revenue Retention (NRR)
            </h3>
            <div className="group relative">
              <Info
                size={isExpanded ? 16 : 14}
                className="text-slate-400 cursor-help"
              />
              <div className="invisible group-hover:visible absolute z-20 top-5 right-0 w-72 rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-xs text-slate-200 shadow-xl">
                {TOOLTIP_TEXT}
              </div>
            </div>
          </div>
          <p
            className={`${isExpanded ? "text-xs" : "text-[11px]"} text-slate-500 mt-1`}
          >
            % of last month revenue kept this month
          </p>
        </div>
      </div>

      {error ? (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-200">
          NRR unavailable: {error}
        </div>
      ) : (
        <>
          <div className="text-center">
            <div
              className={`${isExpanded ? "text-5xl" : "text-3xl"} font-black text-slate-100 leading-none`}
            >
              {nrr.toFixed(1)}%
            </div>
            <div
              className={`${isExpanded ? "mt-2.5 text-sm" : "mt-1.5 text-xs"} inline-flex items-center gap-1.5 ${trendColor}`}
            >
              <TrendIcon size={isExpanded ? 15 : 12} />
              <span>
                {trendSign}
                {delta.toFixed(1)}% vs last month
              </span>
            </div>
          </div>

          <div>
            <div className="nrr-bar-track relative">
              <div className="nrr-zone-red" />
              <div className="nrr-zone-orange" />
              <div className="nrr-zone-green" />
              <div className="nrr-zone-blue" />
              <div
                className="nrr-cursor"
                style={{ left: `${cursorPosition}%` }}
              />
              {nrr > 150 && (
                <span className="absolute -top-5 right-0 text-[10px] font-semibold text-sky-400">
                  ▶ {nrr.toFixed(1)}%
                </span>
              )}
            </div>
            <div
              className={`${isExpanded ? "mt-2.5 text-[11px]" : "mt-1.5 text-[9px]"} flex items-center justify-between text-slate-500`}
            >
              <span>0% Danger</span>
              <span>100% Healthy</span>
              <span>150% Growth</span>
            </div>
          </div>

          <div
            className={`border-t border-slate-800 ${isExpanded ? "pt-4" : "pt-2.5"}`}
          >
            <p
              className={`${isExpanded ? "text-sm mb-3" : "text-[11px] mb-1.5"} font-semibold text-slate-300`}
            >
              Revenue Breakdown
            </p>
            <div className={`${isExpanded ? "h-36" : "h-20"} w-full`}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  layout="vertical"
                  data={breakdownData}
                  margin={{ top: 0, right: 8, left: 8, bottom: 0 }}
                >
                  <XAxis
                    type="number"
                    domain={[0, maxValue * 1.1]}
                    tick={{ fill: "#94A3B8", fontSize: isExpanded ? 11 : 10 }}
                    tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                  />
                  <YAxis
                    type="category"
                    dataKey="label"
                    width={isExpanded ? 90 : 68}
                    tick={{ fill: "#94A3B8", fontSize: isExpanded ? 12 : 10 }}
                  />
                  <RechartsTooltip content={<BreakdownTooltip />} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={24}>
                    {breakdownData.map((item) => (
                      <Cell key={item.label} fill={item.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div
              className={`${isExpanded ? "mt-3 space-y-1 text-sm" : "mt-1 space-y-0.5 text-[11px]"} text-slate-400`}
            >
              <div className="flex items-center justify-between">
                <span>Start</span>
                <span>{currency(data?.revenue_start)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Renewed</span>
                <span>{currency(data?.revenue_renewed)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Churned</span>
                <span>-{currency(data?.revenue_churned)}</span>
              </div>
            </div>
          </div>

          <div
            className={`${isExpanded ? "pt-4" : "pt-2.5"} border-t border-slate-800 flex items-center justify-between gap-3`}
          >
            <span
              className={`inline-flex items-center gap-1 rounded-full border font-semibold ${status.className} ${isExpanded ? "px-3 py-1 text-xs" : "px-2 py-0.5 text-[11px]"}`}
            >
              <span>{status.dot}</span>
              <span>{status.label}</span>
            </span>
            <span
              className={`${isExpanded ? "text-xs" : "text-[11px]"} text-slate-400`}
            >
              Period: {data?.period_label ?? "N/A"}
            </span>
          </div>
        </>
      )}
    </div>
  );
}

NRRCard.propTypes = {
  data: PropTypes.shape({
    nrr_percent: PropTypes.number,
    revenue_start: PropTypes.number,
    revenue_renewed: PropTypes.number,
    revenue_churned: PropTypes.number,
    period_label: PropTypes.string,
  }),
  loading: PropTypes.bool,
  error: PropTypes.string,
  size: PropTypes.oneOf(["compact", "expanded"]),
};
