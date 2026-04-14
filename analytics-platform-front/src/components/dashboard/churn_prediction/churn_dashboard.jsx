import { useCallback, useMemo, useState } from "react";
import { AlertCircle, RotateCcw } from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

import { useAuth } from "../../../context/AuthContext";
import { useToast } from "../../../hooks/useToast";

import KPICard from "../KPICard";
import { useChurnPredictionMetrics } from "../../../hooks/useChurnPredictionMetrics";
import { useChurnPredictionScores } from "../../../hooks/useChurnPredictionScores";
import { useChurnPredictionTrain } from "../../../hooks/useChurnPredictionTrain";
import { useChurnModelGovernance } from "../../../hooks/useChurnModelGovernance";

function Card({ title, subtitle, right, children }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-start justify-between gap-3 mb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-100">{title}</h3>
          {subtitle && (
            <p className="text-sm text-slate-400 mt-1">{subtitle}</p>
          )}
        </div>
        {right}
      </div>
      {children}
    </div>
  );
}

export default function ChurnPredictionDashboard() {
  const { isAdmin } = useAuth();
  const { showToast, Toast } = useToast();

  const [topN, setTopN] = useState(10);
  const [threshold, setThreshold] = useState(0.4);

  // Memoize options to prevent unnecessary hook re-triggers
  const scoresOptions = useMemo(
    () => ({ top: topN, threshold }),
    [topN, threshold],
  );

  const metrics = useChurnPredictionMetrics();
  const scores = useChurnPredictionScores(scoresOptions);
  const trainHook = useChurnPredictionTrain();
  const governance = useChurnModelGovernance();

  const anyError = metrics.error || scores.error || governance.error;

  const distributionSeries = useMemo(() => {
    const d = scores.data?.distribution ?? [];
    return d.map((x) => ({
      risk_category: x.risk_category,
      count: Number(x.count ?? 0),
    }));
  }, [scores.data]);

  const coefficientTop = useMemo(() => {
    const coeffs = metrics.data?.coefficients ?? {};
    const entries = Object.entries(coeffs).map(([k, v]) => ({
      feature: k,
      coefficient: Number(v),
    }));
    entries.sort((a, b) => Math.abs(b.coefficient) - Math.abs(a.coefficient));
    return entries.slice(0, 6);
  }, [metrics.data]);

  const handleRefresh = async () => {
    await Promise.all([
      metrics.refetch(),
      scores.refetch(),
      governance.refetch(),
    ]);
    showToast("Churn prediction refreshed", "success");
  };

  const handleTrain = async () => {
    try {
      await trainHook.train();
      showToast("Model trained successfully", "success");
      await Promise.all([
        metrics.refetch(),
        scores.refetch(),
        governance.refetch(),
      ]);
    } catch (e) {
      showToast(e?.response?.data?.detail ?? "Training failed", "error");
    }
  };

  const governanceStatusClass =
    governance.data?.status === "stable"
      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
      : governance.data?.status === "watch"
        ? "bg-amber-500/10 border-amber-500/30 text-amber-300"
        : "bg-red-500/10 border-red-500/30 text-red-300";

  const kpiCards = (
    <>
      <KPICard
        title="ROC-AUC"
        value={
          metrics.data?.roc_auc != null
            ? Number(metrics.data.roc_auc).toFixed(3)
            : "N/A"
        }
        subtitle="Quality on held-out set"
        icon={RotateCcw}
        iconColor="#6366F1"
        iconBg="bg-violet-500/10"
        trend={0}
        trendLabel="baseline"
      />
      <KPICard
        title="Accuracy"
        value={
          metrics.data?.accuracy != null
            ? Number(metrics.data.accuracy * 100).toFixed(1) + "%"
            : "N/A"
        }
        subtitle="Classification performance"
        icon={RotateCcw}
        iconColor="#22C55E"
        iconBg="bg-emerald-500/10"
        trend={0}
        trendLabel="baseline"
      />
      <KPICard
        title="Churn rate"
        value={
          metrics.data?.churn_rate != null
            ? Number(metrics.data.churn_rate * 100).toFixed(1) + "%"
            : "N/A"
        }
        subtitle="Positive ratio in training"
        icon={RotateCcw}
        iconColor="#F59E0B"
        iconBg="bg-amber-500/10"
        trend={0}
        trendLabel="class balance"
      />
      <KPICard
        title="Train samples"
        value={
          metrics.data?.n_samples != null
            ? Number(metrics.data.n_samples).toLocaleString()
            : "N/A"
        }
        subtitle="Subscription rows used"
        icon={RotateCcw}
        iconColor="#94A3B8"
        iconBg="bg-slate-600/20"
        trend={0}
        trendLabel="dataset"
      />
    </>
  );

  return (
    <>
      {Toast}

      {anyError && (
        <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
          <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
          <p className="flex-1 text-sm text-red-200">{anyError}</p>
          <button
            onClick={handleRefresh}
            className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
          >
            <RotateCcw size={14} /> Retry
          </button>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3">
        {isAdmin() && (
          <button
            onClick={handleTrain}
            disabled={trainHook.loading}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition disabled:opacity-60"
          >
            {trainHook.loading ? "Training..." : "Train model"}
          </button>
        )}

        <button
          onClick={handleRefresh}
          className="px-3 py-2 text-sm text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition"
        >
          Refresh
        </button>

        <div className="flex items-center gap-2 ml-auto">
          <span className="text-xs text-slate-500 font-medium">Threshold:</span>
          <input
            type="number"
            step="0.05"
            min="0"
            max="1"
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
            className="w-24 px-3 py-2 text-xs bg-[#0F1117] border border-slate-700 rounded-lg text-slate-200 focus:outline-none"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {metrics.loading || scores.loading
          ? Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="bg-slate-900 border border-slate-800 rounded-xl p-5 h-full flex flex-col gap-3 animate-pulse"
              >
                <div className="h-4 w-24 bg-slate-800 rounded" />
                <div className="h-8 w-28 bg-slate-800 rounded" />
                <div className="h-3 w-40 bg-slate-800 rounded" />
              </div>
            ))
          : kpiCards}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6 mt-6">
        <div className="xl:col-span-3">
          <Card
            title="Predicted churn risk distribution"
            subtitle="Risk category based on churn probability"
          >
            <div className="h-80 w-full min-w-0">
              <ResponsiveContainer
                width="100%"
                height="100%"
                minWidth="0"
                minHeight="0"
              >
                <BarChart
                  data={distributionSeries}
                  margin={{ top: 10, right: 18, left: 0, bottom: 0 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(148,163,184,0.12)"
                  />
                  <XAxis
                    dataKey="risk_category"
                    stroke="rgba(148,163,184,0.8)"
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis
                    stroke="rgba(148,163,184,0.8)"
                    tick={{ fontSize: 12 }}
                    domain={[0, "auto"]}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "var(--chart-tooltip-bg)",
                      border: "1px solid rgba(148,163,184,0.2)",
                      borderRadius: 12,
                    }}
                  />
                  <Bar dataKey="count" fill="#8B5CF6" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>

        <div className="xl:col-span-2">
          <Card
            title="Feature impact (top coefficients)"
            subtitle="Magnitude of logistic regression coefficients"
          >
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs text-slate-400">
                  <tr>
                    <th className="py-2 pr-2">Feature</th>
                    <th className="py-2 pr-2 text-right">Coefficient</th>
                  </tr>
                </thead>
                <tbody className="text-slate-200">
                  {coefficientTop.length === 0 ? (
                    <tr>
                      <td className="py-3 text-slate-400" colSpan={2}>
                        Coefficients available after training.
                      </td>
                    </tr>
                  ) : (
                    coefficientTop.map((r) => (
                      <tr
                        key={r.feature}
                        className="border-t border-slate-800/60"
                      >
                        <td className="py-3 pr-2">{r.feature}</td>
                        <td className="py-3 pr-2 text-right">
                          {Number(r.coefficient).toFixed(4)}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </div>

      <div className="mt-6">
        <Card
          title={`Top risky users (max risk per user)`}
          subtitle={`Showing top ${topN} users - threshold=${threshold}`}
          right={
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 font-medium">Top:</span>
              <input
                type="number"
                min="1"
                max="200"
                value={topN}
                onChange={(e) => setTopN(Number(e.target.value))}
                className="w-20 px-3 py-2 text-xs bg-[#0F1117] border border-slate-700 rounded-lg text-slate-200 focus:outline-none"
              />
            </div>
          }
        >
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-xs text-slate-400">
                <tr>
                  <th className="py-2 pr-2">Phone</th>
                  <th className="py-2 pr-2">Service</th>
                  <th className="py-2 pr-2 text-right">Risk score</th>
                  <th className="py-2 pr-2">Category</th>
                  <th className="py-2 pr-2 text-right">Pred.</th>
                </tr>
              </thead>
              <tbody className="text-slate-200">
                {(scores.data?.top_users ?? []).length === 0 ? (
                  <tr>
                    <td className="py-3 text-slate-400" colSpan={5}>
                      No predictions available yet.
                    </td>
                  </tr>
                ) : (
                  (scores.data?.top_users ?? []).map((u) => (
                    <tr
                      key={u.user_id}
                      className="border-t border-slate-800/60"
                    >
                      <td className="py-3 pr-2">{u.phone_number}</td>
                      <td className="py-3 pr-2">{u.service_name}</td>
                      <td className="py-3 pr-2 text-right">
                        {(Number(u.churn_risk) * 100).toFixed(1)}%
                      </td>
                      <td className="py-3 pr-2">
                        <span
                          className={`text-xs px-2 py-1 rounded-full border ${
                            u.risk_category === "Low"
                              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                              : u.risk_category === "Medium"
                                ? "bg-amber-500/10 border-amber-500/30 text-amber-300"
                                : "bg-red-500/10 border-red-500/30 text-red-300"
                          }`}
                        >
                          {u.risk_category}
                        </span>
                      </td>
                      <td className="py-3 pr-2 text-right">
                        {u.predicted_churn}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      <div className="mt-6">
        <Card
          title="Model Governance"
          subtitle="Drift monitoring, calibration health, and stable evaluation protocol"
          right={
            <span
              className={`text-xs px-2 py-1 rounded-full border uppercase font-semibold ${governanceStatusClass}`}
            >
              {String(governance.data?.status ?? "unknown").replaceAll(
                "_",
                " ",
              )}
            </span>
          }
        >
          {governance.loading ? (
            <p className="text-sm text-slate-400">Loading governance...</p>
          ) : !governance.data ? (
            <p className="text-sm text-slate-400">
              No governance data available.
            </p>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                <div className="rounded-lg border border-slate-700 bg-slate-800/40 p-3">
                  <p className="text-xs text-slate-400">Days Since Training</p>
                  <p className="text-xl font-bold text-slate-100">
                    {Number(governance.data.days_since_training ?? 0)}
                  </p>
                </div>
                <div className="rounded-lg border border-slate-700 bg-slate-800/40 p-3">
                  <p className="text-xs text-slate-400">High Drift Features</p>
                  <p className="text-xl font-bold text-slate-100">
                    {Number(governance.data?.drift?.high_drift_features ?? 0)}
                  </p>
                </div>
                <div className="rounded-lg border border-slate-700 bg-slate-800/40 p-3">
                  <p className="text-xs text-slate-400">Brier Score</p>
                  <p className="text-xl font-bold text-slate-100">
                    {governance.data?.calibration?.brier_score != null
                      ? Number(governance.data.calibration.brier_score).toFixed(
                          4,
                        )
                      : "N/A"}
                  </p>
                </div>
                <div className="rounded-lg border border-slate-700 bg-slate-800/40 p-3">
                  <p className="text-xs text-slate-400">ECE</p>
                  <p className="text-xl font-bold text-slate-100">
                    {governance.data?.calibration?.ece != null
                      ? Number(governance.data.calibration.ece).toFixed(4)
                      : "N/A"}
                  </p>
                </div>
              </div>

              <div className="rounded-lg border border-slate-700 bg-slate-800/30 p-3">
                <p className="text-xs uppercase tracking-wide text-slate-400 mb-2">
                  Evaluation Protocol
                </p>
                <p className="text-sm text-slate-200">
                  {governance.data?.protocol?.version ?? "churn-governance-v1"}{" "}
                  - {governance.data?.protocol?.evaluation_split ?? "N/A"}
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  Recalibration cadence:{" "}
                  {Number(
                    governance.data?.protocol?.recalibration_cadence_days ?? 30,
                  )}{" "}
                  days
                </p>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="text-xs text-slate-400">
                    <tr>
                      <th className="py-2 pr-2">Feature</th>
                      <th className="py-2 pr-2 text-right">Train Mean</th>
                      <th className="py-2 pr-2 text-right">Current Mean</th>
                      <th className="py-2 pr-2 text-right">Z-Shift</th>
                      <th className="py-2 pr-2">Severity</th>
                    </tr>
                  </thead>
                  <tbody className="text-slate-200">
                    {(governance.data?.drift?.features ?? [])
                      .slice(0, 6)
                      .map((f) => (
                        <tr
                          key={f.feature}
                          className="border-t border-slate-800/60"
                        >
                          <td className="py-3 pr-2">{f.feature}</td>
                          <td className="py-3 pr-2 text-right">
                            {Number(f.train_mean ?? 0).toFixed(2)}
                          </td>
                          <td className="py-3 pr-2 text-right">
                            {Number(f.current_mean ?? 0).toFixed(2)}
                          </td>
                          <td className="py-3 pr-2 text-right">
                            {Number(f.z_shift ?? 0).toFixed(2)}
                          </td>
                          <td className="py-3 pr-2">
                            <span
                              className={`text-xs px-2 py-1 rounded-full border uppercase ${
                                f.severity === "high"
                                  ? "bg-red-500/10 border-red-500/30 text-red-300"
                                  : f.severity === "medium"
                                    ? "bg-amber-500/10 border-amber-500/30 text-amber-300"
                                    : "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                              }`}
                            >
                              {f.severity}
                            </span>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </Card>
      </div>
    </>
  );
}
