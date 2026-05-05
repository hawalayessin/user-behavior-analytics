import { useEffect, useMemo, useRef, useState } from "react";
import {
  AlertCircle,
  Database,
  FileText,
  Upload,
  X,
  CheckCircle2,
  Download,
  Eye,
  Info,
} from "lucide-react";
import AppLayout from "../../components/layout/AppLayout";
import useImportData from "../../hooks/useImportData";
import { useETLPipeline } from "../../hooks/useETLPipeline";
import { getApiErrorMessage } from "../../utils/apiError";
import api from "../../services/api";

const MAX_CSV_MB = 20;
const MAX_SQL_MB = 50;
const ACCEPT_CSV = ".csv";
const ACCEPT_SQL = ".sql";

function bytesToMb(bytes) {
  return Math.round((bytes / (1024 * 1024)) * 10) / 10;
}

function ResultBox({ result }) {
  if (!result) return null;
  const ok = result.success;
  return (
    <div
      className={[
        "border rounded-xl p-4",
        ok
          ? "bg-emerald-500/10 border-emerald-500/30"
          : "bg-red-500/10 border-red-500/30",
      ].join(" ")}
    >
      <div className="flex items-start gap-3">
        {ok ? (
          <CheckCircle2 className="text-emerald-400 mt-0.5" size={18} />
        ) : (
          <AlertCircle className="text-red-400 mt-0.5" size={18} />
        )}
        <div className="flex-1">
          <p className="text-sm font-semibold text-slate-100">
            {ok ? "✅ Import succeeded" : "❌ Import failed"}
          </p>
          {ok && (
            <p className="text-xs text-slate-300 mt-1">
              Rows inserted:{" "}
              <span className="font-semibold">
                {result.rows_inserted ?? "—"}
              </span>{" "}
              | Skipped:{" "}
              <span className="font-semibold">
                {result.rows_skipped ?? "—"}
              </span>{" "}
              | Cohorts recalculated:{" "}
              <span className="font-semibold">
                {String(result.cohorts_recalculated ?? false)}
              </span>{" "}
              | Duration:{" "}
              <span className="font-semibold">
                {result.duration_ms ?? "—"}ms
              </span>
            </p>
          )}

          {!!result?.validation?.invalid_rows && (
            <div className="mt-3">
              <p className="text-xs font-semibold text-yellow-300">
                ⚠️ Detected errors ({result.validation.invalid_rows}):
              </p>
              <div className="mt-2 space-y-1 max-h-40 overflow-auto pr-1">
                {(result.validation.errors ?? []).slice(0, 30).map((e, idx) => (
                  <p key={idx} className="text-xs text-slate-300">
                    Row {e.row} — {e.field}: {e.error}
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ConfirmReplaceModal({ open, onCancel, onConfirm, targetTable }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-700 rounded-2xl p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-slate-100">
              Confirm replace
            </h3>
            <p className="text-sm text-slate-400 mt-1">
              This will{" "}
              <span className="text-red-300 font-semibold">TRUNCATE</span> table{" "}
              <span className="text-slate-200 font-semibold">
                {targetTable}
              </span>{" "}
              and re-import data.
            </p>
          </div>
          <button
            onClick={onCancel}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-400"
          >
            <X size={16} />
          </button>
        </div>

        <div className="mt-5 flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 text-sm rounded-lg bg-red-600 hover:bg-red-700 text-white font-semibold"
          >
            Yes, replace
          </button>
        </div>
      </div>
    </div>
  );
}

function ValidationReportModal({
  open,
  report,
  table,
  mode,
  onCancel,
  onConfirm,
}) {
  if (!open) return null;
  const invalid = report?.invalid_rows ?? 0;
  const valid = report?.valid_rows ?? 0;
  const total = report?.total_rows ?? 0;
  const errors = report?.errors ?? [];
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-3xl bg-slate-900 border border-slate-700 rounded-2xl p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-slate-100">
              Validation complete
            </h3>
            <p className="text-sm text-slate-400 mt-1">
              Table{" "}
              <span className="text-slate-200 font-semibold">{table}</span> —
              mode <span className="text-slate-200 font-semibold">{mode}</span>
            </p>
            <p className="text-sm text-slate-300 mt-3">
              ✅ <span className="font-semibold">{valid}</span> valid rows ready
              to import
              {"  "}—{"  "}❌ <span className="font-semibold">{invalid}</span>{" "}
              invalid rows detected
              {"  "}—{"  "}
              Total: <span className="font-semibold">{total}</span>
            </p>
          </div>
          <button
            onClick={onCancel}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-400"
          >
            <X size={16} />
          </button>
        </div>

        {!!invalid && (
          <div className="mt-5 border border-slate-800 rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 bg-slate-800 border-b border-slate-700">
              <p className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                <Eye size={16} className="text-slate-300" /> Errors preview (max
                200)
              </p>
              <span className="text-xs text-slate-300">
                {errors.length} shown
              </span>
            </div>
            <div className="max-h-72 overflow-auto p-3 space-y-1">
              {errors.slice(0, 200).map((e, idx) => (
                <p key={idx} className="text-xs text-slate-300">
                  Row {e.row} —{" "}
                  <span className="text-slate-200 font-semibold">
                    {e.field}
                  </span>
                  : {e.error}
                </p>
              ))}
            </div>
          </div>
        )}

        <div className="mt-6 flex flex-col sm:flex-row sm:items-center sm:justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800"
          >
            Cancel
          </button>
          <button
            onClick={() => onConfirm(false)}
            className="px-4 py-2 text-sm rounded-lg bg-violet-600 hover:bg-violet-700 text-white font-semibold"
          >
            Confirm import (valid rows only)
          </button>
          {!!invalid && (
            <button
              onClick={() => onConfirm(true)}
              className="px-4 py-2 text-sm rounded-lg bg-yellow-600 hover:bg-yellow-700 text-white font-semibold"
            >
              Force import (skip invalid)
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function ETLConfigPanel({
  mode,
  setMode,
  demoUsers,
  setDemoUsers,
  truncate,
  setTruncate,
  dryRun,
  setDryRun,
  onLaunch,
  isLaunching,
  isRunning,
  error,
}) {
  return (
    <div
      className="relative overflow-hidden"
      style={{
        background:
          "linear-gradient(135deg, color-mix(in srgb, var(--color-primary) 18%, var(--color-bg-card)) 0%, var(--color-bg-card) 55%, color-mix(in srgb, var(--color-info) 12%, var(--color-bg-card)) 100%)",
        border: "1px solid var(--color-border)",
        borderRadius: "20px",
        padding: "28px",
        boxShadow: "var(--color-card-shadow)",
      }}
    >
      <div
        className="pointer-events-none absolute -top-14 -right-10 h-44 w-44 rounded-full"
        style={{
          background:
            "radial-gradient(circle, color-mix(in srgb, var(--color-primary) 28%, transparent) 0%, transparent 70%)",
        }}
      />
      <div
        className="pointer-events-none absolute -bottom-16 -left-12 h-52 w-52 rounded-full"
        style={{
          background:
            "radial-gradient(circle, color-mix(in srgb, var(--color-info) 24%, transparent) 0%, transparent 72%)",
        }}
      />
      <p
        className="relative mb-3 inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold"
        style={{
          borderColor: "var(--color-border)",
          color: "var(--color-text-secondary)",
          backgroundColor:
            "color-mix(in srgb, var(--color-bg-elevated) 75%, transparent)",
        }}
      >
        <Database size={14} />
        Pipeline Orchestration
      </p>
      <div
        className="relative"
        style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          marginBottom: "24px",
        }}
      >
        <div
          style={{
            width: "40px",
            height: "40px",
            borderRadius: "10px",
            backgroundColor: "var(--color-primary-bg)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="var(--color-primary)"
            strokeWidth="2"
            strokeLinecap="round"
          >
            <ellipse cx="12" cy="5" rx="9" ry="3" />
            <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
          </svg>
        </div>
        <div>
          <h3
            style={{
              color: "var(--color-text-primary)",
              fontSize: "20px",
              fontWeight: 700,
              margin: 0,
            }}
          >
            ETL Pipeline — Control
          </h3>
          <p
            style={{
              color: "var(--color-text-muted)",
              fontSize: "13px",
              margin: 0,
            }}
          >
            Sync hawala_db → analytics_db
          </p>
        </div>
      </div>

      <div style={{ marginBottom: "20px" }}>
        <label
          style={{
            display: "block",
            color: "var(--color-text-secondary)",
            fontSize: "13px",
            fontWeight: 500,
            marginBottom: "10px",
          }}
        >
          Execution mode
        </label>
        <div style={{ display: "flex", gap: "12px" }}>
          {[
            {
              value: "demo",
              label: "Demo Mode",
              desc: "Stratified sample",
              icon: "⚡",
              color: "var(--color-info)",
            },
            {
              value: "prod",
              label: "Production Mode",
              desc: "Full dataset",
              icon: "🗄️",
              color: "var(--color-warning)",
            },
          ].map((opt) => (
            <div
              key={opt.value}
              onClick={() => setMode(opt.value)}
              style={{
                flex: 1,
                padding: "14px 16px",
                borderRadius: "10px",
                cursor: "pointer",
                border: `2px solid ${mode === opt.value ? opt.color : "var(--color-border)"}`,
                backgroundColor:
                  mode === opt.value
                    ? `color-mix(in srgb, ${opt.color} 10%, transparent)`
                    : "var(--color-bg-elevated)",
                transition: "all 0.15s ease",
              }}
            >
              <div style={{ fontSize: "20px", marginBottom: "4px" }}>
                {opt.icon}
              </div>
              <div
                style={{
                  color:
                    mode === opt.value
                      ? opt.color
                      : "var(--color-text-primary)",
                  fontSize: "14px",
                  fontWeight: 600,
                }}
              >
                {opt.label}
              </div>
              <div
                style={{ color: "var(--color-text-muted)", fontSize: "12px" }}
              >
                {opt.desc}
              </div>
            </div>
          ))}
        </div>
      </div>

      {mode === "demo" && (
        <div style={{ marginBottom: "20px" }}>
          <label
            style={{
              display: "flex",
              justifyContent: "space-between",
              color: "var(--color-text-secondary)",
              fontSize: "13px",
              fontWeight: 500,
              marginBottom: "8px",
            }}
          >
            <span>Number of users (demo)</span>
            <span style={{ color: "var(--color-primary)", fontWeight: 600 }}>
              {demoUsers.toLocaleString("fr-FR")}
            </span>
          </label>
          <input
            type="range"
            min={5000}
            max={100000}
            step={5000}
            value={demoUsers}
            onChange={(e) => setDemoUsers(Number(e.target.value))}
            style={{ width: "100%", accentColor: "var(--color-primary)" }}
          />
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              color: "var(--color-text-disabled)",
              fontSize: "11px",
              marginTop: "4px",
            }}
          >
            <span>5 000</span>
            <span>50 000</span>
            <span>100 000</span>
          </div>
        </div>
      )}

      <div
        className="relative"
        style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
          marginBottom: "24px",
          padding: "12px 14px",
          backgroundColor: "var(--color-bg-elevated)",
          borderRadius: "8px",
          border: "1px solid var(--color-border)",
        }}
      >
        <input
          type="checkbox"
          id="truncate-chk"
          checked={truncate}
          onChange={(e) => setTruncate(e.target.checked)}
          disabled={dryRun}
          style={{
            width: "16px",
            height: "16px",
            accentColor: "var(--color-primary)",
            cursor: "pointer",
          }}
        />
        <label
          htmlFor="truncate-chk"
          style={{
            cursor: dryRun ? "not-allowed" : "pointer",
            color: "var(--color-text-secondary)",
            fontSize: "13px",
            opacity: dryRun ? 0.6 : 1,
          }}
        >
          Truncate analytics_db before import
          <span
            style={{
              color: "var(--color-text-muted)",
              fontSize: "12px",
              marginLeft: "8px",
            }}
          >
            {dryRun
              ? "(disabled in dry-run)"
              : "(recommended for a full reload)"}
          </span>
        </label>
      </div>

      <div
        className="relative"
        style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
          marginBottom: "24px",
          padding: "12px 14px",
          backgroundColor: "var(--color-info-bg)",
          borderRadius: "8px",
          border: "1px solid var(--color-info)",
        }}
      >
        <input
          type="checkbox"
          id="dry-run-chk"
          checked={dryRun}
          onChange={(e) => setDryRun(e.target.checked)}
          style={{
            width: "16px",
            height: "16px",
            accentColor: "var(--color-primary)",
            cursor: "pointer",
          }}
        />
        <label
          htmlFor="dry-run-chk"
          style={{
            cursor: "pointer",
            color: "var(--color-text-secondary)",
            fontSize: "13px",
          }}
        >
          Test mode (dry-run): no write into analytics_db
        </label>
      </div>

      {error && (
        <div
          style={{
            padding: "12px 14px",
            marginBottom: "16px",
            borderRadius: "8px",
            backgroundColor: "var(--color-danger-bg)",
            border: "1px solid var(--color-danger)",
            color: "var(--color-danger)",
            fontSize: "13px",
          }}
        >
          ⚠️ {error}
        </div>
      )}

      <button
        onClick={onLaunch}
        disabled={isLaunching || isRunning}
        style={{
          width: "100%",
          padding: "14px",
          borderRadius: "10px",
          border: "none",
          cursor: isLaunching || isRunning ? "not-allowed" : "pointer",
          backgroundColor:
            isLaunching || isRunning
              ? "var(--color-border)"
              : "var(--color-primary)",
          color:
            isLaunching || isRunning ? "var(--color-text-disabled)" : "#ffffff",
          fontSize: "15px",
          fontWeight: 600,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "10px",
          transition: "all 0.15s ease",
        }}
      >
        {isLaunching ? (
          <>
            <span
              style={{
                display: "inline-block",
                width: "16px",
                height: "16px",
                border: "2px solid #ffffff40",
                borderTopColor: "#ffffff",
                borderRadius: "50%",
                animation: "spin 0.8s linear infinite",
              }}
            />
            Starting...
          </>
        ) : isRunning ? (
          <>⏳ Pipeline is running...</>
        ) : (
          <>▶ Run ETL pipeline</>
        )}
      </button>
    </div>
  );
}

function ETLProgressPanel({ run, ETL_STEPS }) {
  if (!run) return null;
  const isRunning = run.status === "running";
  const isSuccess = run.status === "success";
  const isFailed = run.status === "failed";

  const formatDuration = (sec) => {
    if (!sec) return "0s";
    if (sec < 60) return `${Math.round(sec)}s`;
    return `${Math.floor(sec / 60)}m ${Math.round(sec % 60)}s`;
  };

  const statusColor = isSuccess
    ? "var(--color-success)"
    : isFailed
      ? "var(--color-danger)"
      : "var(--color-primary)";

  return (
    <div
      style={{
        backgroundColor: "var(--color-bg-card)",
        border: `1px solid ${statusColor}`,
        borderRadius: "12px",
        padding: "28px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "20px",
        }}
      >
        <div>
          <h3
            style={{
              color: "var(--color-text-primary)",
              fontSize: "16px",
              fontWeight: 600,
              margin: 0,
            }}
          >
            {isRunning && "⏳ Pipeline in progress..."}
            {isSuccess && "✅ Pipeline completed successfully"}
            {isFailed && "❌ Pipeline failed"}
          </h3>
          <p
            style={{
              color: "var(--color-text-muted)",
              fontSize: "13px",
              margin: "4px 0 0 0",
            }}
          >
            Mode{" "}
            {run.mode === "demo"
              ? `demo (${(run.demo_users || 50000).toLocaleString("en-US")} users)`
              : "full production"}{" "}
            {" · "}
            {run.dry_run ? "dry-run (safe)" : "write enabled"} {" · "}Duration:{" "}
            {formatDuration(run.duration_sec)}
          </p>
        </div>
        <div style={{ display: "flex", gap: "16px" }}>
          {[
            {
              label: "Inserted rows",
              value: (run.rows_inserted || 0).toLocaleString("en-US"),
              color: "var(--color-success)",
            },
            {
              label: "Skipped rows",
              value: (run.rows_skipped || 0).toLocaleString("en-US"),
              color: "var(--color-text-muted)",
            },
          ].map((stat) => (
            <div key={stat.label} style={{ textAlign: "right" }}>
              <div
                style={{ color: stat.color, fontSize: "18px", fontWeight: 700 }}
              >
                {stat.value}
              </div>
              <div
                style={{ color: "var(--color-text-muted)", fontSize: "11px" }}
              >
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: "24px" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "6px",
          }}
        >
          <span
            style={{ color: "var(--color-text-secondary)", fontSize: "13px" }}
          >
            {isRunning
              ? `Step ${run.current_step_num} / ${run.total_steps} — ${run.current_step_label || ""}`
              : isSuccess
                ? "All steps completed"
                : `Failed at step ${run.current_step_num}`}
          </span>
          <span
            style={{ color: statusColor, fontSize: "13px", fontWeight: 600 }}
          >
            {run.progress_pct}%
          </span>
        </div>
        <div
          style={{
            height: "10px",
            borderRadius: "5px",
            backgroundColor: "var(--color-bg-elevated)",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${run.progress_pct}%`,
              backgroundColor: statusColor,
              borderRadius: "5px",
              transition: "width 0.5s ease",
            }}
          />
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
        {ETL_STEPS.map((step, idx) => {
          const isDone = (run.steps_done || []).includes(step.key);
          const isCurr = isRunning && run.current_step === step.key;
          let dotColor = "var(--color-text-disabled)";
          let textColor = "var(--color-text-disabled)";
          if (isDone) {
            dotColor = "var(--color-success)";
            textColor = "var(--color-text-secondary)";
          }
          if (isCurr) {
            dotColor = "var(--color-primary)";
            textColor = "var(--color-text-primary)";
          }
          if (isFailed && isCurr) dotColor = "var(--color-danger)";

          return (
            <div
              key={step.key}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "8px 12px",
                borderRadius: "8px",
                backgroundColor: isCurr
                  ? "var(--color-primary-bg)"
                  : "transparent",
              }}
            >
              <div
                style={{
                  width: "28px",
                  height: "28px",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "13px",
                  flexShrink: 0,
                  backgroundColor: isDone
                    ? "var(--color-success-bg)"
                    : isCurr
                      ? "var(--color-primary-bg)"
                      : "var(--color-bg-elevated)",
                  border: `1px solid ${dotColor}`,
                  color: dotColor,
                }}
              >
                {isDone ? "✓" : isCurr ? "⟳" : idx + 1}
              </div>
              <span
                style={{
                  color: textColor,
                  fontSize: "13px",
                  fontWeight: isCurr ? 500 : 400,
                }}
              >
                {step.icon} {step.label}
              </span>
              {isDone && (
                <span
                  style={{
                    marginLeft: "auto",
                    color: "var(--color-success)",
                    fontSize: "11px",
                  }}
                >
                  ✅ Done
                </span>
              )}
              {isCurr && isRunning && (
                <span
                  style={{
                    marginLeft: "auto",
                    color: "var(--color-primary)",
                    fontSize: "11px",
                    animation: "pulse 1.5s infinite",
                  }}
                >
                  Running...
                </span>
              )}
            </div>
          );
        })}
      </div>

      {isFailed && run.error && (
        <div
          style={{
            marginTop: "16px",
            padding: "12px 14px",
            borderRadius: "8px",
            backgroundColor: "var(--color-danger-bg)",
            border: "1px solid var(--color-danger)",
            color: "var(--color-danger)",
            fontSize: "12px",
            fontFamily: "monospace",
          }}
        >
          {run.error}
        </div>
      )}
    </div>
  );
}

function ETLHistoryTable({ history, loading, onRefresh, onViewLog }) {
  const PAGE_SIZE = 5;
  const [page, setPage] = useState(1);
  const totalPages = Math.max(1, Math.ceil(history.length / PAGE_SIZE));
  const pageStart = (page - 1) * PAGE_SIZE;
  const pageItems = history.slice(pageStart, pageStart + PAGE_SIZE);
  const formatDate = (iso) => {
    if (!iso) return "—";
    return new Date(iso).toLocaleString("fr-FR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };
  const formatDuration = (sec) => {
    if (!sec) return "—";
    if (sec < 60) return `${Math.round(sec)}s`;
    return `${Math.floor(sec / 60)}m ${Math.round(sec % 60)}s`;
  };

  const formatError = (value, rawValue) => {
    if (!value && !rawValue) return "—";
    const fallback = rawValue ? JSON.stringify(rawValue) : "";
    const text = String(value).replace(/\s+/g, " ").trim();
    const combined = text || fallback;
    if (!combined) return "—";
    return combined.length > 140 ? `${combined.slice(0, 140)}…` : combined;
  };

  const StatusBadge = ({ status }) => {
    const styles = {
      success: {
        bg: "var(--color-success-bg)",
        color: "var(--color-success)",
        label: "✅ Success",
      },
      running: {
        bg: "var(--color-primary-bg)",
        color: "var(--color-primary)",
        label: "⏳ Running",
      },
      failed: {
        bg: "var(--color-danger-bg)",
        color: "var(--color-danger)",
        label: "❌ Failed",
      },
      pending: {
        bg: "var(--color-amber-bg)",
        color: "var(--color-amber)",
        label: "⏸ Pending",
      },
    };
    const s = styles[status] || styles.pending;
    return (
      <span
        style={{
          backgroundColor: s.bg,
          color: s.color,
          padding: "3px 10px",
          borderRadius: "20px",
          fontSize: "12px",
          fontWeight: 500,
          whiteSpace: "nowrap",
        }}
      >
        {s.label}
      </span>
    );
  };

  return (
    <div
      style={{
        backgroundColor: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
        borderRadius: "12px",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "20px 24px",
          borderBottom: "1px solid var(--color-border)",
        }}
      >
        <div>
          <h3
            style={{
              color: "var(--color-text-primary)",
              fontSize: "16px",
              fontWeight: 600,
              margin: 0,
            }}
          >
            ETL Pipeline History
          </h3>
          <p
            style={{
              color: "var(--color-text-muted)",
              fontSize: "13px",
              margin: "2px 0 0 0",
            }}
          >
            {history.length} run(s) recorded
          </p>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          style={{
            padding: "8px 14px",
            borderRadius: "8px",
            border: "1px solid var(--color-border)",
            backgroundColor: "var(--color-bg-elevated)",
            color: "var(--color-text-secondary)",
            cursor: loading ? "not-allowed" : "pointer",
            fontSize: "13px",
            display: "flex",
            alignItems: "center",
            gap: "6px",
          }}
        >
          {loading ? "⟳" : "↻"} Refresh
        </button>
      </div>

      {loading && history.length === 0 ? (
        <div
          style={{
            padding: "48px",
            textAlign: "center",
            color: "var(--color-text-muted)",
          }}
        >
          Loading history...
        </div>
      ) : history.length === 0 ? (
        <div
          style={{
            padding: "48px",
            textAlign: "center",
            color: "var(--color-text-muted)",
          }}
        >
          <div style={{ fontSize: "32px", marginBottom: "8px" }}>🗄️</div>
          <div>No pipeline has been executed yet.</div>
          <div style={{ fontSize: "12px", marginTop: "4px" }}>
            Run your first ETL pipeline above.
          </div>
        </div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ backgroundColor: "var(--color-bg-elevated)" }}>
                {[
                  "Start date",
                  "Mode",
                  "Inserted rows",
                  "Skipped rows",
                  "Duration",
                  "Status",
                  "Error details",
                  "Log",
                ].map((col) => (
                  <th
                    key={col}
                    style={{
                      padding: "10px 16px",
                      textAlign: "left",
                      color: "var(--color-text-muted)",
                      fontSize: "12px",
                      fontWeight: 500,
                      borderBottom: "1px solid var(--color-border)",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {pageItems.map((row, i) => (
                <tr
                  key={row.id}
                  style={{
                    backgroundColor:
                      i % 2 === 0 ? "transparent" : "var(--color-bg-elevated)",
                    borderBottom: "1px solid var(--color-border)",
                  }}
                >
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "var(--color-text-secondary)",
                      fontSize: "13px",
                    }}
                  >
                    {formatDate(row.started_at)}
                  </td>
                  <td style={{ padding: "12px 16px" }}>
                    <span
                      style={{
                        backgroundColor:
                          row.mode === "demo"
                            ? "var(--color-info-bg)"
                            : "var(--color-warning-bg)",
                        color:
                          row.mode === "demo"
                            ? "var(--color-info)"
                            : "var(--color-warning)",
                        padding: "2px 10px",
                        borderRadius: "20px",
                        fontSize: "12px",
                      }}
                    >
                      {row.mode === "demo" ? "Demo" : "Production"}
                    </span>
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "var(--color-success)",
                      fontSize: "13px",
                      fontWeight: 600,
                    }}
                  >
                    {(row.rows_inserted || 0).toLocaleString("en-US")}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "var(--color-text-muted)",
                      fontSize: "13px",
                    }}
                  >
                    {(row.rows_skipped || 0).toLocaleString("en-US")}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "var(--color-text-secondary)",
                      fontSize: "13px",
                    }}
                  >
                    {formatDuration(row.duration_sec)}
                  </td>
                  <td style={{ padding: "12px 16px" }}>
                    <StatusBadge status={row.status} />
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "var(--color-text-muted)",
                      fontSize: "12px",
                      maxWidth: "360px",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                    title={
                      row.error ||
                      (row.error_raw ? JSON.stringify(row.error_raw) : "")
                    }
                  >
                    {formatError(row.error, row.error_raw)}
                  </td>
                  <td style={{ padding: "12px 16px" }}>
                    <button
                      type="button"
                      onClick={() => onViewLog?.(row)}
                      disabled={!row?.id}
                      style={{
                        padding: "6px 10px",
                        borderRadius: "8px",
                        border: "1px solid var(--color-border)",
                        backgroundColor: "var(--color-bg-elevated)",
                        color: "var(--color-text-secondary)",
                        fontSize: "12px",
                        cursor: row?.id ? "pointer" : "not-allowed",
                      }}
                    >
                      View log
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "12px 16px",
              borderTop: "1px solid var(--color-border)",
              color: "var(--color-text-muted)",
              fontSize: "12px",
            }}
          >
            <span>
              Showing {pageStart + 1}-
              {Math.min(pageStart + PAGE_SIZE, history.length)} of{" "}
              {history.length}
            </span>
            <div style={{ display: "flex", gap: "8px" }}>
              <button
                type="button"
                onClick={() => setPage((prev) => Math.max(1, prev - 1))}
                disabled={page <= 1}
                style={{
                  padding: "6px 10px",
                  borderRadius: "8px",
                  border: "1px solid var(--color-border)",
                  backgroundColor: "var(--color-bg-elevated)",
                  color: "var(--color-text-secondary)",
                  fontSize: "12px",
                  cursor: page <= 1 ? "not-allowed" : "pointer",
                }}
              >
                Prev
              </button>
              <button
                type="button"
                onClick={() =>
                  setPage((prev) => Math.min(totalPages, prev + 1))
                }
                disabled={page >= totalPages}
                style={{
                  padding: "6px 10px",
                  borderRadius: "8px",
                  border: "1px solid var(--color-border)",
                  backgroundColor: "var(--color-bg-elevated)",
                  color: "var(--color-text-secondary)",
                  fontSize: "12px",
                  cursor: page >= totalPages ? "not-allowed" : "pointer",
                }}
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ImportDataPage() {
  const [activeTab, setActiveTab] = useState("csv");
  const [targetTable, setTargetTable] = useState("service_types");
  const [mode, setMode] = useState("append");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState([]);
  const [columns, setColumns] = useState([]);
  const [result, setResult] = useState(null);
  const [confirmReplace, setConfirmReplace] = useState(false);
  const [validationModalOpen, setValidationModalOpen] = useState(false);
  const [staged, setStaged] = useState(null); // { import_id, ...report }
  const [tableSchema, setTableSchema] = useState(null);
  const [tableSchemaError, setTableSchemaError] = useState("");
  const [etlLogOpen, setEtlLogOpen] = useState(false);
  const [etlLogContent, setEtlLogContent] = useState("");
  const [etlLogError, setEtlLogError] = useState("");
  const [etlLogLoading, setEtlLogLoading] = useState(false);
  const [etlLogTitle, setEtlLogTitle] = useState("");
  const inputRef = useRef(null);

  const {
    loading,
    history,
    historyLoading,
    schemaLoading,
    stageCsv,
    confirmCsv,
    importDatabaseSql,
    downloadTemplate,
    getTableSchema,
  } = useImportData();
  const {
    mode: etlMode,
    setMode: setEtlMode,
    demoUsers,
    setDemoUsers,
    truncate,
    setTruncate,
    dryRun,
    setDryRun,
    activeRun,
    isLaunching,
    launchETL,
    history: etlHistory,
    historyLoading: etlHistoryLoading,
    fetchHistory: fetchEtlHistory,
    error: etlError,
    ETL_STEPS,
  } = useETLPipeline();
  const isRunning = activeRun?.status === "running";

  useEffect(() => {
    let mounted = true;
    setTableSchemaError("");
    getTableSchema(targetTable)
      .then((schema) => {
        if (mounted) setTableSchema(schema);
      })
      .catch((err) => {
        if (!mounted) return;
        setTableSchema(null);
        setTableSchemaError(
          getApiErrorMessage(err, "Unable to load table schema"),
        );
      });

    return () => {
      mounted = false;
    };
  }, [targetTable, getTableSchema]);

  const accept = activeTab === "csv" ? ACCEPT_CSV : ACCEPT_SQL;
  const maxMb = activeTab === "csv" ? MAX_CSV_MB : MAX_SQL_MB;

  const canSubmit = useMemo(() => {
    if (!file) return false;
    if (activeTab === "sql") return !!mode;
    return !!targetTable && !!mode;
  }, [file, activeTab, targetTable, mode]);

  const resetStateForNewFile = () => {
    setResult(null);
    setPreview([]);
    setColumns([]);
    setStaged(null);
  };

  const handleFileSelected = async (f) => {
    resetStateForNewFile();
    if (!f) return;

    if (bytesToMb(f.size) > maxMb) {
      setResult({
        success: false,
        detail: `File too large (${bytesToMb(f.size)}MB). Max ${maxMb}MB.`,
      });
      return;
    }

    const extOk =
      activeTab === "csv"
        ? f.name.toLowerCase().endsWith(".csv")
        : f.name.toLowerCase().endsWith(".sql");
    if (!extOk) {
      setResult({
        success: false,
        detail: `Invalid file type. Expected ${accept}.`,
      });
      return;
    }

    setFile(f);

    if (activeTab === "csv") {
      // Simple preview using FileReader + split CSV lines (fast + no deps)
      const text = await f.text();
      const lines = text.split(/\r?\n/).filter(Boolean).slice(0, 6);
      if (!lines.length) return;
      const header = lines[0].split(",").map((s) => s.trim());
      setColumns(header);
      const rows = lines.slice(1).map((ln) => ln.split(","));
      setPreview(rows);
    }
  };

  const onDrop = async (e) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) await handleFileSelected(f);
  };

  const handleViewEtlLog = async (row) => {
    if (!row?.id) return;
    setEtlLogLoading(true);
    setEtlLogError("");
    setEtlLogContent("");
    setEtlLogTitle(`ETL log — ${row.id}`);
    setEtlLogOpen(true);
    try {
      const res = await api.get(`/admin/import/run-etl/${row.id}/log`, {
        params: { limit: 300 },
      });
      setEtlLogContent(res.data?.log || "No log content returned.");
    } catch (err) {
      setEtlLogError(getApiErrorMessage(err, "Unable to load ETL log."));
    } finally {
      setEtlLogLoading(false);
    }
  };

  const submitCsv = async () => {
    if (!file) return;
    setResult(null);
    try {
      const report = await stageCsv({ file, table: targetTable, mode });
      setStaged(report);
      setValidationModalOpen(true);
    } catch (err) {
      setResult({
        success: false,
        detail: getApiErrorMessage(err, "Import failed"),
      });
    }
  };

  const submitSql = async () => {
    if (!file) return;
    setResult(null);
    try {
      const res = await importDatabaseSql({ file, mode });
      setResult(res);
    } catch (err) {
      setResult({
        success: false,
        detail: getApiErrorMessage(err, "SQL import failed"),
      });
    }
  };

  const handleSubmit = async () => {
    if (!canSubmit) return;
    if (activeTab === "csv" && mode === "replace") {
      setConfirmReplace(true);
      return;
    }
    if (activeTab === "csv") return submitCsv();
    return submitSql();
  };

  return (
    <AppLayout pageTitle="Import Data">
      <div className="space-y-6">
        <div style={{ marginBottom: "32px" }}>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: activeRun ? "1fr 1fr" : "1fr",
              gap: "24px",
              marginBottom: "24px",
            }}
          >
            <ETLConfigPanel
              mode={etlMode}
              setMode={setEtlMode}
              demoUsers={demoUsers}
              setDemoUsers={setDemoUsers}
              truncate={truncate}
              setTruncate={setTruncate}
              dryRun={dryRun}
              setDryRun={setDryRun}
              onLaunch={launchETL}
              isLaunching={isLaunching}
              isRunning={isRunning}
              error={etlError}
            />
            {activeRun && (
              <ETLProgressPanel run={activeRun} ETL_STEPS={ETL_STEPS} />
            )}
          </div>

          <ETLHistoryTable
            history={etlHistory}
            loading={etlHistoryLoading}
            onRefresh={fetchEtlHistory}
            onViewLog={handleViewEtlLog}
          />
        </div>

        <div
          className="relative overflow-hidden rounded-3xl border p-6 md:p-8"
          style={{
            borderColor: "var(--color-border)",
            background:
              "linear-gradient(135deg, color-mix(in srgb, var(--color-primary) 18%, var(--color-bg-card)) 0%, var(--color-bg-card) 55%, color-mix(in srgb, var(--color-info) 12%, var(--color-bg-card)) 100%)",
            boxShadow: "var(--color-card-shadow)",
          }}
        >
          <div
            className="pointer-events-none absolute -top-14 -right-10 h-44 w-44 rounded-full"
            style={{
              background:
                "radial-gradient(circle, color-mix(in srgb, var(--color-primary) 28%, transparent) 0%, transparent 70%)",
            }}
          />
          <p
            className="relative mb-2 inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold"
            style={{
              borderColor: "var(--color-border)",
              color: "var(--color-text-secondary)",
              backgroundColor:
                "color-mix(in srgb, var(--color-bg-elevated) 75%, transparent)",
            }}
          >
            <Database size={14} />
            Administration Pipeline & Imports
          </p>
          <h1
            className="relative text-3xl font-bold tracking-tight md:text-4xl"
            style={{ color: "var(--color-text-primary)" }}
          >
            Import Data Control Center
          </h1>
          <p
            className="relative mt-2 max-w-3xl text-sm md:text-base"
            style={{ color: "var(--color-text-muted)" }}
          >
            Manage CSV/SQL imports and ETL pipeline control from one unified
            interface. All actions are logged and restricted to administrators.
          </p>
        </div>

        {/* Tabs */}
        <div
          className="inline-flex gap-2 rounded-2xl border p-1.5"
          style={{
            borderColor: "var(--color-border)",
            backgroundColor: "var(--color-bg-card)",
          }}
        >
          <button
            onClick={() => {
              setActiveTab("csv");
              setFile(null);
              resetStateForNewFile();
            }}
            className={[
              "px-4 py-2 rounded-xl text-sm font-semibold border transition",
            ].join(" ")}
            style={
              activeTab === "csv"
                ? {
                    backgroundColor: "var(--color-primary)",
                    color: "#fff",
                    borderColor: "var(--color-primary)",
                  }
                : {
                    backgroundColor: "var(--color-bg-elevated)",
                    color: "var(--color-text-secondary)",
                    borderColor: "var(--color-border)",
                  }
            }
          >
            CSV Import
          </button>
          <button
            onClick={() => {
              setActiveTab("sql");
              setFile(null);
              resetStateForNewFile();
            }}
            className={[
              "px-4 py-2 rounded-xl text-sm font-semibold border transition",
            ].join(" ")}
            style={
              activeTab === "sql"
                ? {
                    backgroundColor: "var(--color-primary)",
                    color: "#fff",
                    borderColor: "var(--color-primary)",
                  }
                : {
                    backgroundColor: "var(--color-bg-elevated)",
                    color: "var(--color-text-secondary)",
                    borderColor: "var(--color-border)",
                  }
            }
          >
            SQL Import
          </button>
        </div>

        {/* Main card */}
        <div
          className="rounded-3xl border p-6 space-y-6"
          style={{
            backgroundColor: "var(--color-bg-card)",
            borderColor: "var(--color-border)",
            boxShadow: "var(--color-card-shadow)",
          }}
        >
          {activeTab === "csv" ? (
            <>
              {/* Table select */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                    <Database size={16} className="text-slate-400" /> Target
                    table
                  </p>
                  <div className="group relative">
                    <button
                      type="button"
                      className="inline-flex items-center justify-center rounded-full p-1 text-slate-400 hover:text-slate-200 hover:bg-slate-800/70 transition"
                      aria-label="Show selected table schema"
                    >
                      <Info size={14} />
                    </button>
                    <div className="invisible opacity-0 group-hover:visible group-hover:opacity-100 transition absolute z-20 top-8 left-0 w-[420px] rounded-xl border border-slate-700 bg-slate-900/95 backdrop-blur-sm p-4 shadow-2xl">
                      <div className="flex items-start justify-between gap-3 mb-3">
                        <div>
                          <p className="text-xs uppercase tracking-wide text-slate-400">
                            Schema preview
                          </p>
                          <p className="text-sm font-semibold text-slate-100 mt-0.5">
                            {targetTable}
                          </p>
                        </div>
                        {schemaLoading && (
                          <span className="text-[11px] px-2 py-1 rounded-md border border-slate-700 bg-slate-800 text-slate-300">
                            Loading...
                          </span>
                        )}
                      </div>

                      {tableSchemaError ? (
                        <p className="text-xs text-red-300">
                          {tableSchemaError}
                        </p>
                      ) : tableSchema ? (
                        <div className="space-y-3">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-[11px] px-2 py-1 rounded-full bg-violet-500/10 border border-violet-500/30 text-violet-200">
                              Required {tableSchema.required?.length ?? 0}
                            </span>
                            <span className="text-[11px] px-2 py-1 rounded-full bg-slate-700/60 border border-slate-600 text-slate-200">
                              Optional {tableSchema.optional?.length ?? 0}
                            </span>
                            <span className="text-[11px] px-2 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-200">
                              Defaults excluded{" "}
                              {tableSchema.defaults_excluded?.length ?? 0}
                            </span>
                            <span className="text-[11px] px-2 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-200">
                              Import order {tableSchema.import_order ?? "-"}
                            </span>
                          </div>

                          <div className="max-h-52 overflow-auto rounded-lg border border-slate-800">
                            <table className="w-full text-[11px]">
                              <thead className="bg-slate-800 border-b border-slate-700">
                                <tr>
                                  <th className="px-3 py-2 text-left text-slate-300 font-semibold">
                                    Column
                                  </th>
                                  <th className="px-3 py-2 text-left text-slate-300 font-semibold">
                                    Role
                                  </th>
                                  <th className="px-3 py-2 text-left text-slate-300 font-semibold">
                                    Relation
                                  </th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-slate-800">
                                {(tableSchema.columns ?? []).map((col) => (
                                  <tr
                                    key={col.name}
                                    className="hover:bg-slate-800/40"
                                  >
                                    <td className="px-3 py-2 text-slate-200 font-medium">
                                      {col.name}
                                    </td>
                                    <td className="px-3 py-2">
                                      <span
                                        className={[
                                          "px-2 py-0.5 rounded-full border text-[10px] uppercase tracking-wide",
                                          col.role === "required"
                                            ? "bg-violet-500/10 border-violet-500/30 text-violet-200"
                                            : "bg-slate-700/60 border-slate-600 text-slate-200",
                                        ].join(" ")}
                                      >
                                        {col.role}
                                      </span>
                                    </td>
                                    <td className="px-3 py-2 text-slate-400">
                                      {col.fk ?? "-"}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      ) : (
                        <p className="text-xs text-slate-400">
                          No schema available for this table.
                        </p>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                  <select
                    value={targetTable}
                    onChange={(e) => setTargetTable(e.target.value)}
                    className="px-3 py-2 rounded-xl bg-slate-800/50 border border-slate-700 text-slate-200 focus:outline-none focus:border-violet-500"
                  >
                    {[
                      "service_types",
                      "services",
                      "users",
                      "campaigns",
                      "subscriptions",
                      "billing_events",
                      "unsubscriptions",
                      "sms_events",
                      "user_activities",
                    ].map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => downloadTemplate(targetTable)}
                    className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-slate-800 border border-slate-700 text-slate-200 hover:bg-slate-700/60"
                    type="button"
                  >
                    <Download size={16} /> Template
                  </button>
                </div>
              </div>

              {/* Mode */}
              <div className="space-y-2">
                <p className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                  <Upload size={16} className="text-slate-400" /> Import mode
                </p>
                <div className="flex items-center gap-6 text-sm text-slate-300">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="mode"
                      checked={mode === "append"}
                      onChange={() => setMode("append")}
                    />
                    Append
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="mode"
                      checked={mode === "replace"}
                      onChange={() => setMode("replace")}
                    />
                    Replace
                  </label>
                </div>
              </div>
            </>
          ) : (
            <div className="space-y-2">
              <p className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <FileText size={16} className="text-slate-400" /> SQL file
              </p>
              <p className="text-xs text-slate-400">
                Only INSERT/COPY allowed.
                DROP/DELETE/TRUNCATE/ALTER/CREATE/UPDATE will be rejected.
              </p>
            </div>
          )}

          {/* Drop zone */}
          <div
            onDrop={onDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => inputRef.current?.click()}
            className="border-dashed border-2 rounded-2xl p-6 transition cursor-pointer"
            style={{
              borderColor:
                "color-mix(in srgb, var(--color-primary) 40%, var(--color-border))",
              background:
                "linear-gradient(180deg, color-mix(in srgb, var(--color-primary-bg) 60%, transparent) 0%, color-mix(in srgb, var(--color-bg-elevated) 55%, transparent) 100%)",
            }}
          >
            <div className="flex items-center gap-3">
              <div
                className="flex h-10 w-10 items-center justify-center rounded-xl border"
                style={{
                  borderColor: "var(--color-border)",
                  backgroundColor: "var(--color-bg-elevated)",
                  color: "var(--color-primary)",
                }}
              >
                <Upload size={18} />
              </div>
              <div className="flex-1">
                <p
                  className="text-sm font-semibold"
                  style={{ color: "var(--color-text-primary)" }}
                >
                  Drag and drop your {activeTab === "csv" ? "CSV" : "SQL"} file
                  here
                </p>
                <p
                  className="text-xs"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  or click to select (max {maxMb}MB)
                </p>
              </div>
              {file && (
                <span
                  className="text-xs px-2 py-1 rounded-lg"
                  style={{
                    color: "var(--color-text-secondary)",
                    backgroundColor: "var(--color-bg-elevated)",
                    border: "1px solid var(--color-border)",
                  }}
                >
                  {file.name} ({bytesToMb(file.size)}MB)
                </span>
              )}
            </div>

            <input
              ref={inputRef}
              type="file"
              accept={accept}
              className="hidden"
              onChange={(e) => handleFileSelected(e.target.files?.[0] ?? null)}
            />
          </div>

          {/* Preview */}
          {activeTab === "csv" && columns.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-semibold text-slate-200">
                Preview (first 5 rows)
              </p>
              <div className="border border-slate-800 rounded-xl overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead className="bg-slate-800 border-b border-slate-700">
                      <tr>
                        {columns.map((c) => (
                          <th
                            key={c}
                            className="px-4 py-2 text-left text-slate-300 font-semibold"
                          >
                            {c}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {preview.map((r, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/30">
                          {columns.map((_, i) => (
                            <td key={i} className="px-4 py-2 text-slate-300">
                              {r[i] ?? ""}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          <button
            disabled={!canSubmit || loading}
            onClick={handleSubmit}
            className="w-full px-4 py-3 rounded-xl text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition"
            style={{
              background:
                "linear-gradient(135deg, var(--color-primary) 0%, color-mix(in srgb, var(--color-primary) 75%, var(--color-info)) 100%)",
              boxShadow:
                "0 10px 30px color-mix(in srgb, var(--color-primary) 30%, transparent)",
            }}
          >
            {loading
              ? "Working..."
              : activeTab === "csv"
                ? "Validate & Import"
                : "Run database import"}
          </button>
        </div>

        {/* Result */}
        {result && (
          <ResultBox
            result={{
              ...result,
              success: !!result.success,
              validation: result.validation,
            }}
          />
        )}

        {/* History */}
        <div
          className="rounded-2xl border p-6 space-y-3"
          style={{
            backgroundColor: "var(--color-bg-card)",
            borderColor: "var(--color-border)",
            boxShadow: "var(--color-card-shadow)",
          }}
        >
          <h3
            className="text-sm font-semibold"
            style={{ color: "var(--color-text-primary)" }}
          >
            Import history
          </h3>
          {historyLoading && (
            <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
              Loading…
            </p>
          )}
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead className="bg-slate-800 border-b border-slate-700">
                <tr>
                  {[
                    "Date",
                    "Admin",
                    "File",
                    "Type",
                    "Scope",
                    "Table",
                    "Mode",
                    "Rows",
                    "Status",
                  ].map((h) => (
                    <th
                      key={h}
                      className="px-4 py-2 text-left text-slate-300 font-semibold"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {(history ?? []).map((h) => (
                  <tr key={h.id} className="hover:bg-slate-800/30">
                    <td className="px-4 py-2 text-slate-300">
                      {h.imported_at
                        ? new Date(h.imported_at).toLocaleString("fr-FR")
                        : "—"}
                    </td>
                    <td className="px-4 py-2 text-slate-300">
                      {h.admin_name ?? "—"}
                    </td>
                    <td className="px-4 py-2 text-slate-300">
                      {h.file_name ?? "—"}
                    </td>
                    <td className="px-4 py-2 text-slate-300">
                      {h.file_type ?? "—"}
                    </td>
                    <td className="px-4 py-2 text-slate-300">
                      {h.scope ?? "—"}
                    </td>
                    <td className="px-4 py-2 text-slate-300">
                      {h.target_table ?? h.table ?? "—"}
                    </td>
                    <td className="px-4 py-2 text-slate-300">
                      {h.mode ?? "—"}
                    </td>
                    <td className="px-4 py-2 text-slate-300">
                      {(h.rows_inserted ?? 0).toLocaleString()} /{" "}
                      {(h.rows_skipped ?? 0).toLocaleString()}
                    </td>
                    <td className="px-4 py-2">
                      <span
                        className={[
                          "px-2 py-1 rounded-full border text-[11px] capitalize",
                          h.status === "success"
                            ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                            : h.status === "partial"
                              ? "bg-yellow-500/10 border-yellow-500/30 text-yellow-300"
                              : "bg-red-500/10 border-red-500/30 text-red-300",
                        ].join(" ")}
                      >
                        {h.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {(!history || history.length === 0) && (
                  <tr>
                    <td
                      colSpan={9}
                      className="px-4 py-8 text-center text-slate-500"
                    >
                      No import history yet
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <ConfirmReplaceModal
          open={confirmReplace}
          targetTable={targetTable}
          onCancel={() => setConfirmReplace(false)}
          onConfirm={async () => {
            setConfirmReplace(false);
            await submitCsv();
          }}
        />

        <ValidationReportModal
          open={validationModalOpen}
          report={staged}
          table={targetTable}
          mode={mode}
          onCancel={() => {
            setValidationModalOpen(false);
            setStaged(null);
          }}
          onConfirm={async (force) => {
            if (!staged?.import_id) return;
            setValidationModalOpen(false);
            try {
              const res = await confirmCsv({
                importId: staged.import_id,
                table: targetTable,
                mode,
                force,
              });
              setResult(res);
              setStaged(null);
              setFile(null);
            } catch (e) {
              setResult({
                success: false,
                detail: getApiErrorMessage(e, "Confirm failed"),
              });
            }
          }}
        />

        <ETLLogModal
          open={etlLogOpen}
          title={etlLogTitle}
          content={etlLogContent}
          error={etlLogError}
          loading={etlLogLoading}
          onClose={() => setEtlLogOpen(false)}
        />
      </div>
    </AppLayout>
  );
}

function ETLLogModal({ open, title, content, error, loading, onClose }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-4xl bg-slate-900 border border-slate-700 rounded-2xl p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-slate-100">{title}</h3>
            <p className="text-xs text-slate-400 mt-1">
              Showing latest lines from the ETL runner log.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-400"
          >
            <X size={16} />
          </button>
        </div>

        <div className="mt-4">
          {loading && (
            <div className="text-sm text-slate-400">Loading log...</div>
          )}
          {!loading && error && (
            <div className="text-sm text-red-300">{error}</div>
          )}
          {!loading && !error && (
            <pre className="text-xs text-slate-200 bg-slate-950 border border-slate-800 rounded-xl p-4 max-h-[60vh] overflow-auto whitespace-pre-wrap">
              {content || "No log content available."}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
