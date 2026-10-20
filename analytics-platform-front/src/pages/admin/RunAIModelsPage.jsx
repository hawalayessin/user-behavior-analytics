import { createElement, useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  Clock3,
  Database,
  Eye,
  Gauge,
  Play,
  RefreshCw,
  ShieldCheck,
  Trash2,
  TrendingDown,
  Users,
} from "lucide-react";

import { DEFAULT_ANALYTICS_FILTERS } from "../../constants/dateFilters";
import { useAnomalies } from "../../hooks/useAnomalies";
import { useSegmentationTrain } from "../../hooks/useSegmentationTrain";
import { useChurnPredictionTrain } from "../../hooks/useChurnPredictionTrain";
import { useChurnPredictionMetrics } from "../../hooks/useChurnPredictionMetrics";
import { useSegmentationKPIs } from "../../hooks/useSegmentationKPIs";

const DEFAULT_SEVERITY = ["critical", "high", "medium"];
const DEFAULT_METRICS = ["dau", "churn_rate", "revenue", "renewals"];
const AI_RUN_HISTORY_KEY = "digmaco:ai-model-run-history:v1";

const numberFormatter = new Intl.NumberFormat();

function formatNumber(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numberFormatter.format(numeric) : "--";
}

function formatPercent(value, digits = 1) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? `${numeric.toFixed(digits)}%` : "--";
}

