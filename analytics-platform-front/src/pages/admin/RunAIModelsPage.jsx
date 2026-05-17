import { useMemo, useState } from "react";
import {
  Play,
  BrainCircuit,
  AlertCircle,
  Users,
  AlertTriangle,
  TrendingDown,
  RefreshCw,
} from "lucide-react";

import AppLayout from "../../components/layout/AppLayout";
import { DEFAULT_ANALYTICS_FILTERS } from "../../constants/dateFilters";
import { useAnomalies } from "../../hooks/useAnomalies";
import { useSegmentationTrain } from "../../hooks/useSegmentationTrain";
import { useChurnPredictionTrain } from "../../hooks/useChurnPredictionTrain";
import { useChurnPredictionMetrics } from "../../hooks/useChurnPredictionMetrics";
import { useSegmentationKPIs } from "../../hooks/useSegmentationKPIs";

const DEFAULT_SEVERITY = ["critical", "high", "medium"];
const DEFAULT_METRICS = ["dau", "churn_rate", "revenue", "renewals"];

function StatusBadge({ status, loading }) {
  if (loading) {
    return (
      <span className="px-2 py-1 rounded-full text-[10px] font-bold border" style={{
        backgroundColor: "var(--color-warning-bg)",
        borderColor: "var(--color-warning)",
        color: "var(--color-warning)"
      }}>
        TRAINING
      </span>
    );
  }

  if (status === "failed") {
    return (
      <span className="px-2 py-1 rounded-full text-[10px] font-bold border" style={{
        backgroundColor: "var(--color-danger-bg)",
        borderColor: "var(--color-danger)",
        color: "var(--color-danger)"
      }}>
        ERROR
      </span>
    );
  }

  return (
    <span className="px-2 py-1 rounded-full text-[10px] font-bold border" style={{
      backgroundColor: "var(--color-success-bg)",
      borderColor: "var(--color-success)",
      color: "var(--color-success)"
    }}>
      IDLE
    </span>
  );
}

function ModuleCard({
  icon: Icon,
  title,
  subtitle,
  primaryMetricLabel,
  primaryMetricValue,
  secondaryMetricLabel,
  secondaryMetricValue,
  loadPct,
  actionLabel,
  loading,
  status,
  onRun,
}) {
  return (
    <div className="h-full min-h-[360px] rounded-xl border p-5 flex flex-col justify-between" style={{
      borderColor: "var(--color-border)",
      backgroundColor: "var(--color-bg-card)",
      boxShadow: "var(--color-card-shadow)"
    }}>
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="h-9 w-9 rounded-lg flex items-center justify-center" style={{
            backgroundColor: "var(--color-primary-bg)"
          }}>
            <Icon size={16} style={{ color: "var(--color-primary)" }} />
          </div>
          <StatusBadge status={status} loading={loading} />
        </div>

        <h3 className="text-4xl font-extrabold leading-tight mb-1" style={{
          color: "var(--color-text-primary)"
        }}>
          {title}
        </h3>
        <p className="text-xs min-h-[40px]" style={{
          color: "var(--color-text-secondary)"
        }}>{subtitle}</p>

        <div className="grid grid-cols-2 gap-3 mt-4">
          <div>
            <p className="text-[10px] uppercase tracking-wider font-semibold" style={{
              color: "var(--color-text-secondary)"
            }}>{primaryMetricLabel}</p>
            <p className="text-5xl font-bold leading-none mt-1" style={{
              color: "var(--color-primary)"
            }}>{primaryMetricValue}</p>
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-wider font-semibold" style={{
              color: "var(--color-text-secondary)"
            }}>{secondaryMetricLabel}</p>
            <p className="text-4xl font-bold leading-none mt-1" style={{
              color: "var(--color-text-primary)"
            }}>{secondaryMetricValue}</p>
          </div>
        </div>

        <div className="mt-4">
          <div className="flex items-center justify-between text-[10px] uppercase tracking-wider font-semibold" style={{
            color: "var(--color-text-secondary)"
          }}>
            <span>Resource Load</span>
            <span>{loadPct}%</span>
          </div>
          <div className="mt-1.5 h-1 rounded-full overflow-hidden" style={{
            backgroundColor: "var(--color-bg-elevated)"
          }}>
            <div
              className="h-full rounded-full"
              style={{
                width: `${Math.max(0, Math.min(100, loadPct))}%`,
                backgroundColor: "var(--color-primary)"
              }}
            />
          </div>
        </div>
      </div>

      <button
        onClick={onRun}
        disabled={loading}
        className="mt-4 w-full h-10 rounded-lg font-bold text-base disabled:opacity-60 transition"
        style={{
          backgroundColor: "var(--color-primary)",
          color: "white"
        }}
        onMouseEnter={(e) => e.target.style.backgroundColor = "var(--color-primary-hover)"}
        onMouseLeave={(e) => e.target.style.backgroundColor = "var(--color-primary)"}
      >
        {loading ? "Running..." : actionLabel}
      </button>
    </div>
  );
}

