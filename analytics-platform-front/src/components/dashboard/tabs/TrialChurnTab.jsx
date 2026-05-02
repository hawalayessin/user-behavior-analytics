import PropTypes from "prop-types";
import ChurnPieChart from "../ChurnPieChart";
import TrialDropoffChart from "../TrialDropoffChart";
import { useDashboardMetrics } from "../../../hooks/useDashboardMetrics";
import { useTrialDropoffByDay } from "../../../hooks/useTrialDropoffByDay";
import { useChurnBreakdown } from "../../../hooks/useChurnBreakdown";
import { useChurnKPIs } from "../../../hooks/useChurnKPIs";

export default function TrialChurnTab({ data, filters }) {
  const metrics = useDashboardMetrics(data);
  if (!metrics) return null;

  const { churn, subscriptions } = data;

  const { data: dropoff } = useTrialDropoffByDay(filters);
  const { data: churnBreakdown } = useChurnBreakdown(filters);
  const { data: churnKpis } = useChurnKPIs(filters);

  const monthlyChurnPct =
    churnKpis?.monthly_churn_rate?.rate ?? churn?.churn_rate_month_pct ?? 0;
  const voluntaryChurnPct =
    churnKpis?.churn_breakdown?.voluntary?.rate ?? churn?.voluntary_pct ?? 0;
  const technicalChurnPct =
    churnKpis?.churn_breakdown?.technical?.rate ?? churn?.technical_pct ?? 0;
  const churnMessage =
    churnKpis?.churn_breakdown?.message ??
    churnKpis?.monthly_churn_rate?.message ??
    null;

  const dropoffBarData = dropoff
    ? [
        { label: "Day 1\n0–24h", value: dropoff.day1 ?? 0, fill: "#6366F1" },
        { label: "Day 2\n24–48h", value: dropoff.day2 ?? 0, fill: "#F59E0B" },
        { label: "Day 3\n48–72h ⚠", value: dropoff.day3 ?? 0, fill: "#EF4444" },
      ]
    : [
        {
          label: "Day 1\n0–24h",
          value: churn?.dropoff?.day1 ?? 0,
          fill: "#6366F1",
        },
        {
          label: "Day 2\n24–48h",
          value: churn?.dropoff?.day2 ?? 0,
          fill: "#F59E0B",
        },
        {
          label: "Day 3\n48–72h ⚠",
          value: churn?.dropoff?.day3 ?? 0,
          fill: "#EF4444",
        },
      ];

  const churnPieData = churnBreakdown
    ? [
        {
          name: "Voluntary",
          value: churnBreakdown.voluntary_pct ?? voluntaryChurnPct,
          fill: "#EF4444",
        },
        {
          name: "Technical",
          value: churnBreakdown.technical_pct ?? technicalChurnPct,
          fill: "#F59E0B",
        },
      ]
    : [
        {
          name: "Voluntary",
          value: voluntaryChurnPct,
          fill: "#EF4444",
        },
        {
          name: "Technical",
          value: technicalChurnPct,
          fill: "#F59E0B",
        },
      ];

  return (
    <div className="space-y-6">
      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          {
            label: "Trial Conversion → Paid",
            value: `${subscriptions.conversion_rate_pct}%`,
            color: "text-emerald-400",
          },
          {
            label: "Monthly Churn",
            value: `${monthlyChurnPct}%`,
            color: "text-red-400",
          },
          {
            label: "Voluntary Churn",
            value: `${voluntaryChurnPct}%`,
            color: "text-violet-400",
          },
        ].map((kpi) => (
          <div
            key={kpi.label}
            className="bg-slate-900 border border-slate-800 rounded-xl p-5"
          >
            <p className="text-xs text-slate-500 mb-1">{kpi.label}</p>
            <p className={`text-2xl font-bold ${kpi.color}`}>{kpi.value}</p>
          </div>
        ))}
      </div>

      {churnMessage && (
        <div className="bg-slate-800/60 border border-slate-700 text-slate-300 text-sm p-3 rounded-xl">
          {churnMessage}
        </div>
      )}

      {/* Churn Pie + Trial Dropoff */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 items-stretch">
        <div className="lg:col-span-1">
          <ChurnPieChart data={churnPieData} />
        </div>
        <div className="lg:col-span-2">
          <TrialDropoffChart data={dropoffBarData} />
        </div>
      </div>

      {/* Critical zone alert */}
      <div className="bg-amber-500/10 border border-amber-500/20 text-amber-300 text-sm p-4 rounded-xl">
        ⚠️ <strong>Critical zone (48–72h)</strong> — Users who do not convert
        before 72h show ~94% churn probability. Focus retention efforts on the
        first 3 days of the trial.
      </div>
    </div>
  );
}

TrialChurnTab.propTypes = {
  data: PropTypes.object.isRequired,
  filters: PropTypes.object.isRequired,
};