function formatLastRun(iso) {
  if (!iso) return "--";
  const dt = new Date(iso);
  if (Number.isNaN(dt.getTime())) return "--";
  return dt.toLocaleString(undefined, {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function durationBetween(startIso, endIso) {
  const start = new Date(startIso);
  const end = new Date(endIso);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return null;
  return Math.max(0, Math.round(((end.getTime() - start.getTime()) / 1000) * 10) / 10);
}

function statusMeta(status, loading) {
  if (loading) {
    return {
      label: "Running",
      icon: RefreshCw,
      bg: "var(--color-warning-bg)",
      fg: "var(--color-warning)",
      border: "var(--color-warning)",
    };
  }

  if (status === "failed" || status === "error") {
    return {
      label: "Error",
      icon: AlertCircle,
      bg: "var(--color-danger-bg)",
      fg: "var(--color-danger)",
      border: "var(--color-danger)",
    };
  }

  if (status === "success") {
    return {
      label: "Ready",
      icon: CheckCircle2,
      bg: "var(--color-success-bg)",
      fg: "var(--color-success)",
      border: "var(--color-success)",
    };
  }

  return {
    label: "Idle",
    icon: Clock3,
    bg: "var(--color-bg-elevated)",
    fg: "var(--color-text-secondary)",
    border: "var(--color-border)",
  };
}

function StatusBadge({ status, loading }) {
  const meta = statusMeta(status, loading);
  const Icon = meta.icon;

  return (
    <span
      className="inline-flex h-7 items-center gap-1.5 rounded-md border px-2 text-xs font-semibold"
      style={{
        backgroundColor: meta.bg,
        borderColor: meta.border,
        color: meta.fg,
      }}
    >
      <Icon size={13} className={loading ? "animate-spin" : ""} />
      {meta.label}
    </span>
  );
}

function MiniStat({ icon, label, value }) {
  const iconNode = icon ? createElement(icon, { size: 14 }) : null;

  return (
    <div
      className="rounded-md border p-3"
      style={{
        backgroundColor: "var(--color-bg-elevated)",
        borderColor: "var(--color-border)",
      }}
    >
      <div className="flex items-center gap-2 text-xs" style={{ color: "var(--color-text-secondary)" }}>
        {iconNode}
        <span>{label}</span>
      </div>
      <p className="mt-2 break-words text-lg font-bold leading-tight sm:text-xl" style={{ color: "var(--color-text-primary)" }}>
        {value}
      </p>
    </div>
  );
}

function ProgressBar({ value }) {
  const pct = Math.max(0, Math.min(100, Number(value) || 0));

  return (
    <div className="mt-3">
      <div className="mb-1 flex items-center justify-between text-xs" style={{ color: "var(--color-text-secondary)" }}>
        <span>Coverage</span>
        <span>{formatPercent(pct)}</span>
      </div>
      <div
        className="h-2 overflow-hidden rounded-full"
        style={{ backgroundColor: "var(--color-bg-elevated)" }}
      >
        <div
          className="h-full rounded-full"
          style={{
            width: `${pct}%`,
            backgroundColor: pct >= 100 ? "var(--color-success)" : "var(--color-primary)",
          }}
        />
      </div>
    </div>
  );
}

function ModuleCard({
  icon,
  title,
  subtitle,
  primaryMetricLabel,
  primaryMetricValue,
  secondaryMetricLabel,
  secondaryMetricValue,
  tertiaryMetricLabel,
  tertiaryMetricValue,
  coverage,
  actionLabel,
  loading,
  status,
  onRun,
}) {
  const iconNode = icon ? createElement(icon, { size: 19, style: { color: "var(--color-primary)" } }) : null;

  return (
    <section
      className="flex h-full min-h-[300px] min-w-0 flex-col justify-between rounded-lg border p-4 sm:p-5"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-bg-card)",
        boxShadow: "var(--color-card-shadow)",
      }}
    >
      <div>
        <div className="mb-4 flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md"
              style={{ backgroundColor: "var(--color-primary-bg)" }}
            >
              {iconNode}
            </div>
            <div className="min-w-0">
              <h2 className="text-lg font-bold leading-tight" style={{ color: "var(--color-text-primary)" }}>
                {title}
              </h2>
              <p className="mt-1 text-sm leading-5" style={{ color: "var(--color-text-secondary)" }}>
                {subtitle}
              </p>
            </div>
          </div>
          <StatusBadge status={status} loading={loading} />
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 xl:grid-cols-1 2xl:grid-cols-3">
          <MiniStat icon={Gauge} label={primaryMetricLabel} value={primaryMetricValue} />
          <MiniStat icon={Clock3} label={secondaryMetricLabel} value={secondaryMetricValue} />
          <MiniStat icon={Database} label={tertiaryMetricLabel} value={tertiaryMetricValue} />
        </div>

        {coverage != null && <ProgressBar value={coverage} />}
      </div>

      <button
        onClick={onRun}
        disabled={loading}
        className="mt-5 flex min-h-11 w-full items-center justify-center gap-2 rounded-md px-3 py-2 text-center text-sm font-bold leading-tight transition disabled:opacity-60"
        style={{
          backgroundColor: "var(--color-primary)",
          color: "white",
        }}
      >
        {loading ? <RefreshCw size={16} className="animate-spin" /> : <Play size={16} />}
        {loading ? "Running" : actionLabel}
      </button>
    </section>
  );
}