export default function RunAIModelsPage() {
  const [runningAll, setRunningAll] = useState(false);
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
    (detectionJob?.logs ?? []).forEach((l) =>
      withSource.push({ ...l, source: "DETECT" }),
    );
    (churnTrain.job?.logs ?? []).forEach((l) =>
      withSource.push({ ...l, source: "TRAIN" }),
    );
    (segmentationTrain.job?.logs ?? []).forEach((l) =>
      withSource.push({ ...l, source: "RECALC" }),
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

  const formatLastRun = (iso) => {
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
  };

  const churnAccuracy =
    churnMetrics.data?.accuracy != null
      ? `${(Number(churnMetrics.data.accuracy) * 100).toFixed(1)}%`
      : "0.0%";
  const churnLastRun = formatLastRun(churnMetrics.data?.trained_at);

  const segDominantPct =
    segmentationKPIs.data?.dominant_pct != null
      ? `${Number(segmentationKPIs.data.dominant_pct).toFixed(1)}%`
      : "0.0%";
  const segUsers =
    segmentationTrain.job?.summary?.users != null
      ? String(segmentationTrain.job.summary.users)
      : "0";

  const anomalyCritical =
    summary?.critical_alerts != null
      ? String(summary.critical_alerts)
      : detectionJob?.result?.critical != null
        ? String(detectionJob.result.critical)
        : "0";

  const anomalyLastRun = formatLastRun(
    detectionJob?.result?.run_completed_at ?? summary?.last_detection?.run_at,
  );

  return (
    <AppLayout pageTitle="Run AI Models">
      <div className="rounded-xl border p-4 md:p-6 space-y-4" style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-bg-primary)"
      }}>
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
          <div>
            <p className="text-[10px] uppercase tracking-wider font-semibold" style={{
              color: "var(--color-text-secondary)"
            }}>System Monitoring</p>
            <h1 className="text-4xl font-extrabold mt-1" style={{
              color: "var(--color-text-primary)"
            }}>Run AI Models</h1>
            <p className="text-xs mt-1" style={{
              color: "var(--color-text-secondary)"
            }}>
              Unified observatory for Tunisian market predictive analytics.
            </p>
            <p className="text-[10px] mt-2 tracking-wider" style={{
              color: "var(--color-text-primary)"
            }}>ADMIN ONLY ACCESS</p>
          </div>

          <button
            onClick={handleRunAll}
            disabled={runningAll}
            className="h-10 px-5 text-sm rounded-lg font-bold flex items-center gap-2 disabled:opacity-60 transition"
            style={{
              backgroundColor: "var(--color-primary)",
              color: "white"
            }}
            onMouseEnter={(e) => e.target.style.backgroundColor = "var(--color-primary-hover)"}
            onMouseLeave={(e) => e.target.style.backgroundColor = "var(--color-primary)"}
          >
            {runningAll ? <RefreshCw size={16} className="animate-spin" /> : <Play size={16} />}
            {runningAll ? "Initializing..." : "Initialize All Models"}
          </button>
        </div>

        {firstError && (
          <div className="flex items-center gap-2 p-3 rounded-lg border" style={{
            backgroundColor: "var(--color-danger-bg)",
            borderColor: "var(--color-danger)"
          }}>
            <AlertCircle size={18} className="flex-shrink-0" style={{
              color: "var(--color-danger)"
            }} />
            <p className="flex-1 text-xs" style={{
              color: "var(--color-danger)"
            }}>{firstError}</p>
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <ModuleCard
            icon={TrendingDown}
            title="Churn Prediction"
            subtitle="Logistic Regression model trained on subscriber activity and recharge frequency."
            primaryMetricLabel="Accuracy"
            primaryMetricValue={churnAccuracy}
            secondaryMetricLabel="Last Run"
            secondaryMetricValue={churnLastRun}
            loadPct={0}
            actionLabel="Train Model"
            loading={churnTrain.loading}
            status={churnTrain.job?.status}
            onRun={churnTrain.train}
          />
          <ModuleCard
            icon={Users}
            title="User Segmentation"
            subtitle="K-Means clustering for customer profiling and behavioral archetypes."
            primaryMetricLabel="Dominant Share"
            primaryMetricValue={segDominantPct}
            secondaryMetricLabel="Users"
            secondaryMetricValue={segUsers}
            loadPct={68}
            actionLabel="Recalculate Model"
            loading={segmentationTrain.loading}
            status={segmentationTrain.job?.status}
            onRun={segmentationTrain.train}
          />
          <ModuleCard
            icon={AlertTriangle}
            title="Anomaly Detection"
            subtitle="Isolation Forest for detecting irregular recharge patterns and fraud."
            primaryMetricLabel="Critical Alerts"
            primaryMetricValue={anomalyCritical}
            secondaryMetricLabel="Last Run"
            secondaryMetricValue={anomalyLastRun}
            loadPct={0}
            actionLabel="Run Detection"
            loading={runDetectionLoading}
            status={detectionJob?.status}
            onRun={runDetection}
          />
        </div>

        <div className="rounded-xl border overflow-hidden" style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-bg-card)"
        }}>
          <div className="h-10 px-4 flex items-center gap-2 border-b" style={{
            borderColor: "var(--color-border)",
            backgroundColor: "var(--color-bg-elevated)"
          }}>
            <BrainCircuit size={12} style={{
              color: "var(--color-primary)"
            }} />
            <p className="text-lg tracking-wide font-semibold" style={{
              color: "var(--color-text-primary)"
            }}>
              REAL-TIME EXECUTION LOGS
            </p>
            <span className="ml-4 text-[10px]" style={{
              color: "var(--color-text-muted)"
            }}>System.uptime: 142h 12m</span>
          </div>
          <div className="max-h-64 overflow-auto p-3" style={{
            backgroundColor: "var(--color-bg-card)"
          }}>
            {mergedLogs.length === 0 ? (
              <p className="text-xs" style={{
                color: "var(--color-text-secondary)"
              }}>No logs yet.</p>
            ) : (
              <div className="space-y-1 text-xs font-mono">
                {mergedLogs.map((l, idx) => (
                  <div key={`${l.source}-${l.ts}-${idx}`} style={{
                    color: "var(--color-text-primary)"
                  }}>
                    <span className="mr-2" style={{
                      color: "var(--color-text-muted)"
                    }}>[{new Date(l.ts).toLocaleTimeString()}]</span>
                    <span className="mr-2" style={{
                      color: "var(--color-primary)"
                    }}>{l.source}</span>
                    <span>{l.message}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
