import PropTypes from "prop-types";
import {
  AlertTriangle,
  BarChart3,
  Circle,
  Info,
  Minus,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

const TOOLTIP_TEXT =
  "NRR measures how much of last month's revenue was retained this month from existing subscribers. 100% = perfect retention. >100% = revenue growth. <100% = revenue loss from existing users.";

function currency(value) {
  return `${Number(value || 0).toLocaleString()} DT`;
}

function currencyAbs(value) {
  return `${Math.abs(Number(value || 0)).toLocaleString()} DT`;
}

function getStatus(nrrPercent) {
  if (nrrPercent > 200) {
    return {
      label: "Check Data",
      className: "bg-amber-500/20 text-amber-300 border-amber-500/40",
      icon: AlertTriangle,
    };
  }
  if (nrrPercent >= 110) {
    return {
      label: "Strong Growth",
      className: "bg-sky-500/20 text-sky-300 border-sky-500/40",
      icon: Circle,
    };
  }
  if (nrrPercent >= 90) {
    return {
      label: "Healthy",
      className: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
      icon: Circle,
    };
  }
  if (nrrPercent >= 70) {
    return {
      label: "At Risk",
      className: "bg-orange-500/20 text-orange-300 border-orange-500/40",
      icon: Circle,
    };
  }
  return {
    label: "Critical",
    className: "bg-red-500/20 text-red-300 border-red-500/40",
    icon: Circle,
  };
}

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
  const hasBaseline = data?.is_available ?? Number(data?.revenue_start ?? 0) > 0;
  const delta = Number((nrr - 100).toFixed(1));
  const clampedNrr = Math.min(Math.max(nrr, 0), 150);
  const cursorPosition = (clampedNrr / 150) * 100;
  const status = hasBaseline
    ? getStatus(nrr)
    : {
        label: "No baseline",
        className: "bg-amber-500/20 text-amber-300 border-amber-500/40",
        icon: AlertTriangle,
      };
  const StatusIcon = status.icon;

  const trendIcon = delta > 0 ? TrendingUp : delta < 0 ? TrendingDown : Minus;
  const TrendIcon = hasBaseline ? trendIcon : AlertTriangle;
  const trendColor =
    !hasBaseline
      ? "text-amber-300"
      : delta > 0
      ? "text-emerald-300"
      : delta < 0
        ? "text-red-300"
        : "text-slate-300";
  const trendSign = delta > 0 ? "+" : "";
  const startRevenue = Number(data?.revenue_start ?? 0);
  const renewedRevenue = Number(data?.revenue_renewed ?? 0);
  const churnedRevenue = Math.abs(Number(data?.revenue_churned ?? 0));
  const currentRevenue = Number(data?.revenue_current ?? 0);
  const retainedPct = startRevenue > 0 ? (renewedRevenue / startRevenue) * 100 : 0;
  const churnedPct = startRevenue > 0 ? (churnedRevenue / startRevenue) * 100 : 0;
  const retainedWidth = Math.min(Math.max(retainedPct, 0), 100);
  const churnedWidth = Math.min(Math.max(churnedPct, 0), 100);
  const currentVsPreviousPct = startRevenue > 0 ? (currentRevenue / startRevenue) * 100 : 0;

  return (
    <div
      className={`bg-slate-900 rounded-xl border border-slate-800 h-full ${isExpanded ? "p-6 space-y-5" : "p-4 space-y-3"}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3
              className={`${isExpanded ? "text-sm" : "text-xs"} text-slate-300 font-semibold inline-flex items-center gap-1.5`}
            >
              <BarChart3 size={isExpanded ? 15 : 13} />
              Net Revenue Retention (NRR)
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
              {hasBaseline ? `${nrr.toFixed(1)}%` : "N/A"}
            </div>
            <div
              className={`${isExpanded ? "mt-2.5 text-sm" : "mt-1.5 text-xs"} inline-flex items-center gap-1.5 ${trendColor}`}
            >
              <TrendIcon size={isExpanded ? 15 : 12} />
              {hasBaseline ? (
                <span>
                  {trendSign}
                  {delta.toFixed(1)}% vs last month
                </span>
              ) : (
                <span>No previous-month revenue baseline</span>
              )}
            </div>
          </div>

          {hasBaseline ? (
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
          ) : (
            <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-100">
              {data?.baseline_note ??
                "NRR cannot be calculated because last month revenue is 0 DT for this scope."}
            </div>
          )}

          <div
            className={`border-t border-slate-800 ${isExpanded ? "pt-4" : "pt-2.5"}`}
          >
            <p
              className={`${isExpanded ? "text-sm mb-3" : "text-[11px] mb-1.5"} font-semibold text-slate-300`}
            >
              Revenue Retention Flow
            </p>
            {hasBaseline ? (
              <div className="space-y-3">
                <div className="rounded-lg border border-slate-800 bg-slate-950/45 p-3">
                  <div className="flex items-center justify-between gap-3 text-xs">
                    <span className="text-slate-400">Last month baseline</span>
                    <span className="font-semibold text-slate-100">
                      {currency(startRevenue)}
                    </span>
                  </div>
                  <div className="mt-3 flex h-3 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full bg-emerald-500"
                      style={{ width: `${retainedWidth}%` }}
                    />
                    <div
                      className="h-full bg-red-500"
                      style={{ width: `${churnedWidth}%` }}
                    />
                  </div>
                  <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-500">
                    <span>{retainedPct.toFixed(1)}% retained</span>
                    <span>{churnedPct.toFixed(1)}% lost</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                  <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 p-3">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-semibold text-emerald-200">
                        Retained revenue
                      </span>
                      <span className="text-xs text-emerald-300">
                        {retainedPct.toFixed(1)}%
                      </span>
                    </div>
                    <div className="mt-2 text-lg font-black text-slate-100">
                      {currency(renewedRevenue)}
                    </div>
                    <div className="mt-2 h-1.5 rounded-full bg-slate-800">
                      <div
                        className="h-full rounded-full bg-emerald-400"
                        style={{ width: `${retainedWidth}%` }}
                      />
                    </div>
                  </div>

                  <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-semibold text-red-200">
                        Revenue lost
                      </span>
                      <span className="text-xs text-red-300">
                        {churnedPct.toFixed(1)}%
                      </span>
                    </div>
                    <div className="mt-2 text-lg font-black text-slate-100">
                      -{currencyAbs(churnedRevenue)}
                    </div>
                    <div className="mt-2 h-1.5 rounded-full bg-slate-800">
                      <div
                        className="h-full rounded-full bg-red-400"
                        style={{ width: `${churnedWidth}%` }}
                      />
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/35 px-3 py-2 text-xs text-slate-400">
                  <span>Current month total revenue</span>
                  <span className="font-semibold text-slate-100">
                    {currency(currentRevenue)}
                    <span className="ml-2 text-slate-500">
                      ({currentVsPreviousPct.toFixed(1)}% of baseline)
                    </span>
                  </span>
                </div>
              </div>
            ) : (
              <div
                className={`${isExpanded ? "mt-3 space-y-2 text-sm" : "mt-1 space-y-2 text-[11px]"} text-slate-400`}
              >
                <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/45 px-3 py-2">
                  <span>Previous month</span>
                  <span className="font-semibold text-slate-100">
                    {currency(startRevenue)}
                  </span>
                </div>
                <div className="flex items-center justify-between rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-3 py-2">
                  <span>Current month</span>
                  <span className="font-semibold text-slate-100">
                    {currency(currentRevenue)}
                  </span>
                </div>
              </div>
            )}
          </div>

          <div
            className={`${isExpanded ? "pt-4" : "pt-2.5"} border-t border-slate-800 flex items-center justify-between gap-3`}
          >
            <span
              className={`inline-flex items-center gap-1 rounded-full border font-semibold ${status.className} ${isExpanded ? "px-3 py-1 text-xs" : "px-2 py-0.5 text-[11px]"}`}
            >
              <StatusIcon
                size={isExpanded ? 12 : 10}
                className={StatusIcon === Circle ? "fill-current" : ""}
              />
              <span>{status.label}</span>
            </span>
            <span
              className={`${isExpanded ? "text-xs" : "text-[11px]"} shrink-0 whitespace-nowrap text-right text-slate-400`}
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
    revenue_current: PropTypes.number,
    revenue_renewed: PropTypes.number,
    revenue_churned: PropTypes.number,
    period_label: PropTypes.string,
    is_available: PropTypes.bool,
    baseline_note: PropTypes.string,
  }),
  loading: PropTypes.bool,
  error: PropTypes.string,
  size: PropTypes.oneOf(["compact", "expanded"]),
};
