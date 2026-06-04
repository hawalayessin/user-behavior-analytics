import { useEffect, useMemo, useRef, useState } from "react";
import {
  AlertCircle,
  Activity,
  BarChart3,
  ClipboardList,
  CreditCard,
  Database,
  DoorOpen,
  Settings,
  Smartphone,
  Tag,
  Target,
  FileText,
  FileUp,
  Upload,
  X,
  CheckCircle2,
  Download,
  Eye,
  Info,
  Layers,
  PlayCircle,
  RefreshCw,
  ShieldCheck,
  Table2,
  Terminal,
  Users,
} from "lucide-react";
import useImportData from "../../hooks/useImportData";
import { useETLPipeline } from "../../hooks/useETLPipeline";
import { getApiErrorMessage } from "../../utils/apiError";
import api from "../../services/api";

const MAX_CSV_MB = 20;
const MAX_SQL_MB = 50;
const ACCEPT_CSV = ".csv";
const ACCEPT_SQL = ".sql";
const TABLE_OPTIONS = [
  "service_types",
  "services",
  "users",
  "campaigns",
  "subscriptions",
  "billing_events",
  "unsubscriptions",
  "sms_events",
  "user_activities",
];

const OBS = {
  background: "var(--import-bg)",
  pageGradient: "var(--import-page-gradient)",
  surfaceLowest: "var(--import-surface-lowest)",
  surfaceLow: "var(--import-surface-low)",
  surface: "var(--import-surface)",
  surfaceHigh: "var(--import-surface-high)",
  surfaceHighest: "var(--import-surface-highest)",
  primary: "var(--import-primary)",
  primaryStrong: "var(--import-primary-strong)",
  primarySoft: "var(--import-primary-soft)",
  primaryBorder: "var(--import-primary-border)",
  primaryGradient: "var(--import-primary-gradient)",
  ctaText: "var(--import-cta-text)",
  text: "var(--import-text)",
  muted: "var(--import-muted)",
  subtle: "var(--import-subtle)",
  divider: "var(--import-divider)",
  borderSoft: "var(--import-border-soft)",
  panelFaint: "var(--import-panel-faint)",
  panelMuted: "var(--import-panel-muted)",
  rowStripe: "var(--import-row-stripe)",
  success: "var(--import-success)",
  successBg: "var(--import-success-bg)",
  successBorder: "var(--import-success-border)",
  warning: "var(--import-warning)",
  warningBg: "var(--import-warning-bg)",
  warningBorder: "var(--import-warning-border)",
  danger: "var(--import-danger)",
  dangerBg: "var(--import-danger-bg)",
  dangerBorder: "var(--import-danger-border)",
  codeBg: "var(--import-code-bg)",
  codeText: "var(--import-code-text)",
};

function bytesToMb(bytes) {
  return Math.round((bytes / (1024 * 1024)) * 10) / 10;
}

