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
import { getApiErrorMessage } from "../../utils/apiError";

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
            {ok ? "✅ Import réussi" : "❌ Import échoué"}
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
                ⚠️ Erreurs détectées ({result.validation.invalid_rows}):
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
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">
            Import Data
          </h1>
          <p className="text-sm text-slate-400">
            Admin only — CSV or SQL import
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => {
              setActiveTab("csv");
              setFile(null);
              resetStateForNewFile();
            }}
            className={[
              "px-4 py-2 rounded-full text-sm font-semibold border transition",
              activeTab === "csv"
                ? "bg-violet-700 text-white border-violet-600"
                : "bg-slate-900 text-slate-300 border-slate-700 hover:bg-slate-800",
            ].join(" ")}
          >
            📄 CSV Import
          </button>
          <button
            onClick={() => {
              setActiveTab("sql");
              setFile(null);
              resetStateForNewFile();
            }}
            className={[
              "px-4 py-2 rounded-full text-sm font-semibold border transition",
              activeTab === "sql"
                ? "bg-violet-700 text-white border-violet-600"
                : "bg-slate-900 text-slate-300 border-slate-700 hover:bg-slate-800",
            ].join(" ")}
          >
            🗄️ SQL Import
          </button>
        </div>

        {/* Main card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
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
                    Append (ajouter)
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="mode"
                      checked={mode === "replace"}
                      onChange={() => setMode("replace")}
                    />
                    Replace (remplacer)
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
            className="border-dashed border-2 border-slate-600 rounded-2xl p-6 bg-slate-950/30 hover:border-purple-500 hover:bg-slate-800/20 transition cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <Upload className="text-slate-400" />
              <div className="flex-1">
                <p className="text-sm text-slate-200 font-semibold">
                  Glisser le fichier {activeTab === "csv" ? "CSV" : "SQL"} ici
                </p>
                <p className="text-xs text-slate-500">
                  ou cliquer pour sélectionner (max {maxMb}MB)
                </p>
              </div>
              {file && (
                <span className="text-xs text-slate-300 bg-slate-800 border border-slate-700 px-2 py-1 rounded-lg">
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
            className="w-full px-4 py-3 rounded-xl bg-violet-700 hover:bg-violet-800 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition"
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
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
          <h3 className="text-sm font-semibold text-slate-100">
            Import history
          </h3>
          {historyLoading && <p className="text-xs text-slate-500">Loading…</p>}
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
      </div>
    </AppLayout>
  );
}