function formatLogTime(iso) {
  if (!iso) return "--";
  const dt = new Date(iso);
  if (Number.isNaN(dt.getTime())) return "--";
  return dt.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

function getLogDetails(log) {
  return Object.entries(log)
    .filter(([key, value]) => !["ts", "message", "source"].includes(key) && value != null && value !== "")
    .map(([key, value]) => `${key}: ${value}`)
    .join(" - ");
}

function loadRunHistory() {
  try {
    const raw = localStorage.getItem(AI_RUN_HISTORY_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveRunHistory(history) {
  try {
    localStorage.setItem(AI_RUN_HISTORY_KEY, JSON.stringify(history.slice(0, 50)));
  } catch {
    // Ignore storage quota/privacy-mode failures.
  }
}

function statusTone(status) {
  if (status === "success") return {
    bg: "var(--color-success-bg)",
    color: "var(--color-success)",
    border: "var(--color-success)",
  };
  if (status === "failed" || status === "error") return {
    bg: "var(--color-danger-bg)",
    color: "var(--color-danger)",
    border: "var(--color-danger)",
  };
  return {
    bg: "var(--color-bg-elevated)",
    color: "var(--color-text-secondary)",
    border: "var(--color-border)",
  };
}

function HistoryStatusBadge({ status }) {
  const tone = statusTone(status);
  return (
    <span
      className="inline-flex rounded-md border px-2 py-1 text-xs font-bold capitalize"
      style={{
        backgroundColor: tone.bg,
        borderColor: tone.border,
        color: tone.color,
      }}
    >
      {status || "unknown"}
    </span>
  );
}

function HistoryDetailsModal({ record, onClose }) {
  if (!record) return null;
  const details = record.details ? JSON.stringify(record.details, null, 2) : "";
  const logs = Array.isArray(record.logs) ? record.logs : [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div
        className="w-full max-w-4xl rounded-lg border p-5"
        style={{
          backgroundColor: "var(--color-bg-card)",
          borderColor: "var(--color-border)",
        }}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: "var(--color-text-muted)" }}>
              {record.model}
            </p>
            <h3 className="mt-1 text-lg font-bold" style={{ color: "var(--color-text-primary)" }}>
              Run details
            </h3>
            <p className="mt-1 text-sm" style={{ color: "var(--color-text-secondary)" }}>
              {record.message || "No message"}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md px-3 py-2 text-sm font-bold"
            style={{
              backgroundColor: "var(--color-bg-elevated)",
              color: "var(--color-text-secondary)",
            }}
          >
            Close
          </button>
        </div>

        {record.error && (
          <div
            className="mt-4 rounded-md border p-3 text-sm"
            style={{
              backgroundColor: "var(--color-danger-bg)",
              borderColor: "var(--color-danger)",
              color: "var(--color-danger)",
            }}
          >
            {record.error}
          </div>
        )}

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div>
            <p className="mb-2 text-xs font-bold uppercase tracking-wide" style={{ color: "var(--color-text-muted)" }}>
              Logs
            </p>
            <pre
              className="max-h-72 overflow-auto rounded-md border p-3 text-xs"
              style={{
                backgroundColor: "var(--color-bg-elevated)",
                borderColor: "var(--color-border)",
                color: "var(--color-text-secondary)",
              }}
            >
              {logs.length
                ? logs.map((log) => `[${formatLogTime(log.ts)}] ${log.message || ""} ${getLogDetails(log) || ""}`).join("\n")
                : "No logs captured."}
            </pre>
          </div>
          <div>
            <p className="mb-2 text-xs font-bold uppercase tracking-wide" style={{ color: "var(--color-text-muted)" }}>
              Details
            </p>
            <pre
              className="max-h-72 overflow-auto rounded-md border p-3 text-xs"
              style={{
                backgroundColor: "var(--color-bg-elevated)",
                borderColor: "var(--color-border)",
                color: "var(--color-text-secondary)",
              }}
            >
              {details || "No extra details."}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}

function LogRow({ log }) {
  const extras = Object.entries(log)
    .filter(([key, value]) => !["ts", "message", "source"].includes(key) && value != null)
    .slice(0, 3);
  const detailText = getLogDetails(log);

  return (
    <div
      className="grid gap-2 rounded-md px-3 py-2 text-xs md:grid-cols-[88px_72px_1fr]"
      style={{ backgroundColor: "var(--color-bg-elevated)", color: "var(--color-text-primary)" }}
    >
      <span style={{ color: "var(--color-text-muted)" }}>
        {formatLogTime(log.ts)}
      </span>
      <span className="font-semibold" style={{ color: "var(--color-primary)" }}>
        {log.source}
      </span>
      <span className="min-w-0 break-words">
        {log.message}
        {detailText && (
          <span className="ml-2" style={{ color: "var(--color-text-muted)" }}>
            {extras.map(([key, value]) => `${key}: ${value}`).join(" · ")}
          </span>
        )}
      </span>
    </div>
  );
}

function ModelHistoryTable({ history, onView, onClear }) {
  return (
    <section
      className="overflow-hidden rounded-lg border"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-bg-card)",
      }}
    >
      <div
        className="flex flex-col gap-3 border-b px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-bg-elevated)",
        }}
      >
        <div className="flex items-center gap-2">
          <Database size={16} style={{ color: "var(--color-primary)" }} />
          <div>
            <h2 className="text-base font-bold" style={{ color: "var(--color-text-primary)" }}>
              AI Model Run History
            </h2>
            <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
              Completed model runs with captured logs and error diagnostics.
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={onClear}
          disabled={history.length === 0}
          className="inline-flex items-center justify-center gap-2 rounded-md px-3 py-2 text-xs font-bold disabled:opacity-50"
          style={{
            backgroundColor: "var(--color-bg-card)",
            color: "var(--color-text-secondary)",
            border: "1px solid var(--color-border)",
          }}
        >
          <Trash2 size={14} />
          Clear
        </button>
      </div>

      <div className="overflow-x-auto p-3">
        <table className="min-w-[860px] w-full text-left text-xs">
          <thead style={{ backgroundColor: "var(--color-bg-elevated)" }}>
            <tr style={{ color: "var(--color-text-muted)" }}>
              {["Completed", "Model", "Status", "Duration", "Message", "Error", "Details"].map((heading) => (
                <th key={heading} className="px-3 py-2 font-semibold uppercase tracking-wide">
                  {heading}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {history.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-3 py-8 text-center" style={{ color: "var(--color-text-secondary)" }}>
                  No historical model run yet.
                </td>
              </tr>
            ) : (
              history.map((record) => (
                <tr
                  key={record.id}
                  className="border-t align-top"
                  style={{
                    borderColor: "var(--color-border)",
                    color: "var(--color-text-primary)",
                  }}
                >
                  <td className="whitespace-nowrap px-3 py-3" style={{ color: "var(--color-text-muted)" }}>
                    {formatLastRun(record.completedAt)}
                  </td>
                  <td className="px-3 py-3 font-semibold">{record.model}</td>
                  <td className="px-3 py-3">
                    <HistoryStatusBadge status={record.status} />
                  </td>
                  <td className="whitespace-nowrap px-3 py-3" style={{ color: "var(--color-text-secondary)" }}>
                    {record.durationSec != null ? `${record.durationSec}s` : "--"}
                  </td>
                  <td className="max-w-[240px] px-3 py-3" style={{ color: "var(--color-text-secondary)" }}>
                    <span className="line-clamp-2">{record.message || "--"}</span>
                  </td>
                  <td className="max-w-[220px] px-3 py-3" style={{ color: record.error ? "var(--color-danger)" : "var(--color-text-muted)" }}>
                    <span className="line-clamp-2">{record.error || "--"}</span>
                  </td>
                  <td className="px-3 py-2">
                    <button
                      type="button"
                      onClick={() => onView(record)}
                      className="inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 font-bold"
                      style={{
                        backgroundColor: "var(--color-primary-bg)",
                        color: "var(--color-primary)",
                      }}
                    >
                      <Eye size={13} />
                      View
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default function RunAIModelsPage() {
  const [runningAll, setRunningAll] = useState(false);
  const [runHistory, setRunHistory] = useState(() => loadRunHistory());
  const [selectedHistory, setSelectedHistory] = useState(null);
  const churnTrain = useChurnPredictionTrain();
  const churnMetrics = useChurnPredictionMetrics();
  const segmentationTrain = useSegmentationTrain();
  const segmentationKPIs = useSegmentationKPIs(DEFAULT_ANALYTICS_FILTERS);
  const {
    runDetection,
    runDetectionLoading,
    detectionJob,
    summary,
    errors,
  } = useAnomalies({
    filters: DEFAULT_ANALYTICS_FILTERS,
    severity: DEFAULT_SEVERITY,
    metrics: DEFAULT_METRICS,
    limit: 1,
    offset: 0,
  });

  const addHistoryRecord = useCallback((record) => {
    setRunHistory((prev) => {
      if (prev.some((item) => item.runKey === record.runKey)) return prev;
      const next = [record, ...prev].slice(0, 50);
      saveRunHistory(next);
      return next;
    });
  }, []);

  const clearHistory = useCallback(() => {
    setRunHistory([]);
    saveRunHistory([]);
  }, []);

  useEffect(() => {
    const job = churnTrain.job;
    if (!job || !["success", "failed"].includes(job.status)) return;
    const completedAt = job.completed_at ?? new Date().toISOString();
    addHistoryRecord({
      id: `churn-${job.job_id ?? completedAt}-${job.status}`,
      runKey: `churn-${job.job_id ?? completedAt}-${job.status}`,
      model: "Churn Prediction",
      status: job.status,
      startedAt: job.started_at,
      completedAt,
      durationSec: durationBetween(job.started_at, completedAt),
      message: job.status === "success" ? "Churn training completed" : "Churn training failed",
      error: job.error ?? null,
      details: job.metrics ?? null,
      logs: job.logs ?? [],
    });
  }, [addHistoryRecord, churnTrain.job]);

  useEffect(() => {
    const job = segmentationTrain.job;
    if (!job || !["success", "failed", "error"].includes(job.status)) return;
    const logs = job.logs ?? [];
    const lastLog = logs[logs.length - 1];
    const completedAt = lastLog?.ts ?? new Date().toISOString();
    const startedAt = logs[0]?.ts ?? null;
    const runKey = [
      "segmentation",
      job.status,
      job.summary?.window_start,
      job.summary?.window_end,
      completedAt,
    ].join("-");
    addHistoryRecord({
      id: runKey,
      runKey,
      model: "User Segmentation",
      status: job.status,
      startedAt,
      completedAt,
      durationSec: job.summary?.total_elapsed_sec ?? durationBetween(startedAt, completedAt),
      message: job.message ?? "Segmentation training completed",
      error: job.status === "success" ? null : job.message,
      details: job.summary ?? null,
      logs,
    });
  }, [addHistoryRecord, segmentationTrain.job]);

  useEffect(() => {
    const job = detectionJob;
    if (!job || !["success", "failed", "error", "not_found"].includes(job.status)) return;
    const logs = job.logs ?? [];
    const lastLog = logs[logs.length - 1];
    const completedAt = job.result?.run_completed_at ?? lastLog?.ts ?? new Date().toISOString();
    const startedAt = logs[0]?.ts ?? null;
    const runKey = `anomaly-${job.job_id ?? completedAt}-${job.status}`;
    addHistoryRecord({
      id: runKey,
      runKey,
      model: "Anomaly Detection",
      status: job.status === "not_found" ? "failed" : job.status,
      startedAt,
      completedAt,
      durationSec: durationBetween(startedAt, completedAt),
      message: job.message ?? (job.status === "success" ? "Anomaly detection completed" : "Anomaly detection failed"),
      error: job.error ?? null,
      details: job.result ?? null,
      logs,
    });
  }, [addHistoryRecord, detectionJob]);

  const handleRunAll = async () => {
    setRunningAll(true);
    try {
      await Promise.allSettled([
        runDetection(),
        churnTrain.train(),
        segmentationTrain.train(),
      ]);
    } finally {
      setRunningAll(false);
    }
  };

  const mergedLogs = useMemo(() => {
    const withSource = [];
    (detectionJob?.logs ?? []).forEach((log) =>
      withSource.push({ ...log, source: "ANOMALY" }),
    );
    (churnTrain.job?.logs ?? []).forEach((log) =>
      withSource.push({ ...log, source: "CHURN" }),
    );
    (segmentationTrain.job?.logs ?? []).forEach((log) =>
      withSource.push({ ...log, source: "SEGMENT" }),
    );
    return withSource.sort((a, b) => new Date(a.ts) - new Date(b.ts));
  }, [detectionJob, churnTrain.job, segmentationTrain.job]);

  const firstError =
    churnTrain.error ||
    churnMetrics.error ||
    segmentationKPIs.error ||
    segmentationTrain.error ||
    errors?.summary ||
    errors?.timeline ||
    null;

  const churnBalancedAccuracy =
    churnMetrics.data?.balanced_accuracy != null
      ? formatPercent(Number(churnMetrics.data.balanced_accuracy) * 100)
      : "--";
  const churnLastRun = formatLastRun(churnMetrics.data?.trained_at);
  const churnTrainingUsers = churnTrain.job?.summary?.rows ?? churnTrain.job?.summary?.users;

  const segSummary = segmentationTrain.job?.summary ?? {};
  const segDominantPct = formatPercent(segmentationKPIs.data?.dominant_pct);
  const segTargetedUsers = segSummary.targeted_active_users ?? segSummary.users;
  const segSegmentedUsers = segSummary.segmented_users ?? segSummary.users;
  const segCoverage = segSummary.coverage_pct;

  const anomalyCritical =
    summary?.critical_alerts != null
      ? summary.critical_alerts
      : detectionJob?.result?.critical;
  const anomalyLastRun = formatLastRun(
    detectionJob?.result?.run_completed_at ?? summary?.last_detection?.run_at,
  );
  const anomalyTotal = summary?.total_anomalies ?? detectionJob?.result?.total_anomalies;

  return (
    <div className="min-w-0 space-y-5">
      <header
        className="min-w-0 rounded-lg border p-4 sm:p-5"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-bg-card)",
        }}
      >
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-3xl">
            <div className="flex items-center gap-2 text-sm font-semibold" style={{ color: "var(--color-primary)" }}>
              <BrainCircuit size={17} />
              AI model operations
            </div>
            <h1 className="mt-2 text-lg font-extrabold leading-tight sm:text-3xl" style={{ color: "var(--color-text-primary)" }}>
              Run AI Models
            </h1>
            <p className="mt-2 text-sm leading-6" style={{ color: "var(--color-text-secondary)" }}>
              Admin console for model execution, training health, and segmentation coverage.
            </p>
          </div>

          <button
            onClick={handleRunAll}
            disabled={runningAll}
            className="flex min-h-11 w-full items-center justify-center gap-2 rounded-md px-4 py-2 text-center text-sm font-bold leading-tight transition disabled:opacity-60 sm:w-auto"
            style={{
              backgroundColor: "var(--color-primary)",
              color: "white",
            }}
          >
            {runningAll ? <RefreshCw size={17} className="animate-spin" /> : <Play size={17} />}
            {runningAll ? "Starting models" : "Run all models"}
          </button>
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-3">
          <MiniStat icon={ShieldCheck} label="Admin scope" value="Full access" />
          <MiniStat icon={Users} label="Segmentation coverage" value={segCoverage != null ? formatPercent(segCoverage) : "--"} />
          <MiniStat icon={Activity} label="Execution logs" value={formatNumber(mergedLogs.length)} />
        </div>
      </header>

      {firstError && (
        <div
          className="flex items-start gap-3 rounded-lg border p-4"
          style={{
            backgroundColor: "var(--color-danger-bg)",
            borderColor: "var(--color-danger)",
          }}
        >
          <AlertCircle size={19} className="mt-0.5 shrink-0" style={{ color: "var(--color-danger)" }} />
          <p className="text-sm" style={{ color: "var(--color-danger)" }}>
            {firstError}
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <ModuleCard
          icon={TrendingDown}
          title="Churn Prediction"
          subtitle="Logistic regression training on subscriber behavior."
          primaryMetricLabel="Balanced acc."
          primaryMetricValue={churnBalancedAccuracy}
          secondaryMetricLabel="Last run"
          secondaryMetricValue={churnLastRun}
          tertiaryMetricLabel="Rows"
          tertiaryMetricValue={formatNumber(churnTrainingUsers)}
          actionLabel="Train model"
          loading={churnTrain.loading}
          status={churnTrain.job?.status}
          onRun={churnTrain.train}
        />
        <ModuleCard
          icon={Users}
          title="User Segmentation"
          subtitle="K-Means clustering over the complete active targeted base."
          primaryMetricLabel="Dominant share"
          primaryMetricValue={segDominantPct}
          secondaryMetricLabel="Targeted users"
          secondaryMetricValue={formatNumber(segTargetedUsers)}
          tertiaryMetricLabel="Segmented users"
          tertiaryMetricValue={formatNumber(segSegmentedUsers)}
          coverage={segCoverage}
          actionLabel="Recalculate model"
          loading={segmentationTrain.loading}
          status={segmentationTrain.job?.status}
          onRun={segmentationTrain.train}
        />
        <ModuleCard
          icon={AlertTriangle}
          title="Anomaly Detection"
          subtitle="Isolation Forest detection for unusual activity patterns."
          primaryMetricLabel="Critical alerts"
          primaryMetricValue={formatNumber(anomalyCritical)}
          secondaryMetricLabel="Last run"
          secondaryMetricValue={anomalyLastRun}
          tertiaryMetricLabel="Anomalies"
          tertiaryMetricValue={formatNumber(anomalyTotal)}
          actionLabel="Run detection"
          loading={runDetectionLoading}
          status={detectionJob?.status}
          onRun={runDetection}
        />
      </div>

      <section
        className="overflow-hidden rounded-lg border"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-bg-card)",
        }}
      >
        <div
          className="flex items-center justify-between gap-3 border-b px-4 py-3"
          style={{
            borderColor: "var(--color-border)",
            backgroundColor: "var(--color-bg-elevated)",
          }}
        >
          <div className="flex items-center gap-2">
            <BrainCircuit size={16} style={{ color: "var(--color-primary)" }} />
            <h2 className="text-base font-bold" style={{ color: "var(--color-text-primary)" }}>
              Execution logs
            </h2>
          </div>
          <span className="text-xs" style={{ color: "var(--color-text-muted)" }}>
            {formatNumber(mergedLogs.length)} events
          </span>
        </div>

        <div className="max-h-72 overflow-auto p-3">
          <div
            className="min-w-[560px] overflow-hidden rounded-md border"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: "var(--color-bg-card)",
            }}
          >
            <div
              className="grid gap-2 border-b px-3 py-2 text-xs font-semibold uppercase tracking-wide md:grid-cols-[88px_72px_1fr]"
              style={{
                borderColor: "var(--color-border)",
                backgroundColor: "var(--color-bg-elevated)",
                color: "var(--color-text-muted)",
              }}
            >
              <span>Time</span>
              <span>Model</span>
              <span>Event / details</span>
            </div>
            {mergedLogs.length === 0 ? (
              <div className="px-3 py-6 text-center text-sm" style={{ color: "var(--color-text-secondary)" }}>
                No model execution yet.
              </div>
            ) : (
              mergedLogs.map((log, idx) => (
                <LogRow key={`${log.source}-${log.ts}-${idx}`} log={log} />
              ))
            )}
          </div>
        </div>
      </section>

      <ModelHistoryTable
        history={runHistory}
        onView={setSelectedHistory}
        onClear={clearHistory}
      />

      <HistoryDetailsModal
        record={selectedHistory}
        onClose={() => setSelectedHistory(null)}
      />
    </div>
  );
}