function SectionShell({ eyebrow, title, icon, action, children }) {
  const SectionIcon = icon;
  return (
    <section className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div
            className="flex h-10 w-10 items-center justify-center rounded-lg"
            style={{
              backgroundColor: OBS.surfaceHigh,
              color: OBS.primary,
            }}
          >
            <SectionIcon size={18} />
          </div>
          <div>
            <p
              className="text-[11px] font-bold uppercase tracking-[0.22em]"
              style={{ color: OBS.muted }}
            >
              {eyebrow}
            </p>
            <h2
              className="mt-1 text-xl font-extrabold"
              style={{ color: OBS.text, letterSpacing: 0 }}
            >
              {title}
            </h2>
          </div>
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

function StatusPill({ tone = "default", children }) {
  const tones = {
    default: { bg: OBS.surfaceHighest, color: OBS.subtle },
    success: { bg: OBS.successBg, color: OBS.success },
    warning: { bg: OBS.warningBg, color: OBS.warning },
    danger: { bg: OBS.dangerBg, color: OBS.danger },
    info: { bg: OBS.primarySoft, color: OBS.primary },
  };
  const t = tones[tone] ?? tones.default;
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-[0.12em]"
      style={{ backgroundColor: t.bg, color: t.color }}
    >
      {children}
    </span>
  );
}

function ResultBox({ result }) {
  if (!result) return null;
  const ok = result.success;
  return (
    <div
      className="rounded-xl p-5"
      style={{
        backgroundColor: ok ? OBS.successBg : OBS.dangerBg,
        boxShadow: ok
          ? `inset 0 0 0 1px ${OBS.successBorder}`
          : `inset 0 0 0 1px ${OBS.dangerBorder}`,
      }}
    >
      <div className="flex items-start gap-3">
        {ok ? (
          <CheckCircle2 className="text-emerald-400 mt-0.5" size={18} />
        ) : (
          <AlertCircle className="text-red-400 mt-0.5" size={18} />
        )}
        <div className="flex-1">
          <p className="text-sm font-bold" style={{ color: OBS.text }}>
            {ok ? "Import succeeded" : "Import failed"}
          </p>
          {result.detail && (
            <p className="mt-1 text-xs" style={{ color: OBS.subtle }}>
              {result.detail}
            </p>
          )}
          {ok && (
            <p className="text-xs mt-2" style={{ color: OBS.subtle }}>
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
                Detected errors ({result.validation.invalid_rows}):
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
              <span className="font-semibold">{valid}</span> valid rows ready to
              import
              {"  "}—{"  "}
              <span className="font-semibold">{invalid}</span> invalid rows
              detected
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
  onStop,
  isLaunching,
  isRunning,
  isStopping,
  canStop,
  error,
}) {
  const launchLabel = isLaunching
    ? "Starting..."
    : isRunning
      ? isStopping
        ? "Stopping..."
        : "Pipeline is running..."
      : "Trigger Manual Run";

  return (
    <div
      className="overflow-hidden rounded-lg"
      style={{
        backgroundColor: OBS.surfaceHigh,
        boxShadow: OBS.borderSoft,
      }}
    >
      <div className="flex flex-col gap-5 p-6 md:flex-row md:items-center md:justify-between">
        <div>
          <p
            className="text-[10px] font-black uppercase tracking-[0.22em]"
            style={{ color: OBS.muted }}
          >
            Current Task
          </p>
          <h3
            className="mt-2 text-xl font-black"
            style={{ color: OBS.text, letterSpacing: 0 }}
          >
            {mode === "prod"
              ? "Production Cluster - TN_S1"
              : "Demo Validation Cluster"}
          </h3>
          <div className="mt-3 flex flex-wrap items-center gap-4">
            <div>
              <p
                className="text-[10px] font-bold uppercase tracking-[0.14em]"
                style={{ color: OBS.muted }}
              >
                Source
              </p>
              <p className="font-mono text-xs" style={{ color: OBS.subtle }}>
                hawala_db
              </p>
            </div>
            <div
              className="h-7 w-px"
              style={{ backgroundColor: OBS.divider }}
            />
            <div>
              <p
                className="text-[10px] font-bold uppercase tracking-[0.14em]"
                style={{ color: OBS.muted }}
              >
                Target
              </p>
              <p className="font-mono text-xs" style={{ color: OBS.primary }}>
                analytics_db
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={onLaunch}
          disabled={isLaunching || isRunning}
          className="inline-flex min-h-12 items-center justify-center gap-3 rounded-lg px-7 text-sm font-black uppercase tracking-[0.12em] transition active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60"
          style={{
            background:
              isLaunching || isRunning
                ? OBS.surfaceHighest
                : OBS.primaryGradient,
            color: isLaunching || isRunning ? OBS.muted : OBS.ctaText,
            boxShadow:
              isLaunching || isRunning
                ? "none"
                : `0 0 24px ${OBS.primarySoft}`,
          }}
        >
          {isLaunching ? (
            <span
              className="inline-block h-4 w-4 rounded-full"
              style={{
                border: `2px solid ${OBS.primaryBorder}`,
                borderTopColor: OBS.ctaText,
                animation: "spin 0.8s linear infinite",
              }}
            />
          ) : (
            <PlayCircle size={18} />
          )}
          {launchLabel}
        </button>
      </div>

      <div className="grid gap-8 p-6 pt-0 lg:grid-cols-[minmax(220px,0.9fr)_minmax(300px,1.6fr)]">
        <div className="space-y-4">
          <p
            className="text-[10px] font-black uppercase tracking-[0.18em]"
            style={{ color: OBS.muted }}
          >
            Ingestion Strategy
          </p>
          <div className="grid grid-cols-2 gap-3">
            {[
              {
                value: "prod",
                label: "Full",
                desc: "Full dataset",
                icon: Database,
                tone: OBS.primaryStrong,
              },
              {
                value: "demo",
                label: "Demo",
                desc: "Stratified sample",
                icon: Settings,
                tone: OBS.muted,
              },
            ].map((opt) => {
              const StrategyIcon = opt.icon;
              const active = mode === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setMode(opt.value)}
                  className="flex min-h-24 flex-col items-center justify-center gap-2 rounded-lg text-xs font-black uppercase tracking-[0.10em] transition"
                  style={{
                    backgroundColor: active
                      ? OBS.primarySoft
                      : OBS.panelFaint,
                    color: active ? OBS.primary : OBS.muted,
                    boxShadow: active
                      ? `inset 0 0 0 1px ${OBS.primaryBorder}`
                      : OBS.borderSoft,
                  }}
                >
                  <StrategyIcon size={18} />
                  <span>{opt.label}</span>
                  <span
                    className="normal-case tracking-normal"
                    style={{ color: active ? OBS.subtle : OBS.muted }}
                  >
                    {opt.desc}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="space-y-4">
          <p
            className="text-[10px] font-black uppercase tracking-[0.18em]"
            style={{ color: OBS.muted }}
          >
            Pipeline Visualization
          </p>
          <div
            className="flex items-center rounded-lg p-5"
            style={{ backgroundColor: OBS.panelFaint }}
          >
            {[
              { label: "SFTP", icon: Download, done: true },
              { label: "Transform", icon: Settings, done: mode === "demo" },
              { label: "Database", icon: Database, done: !dryRun },
            ].map((node, idx, arr) => {
              const NodeIcon = node.icon;
              return (
                <div
                  key={node.label}
                  className="flex flex-1 items-center last:flex-none"
                >
                  <div className="flex flex-col items-center gap-2">
                    <div
                      className="flex h-9 w-9 items-center justify-center rounded"
                      style={{
                        backgroundColor: node.done
                          ? OBS.successBg
                          : OBS.panelMuted,
                        color: node.done ? OBS.success : OBS.muted,
                        boxShadow: node.done
                          ? `inset 0 0 0 1px ${OBS.successBorder}`
                          : OBS.borderSoft,
                      }}
                    >
                      <NodeIcon size={15} />
                    </div>
                    <span
                      className="text-[9px] font-black uppercase tracking-[0.12em]"
                      style={{ color: OBS.muted }}
                    >
                      {node.label}
                    </span>
                  </div>
                  {idx < arr.length - 1 && (
                    <div
                      className="mx-3 h-px flex-1"
                      style={{ backgroundColor: OBS.divider }}
                    >
                      <div
                        className="h-px"
                        style={{
                          width: node.done ? "100%" : "40%",
                          backgroundColor: node.done ? OBS.success : OBS.primary,
                        }}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="space-y-5 px-6 pb-6">
        {mode === "demo" && (
          <div>
            <label
              className="mb-3 flex justify-between text-xs font-bold"
              style={{ color: OBS.text }}
            >
              <span>Number of users (demo)</span>
              <span style={{ color: OBS.primaryStrong }}>
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
              className="w-full"
              style={{ accentColor: OBS.primaryStrong }}
            />
            <div
              className="mt-2 flex justify-between text-[11px]"
              style={{ color: OBS.muted }}
            >
              <span>5 000</span>
              <span>50 000</span>
              <span>100 000</span>
            </div>
          </div>
        )}

        <div
          className="flex items-center gap-3 rounded-lg px-4 py-3"
          style={{
            backgroundColor: dryRun
              ? OBS.panelMuted
              : OBS.panelFaint,
            color: dryRun ? OBS.muted : OBS.subtle,
          }}
        >
          <input
            type="checkbox"
            id="truncate-chk"
            checked={truncate}
            onChange={(e) => setTruncate(e.target.checked)}
            disabled={dryRun}
            style={{ accentColor: OBS.primaryStrong }}
          />
          <label
            htmlFor="truncate-chk"
            className="cursor-pointer text-sm font-semibold"
            style={{ cursor: dryRun ? "not-allowed" : "pointer" }}
          >
            Truncate analytics_db before import{" "}
            <span className="ml-1 text-xs">
              {dryRun ? "(disabled in dry-run)" : "(full reload)"}
            </span>
          </label>
        </div>

        <div
          className="flex items-center gap-3 rounded-lg px-4 py-3"
          style={{
            backgroundColor: OBS.primarySoft,
            color: OBS.text,
            boxShadow: `inset 0 0 0 1px ${OBS.primaryBorder}`,
          }}
        >
          <input
            type="checkbox"
            id="dry-run-chk"
            checked={dryRun}
            onChange={(e) => setDryRun(e.target.checked)}
            style={{ accentColor: OBS.primaryStrong }}
          />
          <label
            htmlFor="dry-run-chk"
            className="cursor-pointer text-sm font-bold"
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
          {error}
        </div>
      )}

      {canStop && (
        <button
          onClick={onStop}
          disabled={isStopping}
          style={{
            marginTop: "12px",
            width: "100%",
            padding: "12px",
            borderRadius: "10px",
            border: "1px solid var(--color-danger)",
            cursor: isStopping ? "not-allowed" : "pointer",
            backgroundColor: isStopping
              ? "var(--color-danger-bg)"
              : "transparent",
            color: "var(--color-danger)",
            fontSize: "14px",
            fontWeight: 600,
          }}
        >
          {isStopping ? "Stopping..." : "Stop ETL pipeline"}
        </button>
      )}
      </div>
    </div>
  );
}

function ETLProgressPanel({ run, ETL_STEPS }) {
  const isRunning = run?.status === "running";
  const isSuccess = run?.status === "success";
  const isFailed = run?.status === "failed";
  const isStopping = run?.status === "stopping";
  const isStopped = run?.status === "stopped";
  const isActive = isRunning || isStopping;
  const currentStep = run?.current_step ?? ETL_STEPS[0]?.key;
  const progress = run?.progress_pct ?? 0;

  const formatDuration = (sec) => {
    if (!sec) return "0s";
    if (sec < 60) return `${Math.round(sec)}s`;
    return `${Math.floor(sec / 60)}m ${Math.round(sec % 60)}s`;
  };

  const statusColor = isSuccess
    ? OBS.success
    : isFailed || isStopped
      ? OBS.danger
      : isStopping
        ? OBS.warning
        : isRunning
          ? OBS.primaryStrong
          : OBS.muted;

  const iconByStep = {
    settings: Settings,
    tag: Tag,
    users: Users,
    "clipboard-list": ClipboardList,
    "credit-card": CreditCard,
    "door-open": DoorOpen,
    "bar-chart-3": BarChart3,
    smartphone: Smartphone,
    target: Target,
  };

  return (
    <div
      className="rounded-lg p-6"
      style={{
        backgroundColor: OBS.surfaceHigh,
        boxShadow: OBS.borderSoft,
      }}
    >
      <div className="mb-7 flex items-start justify-between gap-4">
        <div>
          <h3
            className="text-sm font-black uppercase tracking-[0.16em]"
            style={{ color: OBS.subtle, letterSpacing: "0.16em" }}
          >
            Detailed Status
          </h3>
          <p className="mt-2 text-xs" style={{ color: OBS.muted }}>
            {run?.log_id ? `JOB_ID: ${run.log_id.slice(0, 8)}` : "JOB_ID: idle"}
          </p>
        </div>
        <StatusPill tone={isRunning ? "info" : isSuccess ? "success" : isFailed ? "danger" : "default"}>
          {run?.status ?? "Idle"}
        </StatusPill>
      </div>

      <div className="mb-6 grid grid-cols-2 gap-3">
        {[
          {
            label: "Inserted",
            value: (run?.rows_inserted || 0).toLocaleString("en-US"),
            color: OBS.success,
          },
          {
            label: "Duration",
            value: formatDuration(run?.duration_sec),
            color: OBS.subtle,
          },
        ].map((stat) => (
          <div
            key={stat.label}
            className="rounded-lg p-3"
            style={{ backgroundColor: OBS.panelFaint }}
          >
            <p
              className="text-[10px] font-bold uppercase tracking-[0.14em]"
              style={{ color: OBS.muted }}
            >
              {stat.label}
            </p>
            <p className="mt-1 text-sm font-black" style={{ color: stat.color }}>
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      <div className="mb-7">
        <div className="mb-2 flex items-center justify-between text-xs font-bold">
          <span style={{ color: OBS.subtle }}>
            {run
              ? `Step ${run.current_step_num ?? 1} / ${run.total_steps ?? ETL_STEPS.length}`
              : "Waiting for next run"}
          </span>
          <span style={{ color: statusColor }}>{progress}%</span>
        </div>
        <div
          className="h-1.5 overflow-hidden rounded-full"
          style={{ backgroundColor: OBS.panelMuted }}
        >
          <div
            className="h-full rounded-full transition-all"
            style={{
              width: `${progress}%`,
              backgroundColor: statusColor,
            }}
          />
        </div>
      </div>

      <div className="import-step-rail relative space-y-5 before:absolute before:left-3 before:top-3 before:bottom-3 before:w-px">
        {ETL_STEPS.map((step, idx) => {
          const isDone = !!run && (run.steps_done || []).includes(step.key);
          const isCurr = !!run && isActive && currentStep === step.key;
          const isFailedHere = isFailed && currentStep === step.key;
          const StepIcon = iconByStep[step.icon] ?? Database;
          const dotColor = isDone
            ? OBS.success
            : isFailedHere
              ? OBS.danger
              : isCurr
                ? OBS.primaryStrong
                : OBS.muted;

          return (
            <div key={step.key} className="relative flex gap-4 pl-10">
              <div
                className="absolute left-0 top-0 z-10 flex h-6 w-6 items-center justify-center rounded-full"
                style={{
                  backgroundColor: isDone
                    ? OBS.successBg
                    : isCurr
                      ? OBS.primarySoft
                      : OBS.panelMuted,
                  color: dotColor,
                  boxShadow: isDone || isCurr || isFailedHere
                    ? `inset 0 0 0 1px ${dotColor}`
                    : OBS.borderSoft,
                }}
              >
                {isDone ? <CheckCircle2 size={13} /> : <StepIcon size={12} />}
              </div>
              <div className={isCurr ? "" : !run && idx > 1 ? "opacity-45" : ""}>
                <div className="flex flex-wrap items-center gap-2">
                  <p
                    className="text-sm font-bold"
                    style={{
                      color: isCurr ? OBS.primary : isDone ? OBS.text : OBS.subtle,
                    }}
                  >
                    {step.label}
                  </p>
                  {isCurr && (
                    <span
                      className="text-[10px] font-black uppercase tracking-[0.12em]"
                      style={{ color: statusColor }}
                    >
                      {isStopping ? "Stopping" : "Running"}
                    </span>
                  )}
                </div>
                <p className="mt-1 text-xs" style={{ color: OBS.muted }}>
                  {isDone
                    ? "Completed"
                    : isCurr
                      ? "Normalizing and loading this stage..."
                      : run
                        ? "Pending"
                        : idx === 0
                          ? "Ready to extract"
                          : "Awaiting pipeline trigger"}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {isFailed && run?.error && (
        <pre
          className="mt-5 max-h-32 overflow-auto whitespace-pre-wrap rounded-lg p-3 text-xs"
          style={{
            backgroundColor: OBS.dangerBg,
            color: OBS.danger,
          }}
        >
          {run.error}
        </pre>
      )}
    </div>
  );
}

function ETLLiveLogPanel({ log, isRunning }) {
  return (
    <div
      style={{
        backgroundColor: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
        borderRadius: "12px",
        padding: "20px",
      }}
    >
      <div className="flex items-center justify-between mb-3">
        <h4
          className="text-sm font-semibold"
          style={{ color: "var(--color-text-primary)" }}
        >
          Terminal Live Logs
        </h4>
        <span
          className="text-xs px-2 py-1 rounded-full"
          style={{
            color: isRunning
              ? "var(--color-primary)"
              : "var(--color-text-muted)",
            backgroundColor: isRunning
              ? "var(--color-primary-bg)"
              : "var(--color-bg-elevated)",
            border: "1px solid var(--color-border)",
          }}
        >
          {isRunning ? "Streaming..." : "Idle"}
        </span>
      </div>
      <pre
        className="text-xs rounded-xl p-4 max-h-[320px] overflow-auto whitespace-pre-wrap"
        style={{
          backgroundColor: OBS.codeBg,
          border: "1px solid var(--color-border)",
          color: OBS.codeText,
        }}
      >
        {log || "No runtime logs yet. Start an ETL run to stream logs here."}
      </pre>
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
        label: "Success",
      },
      running: {
        bg: "var(--color-primary-bg)",
        color: "var(--color-primary)",
        label: "Running",
      },
      stopping: {
        bg: "var(--color-warning-bg)",
        color: "var(--color-warning)",
        label: "Stopping",
      },
      failed: {
        bg: "var(--color-danger-bg)",
        color: "var(--color-danger)",
        label: "Failed",
      },
      stopped: {
        bg: "var(--color-danger-bg)",
        color: "var(--color-danger)",
        label: "Stopped",
      },
      pending: {
        bg: "var(--color-amber-bg)",
        color: "var(--color-amber)",
        label: "Pending",
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
          <RefreshCw size={14} />
          {loading ? "Refreshing..." : "Refresh"}
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
          <div style={{ fontSize: "32px", marginBottom: "8px" }}>ï¿½</div>
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
  const [importLogOpen, setImportLogOpen] = useState(false);
  const [importLogContent, setImportLogContent] = useState("");
  const [importLogError, setImportLogError] = useState("");
  const [importLogLoading, setImportLogLoading] = useState(false);
  const [importLogTitle, setImportLogTitle] = useState("");
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
    getImportHistoryDetails,
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
    stopETL,
    history: etlHistory,
    historyLoading: etlHistoryLoading,
    fetchHistory: fetchEtlHistory,
    error: etlError,
    ETL_STEPS,
    runLog,
    isStopping,
  } = useETLPipeline();
  const isRunning = activeRun?.status === "running";
  const isRunStopping = activeRun?.status === "stopping";
  const isStreaming = isRunning || isRunStopping;

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

  const openImportLogDetails = async (historyItem) => {
    if (!historyItem?.id) return;
    setImportLogOpen(true);
    setImportLogLoading(true);
    setImportLogError("");
    setImportLogContent("");
    setImportLogTitle(
      `Import log — ${historyItem.file_name || historyItem.target_table || "run"}`,
    );
    try {
      const details = await getImportHistoryDetails(historyItem.id);
      setImportLogContent(JSON.stringify(details, null, 2));
    } catch (err) {
      setImportLogError(
        getApiErrorMessage(err, "Failed to load import log details"),
      );
    } finally {
      setImportLogLoading(false);
    }
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
      if (mode === "demo" || report?.demo_mode) {
        setResult({
          success: true,
          mode: "demo",
          detail:
            "Test mode completed. Validation only, no data written to database.",
          rows_inserted: report?.valid_rows ?? 0,
          rows_skipped: report?.invalid_rows ?? 0,
          validation: {
            total_rows: report?.total_rows ?? 0,
            valid_rows: report?.valid_rows ?? 0,
            invalid_rows: report?.invalid_rows ?? 0,
            errors: report?.errors ?? [],
          },
          cohorts_recalculated: false,
          duration_ms: report?.duration_ms,
        });
        setStaged(null);
        return;
      }
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
    <div
      className="import-observatory min-h-full rounded-2xl p-4 md:p-6"
      style={{
        background: OBS.pageGradient,
      }}
    >
      <div className="mx-auto max-w-[1600px] space-y-10">
        <header className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div
              className="mb-4 inline-flex items-center gap-2 rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-[0.22em]"
              style={{
                backgroundColor: OBS.primarySoft,
                color: OBS.primary,
              }}
            >
              <Database size={14} />
              Infrastructure Control
            </div>
            <h1
              className="max-w-3xl text-3xl font-black md:text-4xl"
              style={{ color: OBS.text, letterSpacing: 0 }}
            >
              Import Data Control Center
            </h1>
            <p
              className="mt-3 max-w-3xl text-sm md:text-base"
              style={{ color: OBS.subtle }}
            >
              Monitor automated ETL pipelines and validate manual telecom data
              uploads from a dense, safe administration workspace.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 lg:min-w-[520px]">
            {[
              {
                label: "Default safety",
                value: dryRun ? "Dry-run" : "Writes on",
                tone: dryRun ? "success" : "warning",
                icon: ShieldCheck,
              },
              {
                label: "Active stream",
                value: isStreaming ? "Running" : "Idle",
                tone: isStreaming ? "info" : "default",
                icon: Activity,
              },
              {
                label: "ETL steps",
                value: String(ETL_STEPS.length),
                tone: "default",
                icon: Layers,
              },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.label}
                  className="rounded-xl p-4"
                  style={{
                    backgroundColor: OBS.surfaceLow,
                    boxShadow: OBS.borderSoft,
                  }}
                >
                  <div className="flex items-center justify-between gap-3">
                    <p
                      className="text-[10px] font-bold uppercase tracking-[0.16em]"
                      style={{ color: OBS.muted }}
                    >
                      {item.label}
                    </p>
                    <Icon size={16} style={{ color: OBS.primary }} />
                  </div>
                  <div className="mt-3">
                    <StatusPill tone={item.tone}>{item.value}</StatusPill>
                  </div>
                </div>
              );
            })}
          </div>
        </header>

        <SectionShell
          eyebrow="Automated ETL"
          title="Pipeline Orchestration"
          icon={Database}
          action={
            <StatusPill tone={dryRun ? "success" : "warning"}>
              {dryRun ? "No DB write by default" : "Write mode visible"}
            </StatusPill>
          }
        >
          <div>
            <div className="mb-6 grid gap-6 xl:grid-cols-[minmax(0,2fr)_minmax(320px,1fr)]">
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
                onStop={stopETL}
                isLaunching={isLaunching}
                isRunning={isStreaming}
                isStopping={isStopping || isRunStopping}
                canStop={!!activeRun && isStreaming}
                error={etlError}
              />
            <ETLProgressPanel run={activeRun} ETL_STEPS={ETL_STEPS} />
            </div>

        {activeRun && (
          <div style={{ marginBottom: "24px" }}>
            <ETLLiveLogPanel log={runLog} isRunning={isStreaming} />
          </div>
        )}

        <ETLHistoryTable
          history={etlHistory}
          loading={etlHistoryLoading}
          onRefresh={fetchEtlHistory}
          onViewLog={handleViewEtlLog}
        />
      </div>
        </SectionShell>

      <div
        className="rounded-xl p-6 md:p-7"
        style={{
          backgroundColor: OBS.surfaceLow,
          boxShadow: OBS.borderSoft,
        }}
      >
        <p
          className="mb-2 inline-flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.22em]"
          style={{
            color: OBS.primary,
          }}
        >
          <FileUp size={14} />
          Manual Data Entry
        </p>
        <h1
          className="text-2xl font-extrabold"
          style={{ color: OBS.text, letterSpacing: 0 }}
        >
          Controlled CSV and SQL uploads
        </h1>
        <p
          className="mt-2 max-w-3xl text-sm"
          style={{ color: OBS.subtle }}
        >
          Select the file type, inspect schema requirements, preview local data,
          then validate before any import confirmation flow.
        </p>
      </div>

      {/* Tabs */}
      <div
        className="inline-flex gap-1 rounded-lg p-1"
        style={{
          backgroundColor: OBS.surfaceLowest,
          boxShadow: OBS.borderSoft,
        }}
      >
        <button
          onClick={() => {
            setActiveTab("csv");
            setFile(null);
            resetStateForNewFile();
          }}
          className={[
            "inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-bold transition",
          ].join(" ")}
          style={
            activeTab === "csv"
              ? {
                  background: OBS.primaryGradient,
                  color: OBS.ctaText,
                }
              : {
                  backgroundColor: "transparent",
                  color: OBS.subtle,
                }
          }
        >
          <Table2 size={16} />
          CSV Import
        </button>
        <button
          onClick={() => {
            setActiveTab("sql");
            setFile(null);
            resetStateForNewFile();
          }}
          className={[
            "inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-bold transition",
          ].join(" ")}
          style={
            activeTab === "sql"
              ? {
                  background: OBS.primaryGradient,
                  color: OBS.ctaText,
                }
              : {
                  backgroundColor: "transparent",
                  color: OBS.subtle,
                }
          }
        >
          <Terminal size={16} />
          SQL Import
        </button>
      </div>

      {/* Main card */}
      <div
        className="rounded-xl p-6 space-y-6"
        style={{
          backgroundColor: OBS.surfaceHigh,
          boxShadow: OBS.borderSoft,
        }}
      >
        {activeTab === "csv" ? (
          <>
            {/* Table select */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <p className="text-sm font-bold flex items-center gap-2" style={{ color: OBS.text }}>
                  <Database size={16} style={{ color: OBS.primary }} /> Target
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
                  className="px-4 py-3 rounded-lg text-sm font-semibold focus:outline-none"
                  style={{
                    backgroundColor: OBS.surfaceLowest,
                    color: OBS.text,
                    border: "0",
                    boxShadow: `inset 0 -2px 0 ${OBS.primaryBorder}`,
                  }}
                >
                  {TABLE_OPTIONS.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
                <button
                  onClick={() => downloadTemplate(targetTable)}
                  className="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-lg text-sm font-bold"
                  type="button"
                  style={{
                    backgroundColor: OBS.surfaceHighest,
                    color: OBS.subtle,
                  }}
                >
                  <Download size={16} /> Template
                </button>
              </div>
            </div>

            {/* Mode */}
            <div className="space-y-2">
              <p className="text-sm font-bold flex items-center gap-2" style={{ color: OBS.text }}>
                <Upload size={16} style={{ color: OBS.primary }} /> Import mode
              </p>
              <div className="grid gap-3 text-sm md:grid-cols-3">
                <label
                  className="flex cursor-pointer items-center gap-3 rounded-lg px-4 py-3"
                  style={{
                    backgroundColor:
                      mode === "append" ? OBS.primarySoft : OBS.surface,
                    color: mode === "append" ? OBS.primary : OBS.subtle,
                    boxShadow:
                      mode === "append"
                        ? `inset 0 0 0 1px ${OBS.primaryBorder}`
                        : OBS.borderSoft,
                  }}
                >
                  <input
                    type="radio"
                    name="mode"
                    checked={mode === "append"}
                    onChange={() => setMode("append")}
                  />
                  Append
                </label>
                <label
                  className="flex cursor-pointer items-center gap-3 rounded-lg px-4 py-3"
                  style={{
                    backgroundColor:
                      mode === "replace" ? OBS.warningBg : OBS.surface,
                    color: mode === "replace" ? OBS.warning : OBS.subtle,
                    boxShadow:
                      mode === "replace"
                        ? `inset 0 0 0 1px ${OBS.warningBorder}`
                        : OBS.borderSoft,
                  }}
                >
                  <input
                    type="radio"
                    name="mode"
                    checked={mode === "replace"}
                    onChange={() => setMode("replace")}
                  />
                  Replace
                </label>
                <label
                  className="flex cursor-pointer items-center gap-3 rounded-lg px-4 py-3"
                  style={{
                    backgroundColor:
                      mode === "demo" ? OBS.successBg : OBS.surface,
                    color: mode === "demo" ? OBS.success : OBS.subtle,
                    boxShadow:
                      mode === "demo"
                        ? `inset 0 0 0 1px ${OBS.successBorder}`
                        : OBS.borderSoft,
                  }}
                >
                  <input
                    type="radio"
                    name="mode"
                    checked={mode === "demo"}
                    onChange={() => setMode("demo")}
                  />
                  Test (No DB write)
                </label>
              </div>
              {mode === "demo" && (
                <p className="text-xs font-semibold text-emerald-300">
                  Demo mode: validation only, no business table write.
                </p>
              )}
            </div>
          </>
        ) : (
          <div className="space-y-2">
            <p className="text-sm font-bold flex items-center gap-2" style={{ color: OBS.text }}>
              <FileText size={16} style={{ color: OBS.primary }} /> SQL file
            </p>
            <p className="text-xs" style={{ color: OBS.subtle }}>
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
          className="rounded-xl p-8 transition cursor-pointer"
          style={{
            backgroundColor: OBS.surfaceLow,
            boxShadow:
              `inset 0 0 0 2px ${OBS.primaryBorder}, inset 0 -80px 120px ${OBS.primarySoft}`,
          }}
        >
          <div className="flex flex-col gap-5 md:flex-row md:items-center">
            <div
              className="flex h-14 w-14 items-center justify-center rounded-full"
              style={{
                backgroundColor: OBS.primarySoft,
                color: OBS.primary,
              }}
            >
              <Upload size={24} />
            </div>
            <div className="flex-1">
              <p
                className="text-lg font-extrabold"
                style={{ color: OBS.text, letterSpacing: 0 }}
              >
                Drag and drop your {activeTab === "csv" ? "CSV" : "SQL"} file
                here
              </p>
              <p
                className="mt-1 text-sm"
                style={{ color: OBS.subtle }}
              >
                or click to select (max {maxMb}MB)
              </p>
            </div>
            {file && (
              <span
                className="max-w-full truncate rounded-lg px-3 py-2 text-xs font-semibold md:max-w-[360px]"
                style={{
                  color: OBS.subtle,
                  backgroundColor: OBS.surfaceHighest,
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
            <p className="text-sm font-bold" style={{ color: OBS.text }}>
              Preview (first 5 rows)
            </p>
            <div
              className="rounded-xl overflow-hidden"
              style={{
                backgroundColor: OBS.surfaceLow,
                boxShadow: OBS.borderSoft,
              }}
            >
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead style={{ backgroundColor: OBS.surfaceHighest }}>
                    <tr>
                      {columns.map((c) => (
                        <th
                          key={c}
                          className="px-4 py-3 text-left font-bold uppercase tracking-[0.12em]"
                          style={{ color: OBS.muted }}
                        >
                          {c}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {preview.map((r, idx) => (
                      <tr
                        key={idx}
                        style={{
                          backgroundColor:
                            idx % 2 ? OBS.rowStripe : "transparent",
                        }}
                      >
                        {columns.map((_, i) => (
                          <td
                            key={i}
                            className="px-4 py-3"
                            style={{ color: OBS.subtle }}
                          >
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
          className="w-full rounded-lg px-4 py-4 text-sm font-black uppercase tracking-[0.14em] disabled:opacity-50 disabled:cursor-not-allowed transition"
          style={{
            background: OBS.primaryGradient,
            color: OBS.ctaText,
            boxShadow: `0 0 32px ${OBS.primarySoft}`,
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
        className="rounded-xl p-6 space-y-4"
        style={{
          backgroundColor: OBS.surfaceHigh,
          boxShadow: OBS.borderSoft,
        }}
      >
        <div className="flex items-center justify-between gap-3">
          <div>
            <p
              className="text-[11px] font-bold uppercase tracking-[0.20em]"
              style={{ color: OBS.muted }}
            >
              Manual Activity
            </p>
            <h3 className="mt-1 text-lg font-extrabold" style={{ color: OBS.text, letterSpacing: 0 }}>
              Import History
            </h3>
          </div>
          <StatusPill tone="default">{history?.length ?? 0} rows</StatusPill>
        </div>
        {historyLoading && (
          <p className="text-xs" style={{ color: OBS.subtle }}>
            Loading…
          </p>
        )}
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead style={{ backgroundColor: OBS.surfaceHighest }}>
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
                  "Details",
                ].map((h) => (
                  <th
                    key={h}
                    className="px-4 py-3 text-left font-bold uppercase tracking-[0.14em]"
                    style={{ color: OBS.muted }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(history ?? []).map((h, idx) => (
                <tr
                  key={h.id}
                  style={{
                    backgroundColor:
                      idx % 2 ? OBS.rowStripe : "transparent",
                  }}
                >
                  <td className="px-4 py-3" style={{ color: OBS.subtle }}>
                    {h.imported_at
                      ? new Date(h.imported_at).toLocaleString("fr-FR")
                      : "—"}
                  </td>
                  <td className="px-4 py-3" style={{ color: OBS.subtle }}>
                    {h.admin_name ?? "—"}
                  </td>
                  <td className="px-4 py-3" style={{ color: OBS.subtle }}>
                    {h.file_name ?? "—"}
                  </td>
                  <td className="px-4 py-3" style={{ color: OBS.subtle }}>
                    {h.file_type ?? "—"}
                  </td>
                  <td className="px-4 py-3" style={{ color: OBS.subtle }}>
                    {h.scope ?? "—"}
                  </td>
                  <td className="px-4 py-3" style={{ color: OBS.subtle }}>
                    {h.target_table ?? h.table ?? "—"}
                  </td>
                  <td className="px-4 py-3" style={{ color: OBS.subtle }}>
                    {h.mode ?? "—"}
                  </td>
                  <td className="px-4 py-3" style={{ color: OBS.subtle }}>
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
                  <td className="px-4 py-2">
                    <button
                      type="button"
                      onClick={() => openImportLogDetails(h)}
                      className="rounded-md px-3 py-1.5 text-[11px] font-bold"
                      style={{
                        backgroundColor: OBS.surfaceHighest,
                        color: OBS.subtle,
                      }}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
              {(!history || history.length === 0) && (
                <tr>
                  <td
                    colSpan={10}
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
        subtitle="Showing latest lines from the ETL runner log."
        onClose={() => setEtlLogOpen(false)}
      />

      <ETLLogModal
        open={importLogOpen}
        title={importLogTitle}
        content={importLogContent}
        error={importLogError}
        loading={importLogLoading}
        subtitle="Showing full import diagnostic payload (validation, errors, and runtime context)."
        onClose={() => setImportLogOpen(false)}
      />
      </div>
    </div>
  );
}

function ETLLogModal({
  open,
  title,
  content,
  error,
  loading,
  subtitle,
  onClose,
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-4xl bg-slate-900 border border-slate-700 rounded-2xl p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-slate-100">{title}</h3>
            <p className="text-xs text-slate-400 mt-1">
              {subtitle || "Showing latest lines from the ETL runner log."}
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
