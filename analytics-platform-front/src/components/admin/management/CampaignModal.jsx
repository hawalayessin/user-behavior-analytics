import { useEffect, useMemo, useRef, useState } from "react";
import PropTypes from "prop-types";
import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  Download,
  Upload,
  X,
} from "lucide-react";

const MAX_FILE_SIZE = 5 * 1024 * 1024;

function getFileExtension(name = "") {
  const idx = name.lastIndexOf(".");
  return idx >= 0 ? name.slice(idx).toLowerCase() : "";
}

export default function CampaignModal({
  open,
  mode,
  initialValue,
  services,
  onUploadTargets,
  onClose,
  onSave,
}) {
  const [name, setName] = useState("");
  const [serviceId, setServiceId] = useState("");
  const [sendDate, setSendDate] = useState("");
  const [targetSize, setTargetSize] = useState("");
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [targetFile, setTargetFile] = useState(null);
  const [targetPreview, setTargetPreview] = useState([]);
  const [targetList, setTargetList] = useState([]);
  const [targetCount, setTargetCount] = useState(0);
  const [uploadErrors, setUploadErrors] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [dupesRemoved, setDupesRemoved] = useState(0);
  const [showFormatGuide, setShowFormatGuide] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    setName(initialValue?.name ?? "");
    setServiceId(initialValue?.service_id ?? "");
    setSendDate(initialValue?.send_date ?? "");
    setTargetSize(
      initialValue?.target_size != null ? String(initialValue.target_size) : "",
    );
    setErrors({});
    setSaving(false);
    setTargetFile(null);
    setTargetPreview([]);
    setTargetList([]);
    setTargetCount(0);
    setUploadErrors([]);
    setUploading(false);
    setDupesRemoved(0);
    setShowFormatGuide(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }, [open, initialValue]);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  const title = mode === "edit" ? "Edit Campaign" : "Add New Campaign";

  const payload = useMemo(() => {
    return {
      name: name.trim(),
      service_id: serviceId,
      send_date: sendDate ? new Date(sendDate).toISOString() : null,
      target_size: Number(targetSize),
      targets: targetList,
    };
  }, [name, serviceId, sendDate, targetSize, targetList]);

  const validate = () => {
    const e = {};
    if (!payload.name) e.name = "Campaign name is required.";
    if (payload.name.length > 255) e.name = "Max 255 characters.";
    if (mode === "add" && !payload.service_id)
      e.service_id = "Service is required.";
    if (!sendDate) e.send_date = "Send date is required.";
    if (!Number.isFinite(payload.target_size) || payload.target_size <= 0)
      e.target_size = "Target size must be > 0.";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const downloadTemplate = () => {
    const headers = "phone_number,segment,region\n";
    const blob = new Blob([headers], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "campaign_targets_template.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const nextErrors = [];
    const ext = getFileExtension(file.name);
    if (![".csv", ".sql"].includes(ext)) {
      nextErrors.push("Only .csv and .sql files accepted");
    }
    if (file.size > MAX_FILE_SIZE) {
      nextErrors.push("File exceeds 5MB limit");
    }
    if (nextErrors.length) {
      setUploadErrors(nextErrors);
      setTargetFile(null);
      setTargetPreview([]);
      setTargetList([]);
      setTargetCount(0);
      setDupesRemoved(0);
      return;
    }

    if (!onUploadTargets) {
      setUploadErrors(["Upload service unavailable"]);
      return;
    }

    setUploading(true);
    setUploadErrors([]);
    try {
      const res = await onUploadTargets(file);
      setTargetFile(file);
      setTargetPreview(res.preview ?? []);
      setTargetList(res.targets ?? []);
      setTargetCount(Number(res.valid ?? 0));
      setDupesRemoved(Number(res.duplicates_removed ?? 0));
      if (Number(res.valid ?? 0) > 0) {
        setTargetSize(String(res.valid));
      }

      const invalid = Array.isArray(res.invalid_phones)
        ? res.invalid_phones
        : [];
      if (invalid.length > 0) {
        setUploadErrors([`Invalid phone numbers: ${invalid.join(", ")}`]);
      }
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setUploadErrors([
        typeof detail === "string" ? detail : "Failed to parse target file",
      ]);
      setTargetFile(null);
      setTargetPreview([]);
      setTargetList([]);
      setTargetCount(0);
      setDupesRemoved(0);
    } finally {
      setUploading(false);
    }
  };

  const submit = async () => {
    if (!validate()) return;
    setSaving(true);
    try {
      const finalTargetSize =
        targetList.length > 0 ? targetList.length : payload.target_size;
      const out = {
        name: payload.name,
        send_date: payload.send_date,
        target_size: finalTargetSize,
      };
      if (mode === "add") out.service_id = payload.service_id;
      if (mode === "add" && targetList.length > 0) out.targets = targetList;
      await onSave(out);
      onClose();
    } finally {
      setSaving(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-700 rounded-2xl p-6 shadow-xl my-6 mx-auto max-h-[90vh] overflow-y-auto">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-slate-100">{title}</h3>
            <p className="text-sm text-slate-400 mt-1">
              Fill campaign details and save.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-slate-800 rounded transition text-slate-400 hover:text-slate-200"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>

        <div className="mt-5 space-y-4">
          <div>
            <label className="block text-sm text-slate-300 font-medium mb-1">
              Campaign Name *
            </label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-100 focus:outline-none focus:border-violet-500"
              placeholder="e.g. Acquisition Tawer - Nov 2025"
            />
            {errors.name && (
              <p className="text-xs text-red-300 mt-1">{errors.name}</p>
            )}
          </div>

          <div>
            <label className="block text-sm text-slate-300 font-medium mb-1">
              Service *
            </label>
            <select
              value={serviceId}
              onChange={(e) => setServiceId(e.target.value)}
              disabled={mode === "edit"}
              className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-100 focus:outline-none focus:border-violet-500 disabled:opacity-60"
            >
              <option value="">Select a service</option>
              {(services ?? []).map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
            {errors.service_id && (
              <p className="text-xs text-red-300 mt-1">{errors.service_id}</p>
            )}
            {mode === "edit" && (
              <p className="text-xs text-slate-500 mt-1">
                Service cannot be changed after creation.
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm text-slate-300 font-medium mb-1">
              Send Date *
            </label>
            <input
              type="date"
              value={sendDate}
              onChange={(e) => setSendDate(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-100 focus:outline-none focus:border-violet-500"
            />
            {errors.send_date && (
              <p className="text-xs text-red-300 mt-1">{errors.send_date}</p>
            )}
          </div>

          <div>
            <input
              value={targetSize}
              onChange={(e) => setTargetSize(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-100 focus:outline-none focus:border-violet-500"
              placeholder=""
              inputMode="numeric"
            />
            {errors.target_size && (
              <p className="text-xs text-red-300 mt-1">{errors.target_size}</p>
            )}
            {targetCount > 0 && (
              <p className="text-xs text-emerald-300 mt-1">
                Auto-filled from uploaded targets.
              </p>
            )}
          </div>

          {mode === "add" && (
            <div className="rounded-xl border border-slate-700/60 bg-slate-800/30 p-4 space-y-3">
              <div className="flex items-center justify-between gap-2">
                <div>
                  <p className="text-sm text-slate-200 font-semibold">
                    Target Audience
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Upload Target File
                  </p>
                  <p className="text-xs text-slate-500">
                    CSV or SQL file — must contain phone_number column
                  </p>
                </div>
                <button
                  type="button"
                  onClick={downloadTemplate}
                  className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-600 text-xs text-slate-200 hover:bg-slate-700/40 transition"
                >
                  <Download size={14} />
                  Template CSV
                </button>
              </div>

              <div className="rounded-lg border border-dashed border-slate-600 p-3 bg-slate-900/30">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.sql"
                  className="hidden"
                  onChange={handleFileChange}
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                  className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg border border-slate-600 text-slate-200 hover:bg-slate-700/40 disabled:opacity-60 transition"
                >
                  <Upload size={15} />
                  {uploading ? "Uploading..." : "Choose CSV or SQL file"}
                </button>

                {targetFile && (
                  <div className="mt-2 inline-flex items-center gap-2 text-xs text-emerald-300">
                    <CheckCircle2 size={14} />
                    {targetFile.name}
                  </div>
                )}
              </div>

              <button
                type="button"
                onClick={() => setShowFormatGuide((v) => !v)}
                className="w-full flex items-center justify-between px-3 py-2 rounded-lg border border-slate-700 text-sm text-slate-200 hover:bg-slate-800/50 transition"
              >
                <span>Accepted format guide</span>
                <ChevronDown
                  size={15}
                  className={`transition-transform ${showFormatGuide ? "rotate-180" : ""}`}
                />
              </button>

              {showFormatGuide && (
                <div className="text-xs text-slate-300 space-y-2 rounded-lg border border-slate-700 bg-slate-900/40 p-3">
                  <p className="font-semibold">CSV format expected:</p>
                  <pre className="whitespace-pre-wrap text-slate-400">
                    phone_number,segment,region\n+21698000001,premium,tunis\n+21621000002,basic,sfax
                  </pre>
                  <p className="font-semibold">SQL INSERT format expected:</p>
                  <pre className="whitespace-pre-wrap text-slate-400">
                    INSERT INTO campaign_targets (phone_number, segment)\nVALUES
                    ('+21698000001', 'premium'),\n ('+21621000002', 'basic');
                  </pre>
                  <p className="text-slate-400">
                    Tip: You can export phone_number directly from the
                    message_events table: SELECT DISTINCT phone_number FROM
                    message_events WHERE service_id = '&lt;your_service_id&gt;'
                    AND event_type = 'SUBSCRIPTION';
                  </p>
                </div>
              )}

              {targetCount > 0 && (
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-300">
                  <CheckCircle2 size={13} />
                  {`\u2713 ${targetCount} phone numbers loaded`}
                </div>
              )}

              {dupesRemoved > 0 && (
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-xs text-amber-300">
                  <AlertCircle size={13} />
                  {`\u26a0 ${dupesRemoved} duplicates removed automatically`}
                </div>
              )}

              {uploadErrors.length > 0 && (
                <div className="space-y-1">
                  {uploadErrors.map((err, idx) => (
                    <p key={`${err}-${idx}`} className="text-xs text-red-300">
                      {err}
                    </p>
                  ))}
                </div>
              )}

              {targetPreview.length > 0 && (
                <div className="overflow-x-auto rounded-lg border border-slate-700/60 bg-slate-900/30">
                  <table className="w-full text-xs">
                    <thead className="bg-slate-800/80 border-b border-slate-700/70">
                      <tr>
                        <th className="px-3 py-2 text-left text-slate-300 font-medium">
                          phone_number
                        </th>
                        <th className="px-3 py-2 text-left text-slate-300 font-medium">
                          segment
                        </th>
                        <th className="px-3 py-2 text-left text-slate-300 font-medium">
                          region
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700/60">
                      {targetPreview.map((row, idx) => (
                        <tr key={`${row.phone_number}-${idx}`}>
                          <td className="px-3 py-2 text-slate-200">
                            {row.phone_number || "-"}
                          </td>
                          <td className="px-3 py-2 text-slate-400">
                            {row.segment || "-"}
                          </td>
                          <td className="px-3 py-2 text-slate-400">
                            {row.region || "-"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="mt-6 flex gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="flex-1 px-4 py-2 border border-slate-700 rounded-lg text-slate-300 font-semibold hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={submit}
            disabled={saving}
            className="flex-1 px-4 py-2 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition"
          >
            {saving ? "Saving..." : "Save Campaign"}
          </button>
        </div>
      </div>
    </div>
  );
}

CampaignModal.propTypes = {
  open: PropTypes.bool.isRequired,
  mode: PropTypes.oneOf(["add", "edit"]).isRequired,
  initialValue: PropTypes.object,
  services: PropTypes.array,
  onUploadTargets: PropTypes.func,
  onClose: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired,
};
