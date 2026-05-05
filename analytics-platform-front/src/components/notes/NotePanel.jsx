import React, { useEffect, useMemo, useState } from "react";
import PropTypes from "prop-types";
import { X } from "lucide-react";

const METRICS = ["DAU", "MAU", "WAU", "Churn", "MRR", "Conversion Rate"];

export default function NotePanel({
  open,
  onClose,
  onSubmit,
  services,
  campaigns,
  initialNote,
}) {
  const [form, setForm] = useState({
    service_id: "",
    campaign_id: "",
    metric: "",
    period_start: "",
    period_end: "",
    content: "",
  });
  const [isGlobal, setIsGlobal] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!initialNote) {
      setForm({
        service_id: "",
        campaign_id: "",
        metric: "",
        period_start: "",
        period_end: "",
        content: "",
      });
      setIsGlobal(false);
      return;
    }
    setForm({
      service_id: initialNote.service_id || "",
      campaign_id: initialNote.campaign_id || "",
      metric: initialNote.metric || "",
      period_start: initialNote.period_start || "",
      period_end: initialNote.period_end || "",
      content: initialNote.content || "",
    });
    setIsGlobal(
      !initialNote.service_id &&
        !initialNote.campaign_id &&
        !initialNote.metric,
    );
  }, [initialNote]);

  const title = useMemo(
    () => (initialNote ? "Edit Analyst Note" : "New Analyst Note"),
    [initialNote],
  );

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setError("");
    if (
      isGlobal &&
      (name === "service_id" || name === "campaign_id" || name === "metric")
    ) {
      setIsGlobal(false);
    }
  };

  const handleGlobalToggle = (event) => {
    const enabled = event.target.checked;
    setIsGlobal(enabled);
    if (enabled) {
      setForm((prev) => ({
        ...prev,
        service_id: "",
        campaign_id: "",
        metric: "",
      }));
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!form.content || form.content.trim().length < 10) {
      setError("Content must be at least 10 characters.");
      return;
    }
    onSubmit({
      ...form,
      service_id: form.service_id || null,
      campaign_id: form.campaign_id || null,
      metric: form.metric || null,
      period_start: form.period_start || null,
      period_end: form.period_end || null,
      content: form.content.trim(),
    });
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="absolute right-0 top-0 h-full w-full max-w-lg bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div>
            <h2 className="text-lg font-semibold text-slate-100">{title}</h2>
            <p className="text-xs text-slate-400">
              Add context to KPIs and reporting.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-400"
          >
            <X size={18} />
          </button>
        </div>

        <form
          onSubmit={handleSubmit}
          className="flex-1 overflow-y-auto p-6 space-y-4"
        >
          {error && (
            <div className="p-3 rounded-lg border border-red-500/30 bg-red-500/10 text-sm text-red-200">
              {error}
            </div>
          )}

          <div className="flex items-center gap-2">
            <input
              id="global-note"
              type="checkbox"
              checked={isGlobal}
              onChange={handleGlobalToggle}
              className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-indigo-500"
            />
            <label htmlFor="global-note" className="text-sm text-slate-300">
              Global note (no service, campaign, or metric)
            </label>
          </div>

          <div>
            <label className="text-xs uppercase tracking-wide text-slate-400">
              Service
            </label>
            <select
              name="service_id"
              value={form.service_id}
              onChange={handleChange}
              disabled={isGlobal}
              className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
            >
              <option value="">Select service</option>
              {services.map((service) => (
                <option key={service.id} value={service.id}>
                  {service.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs uppercase tracking-wide text-slate-400">
              Campaign (optional)
            </label>
            <select
              name="campaign_id"
              value={form.campaign_id}
              onChange={handleChange}
              disabled={isGlobal}
              className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
            >
              <option value="">No campaign</option>
              {campaigns.map((campaign) => (
                <option key={campaign.id} value={campaign.id}>
                  {campaign.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs uppercase tracking-wide text-slate-400">
              Metric
            </label>
            <select
              name="metric"
              value={form.metric}
              onChange={handleChange}
              disabled={isGlobal}
              className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
            >
              <option value="">Select metric</option>
              {METRICS.map((metric) => (
                <option key={metric} value={metric}>
                  {metric}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="text-xs uppercase tracking-wide text-slate-400">
                Period Start
              </label>
              <input
                type="date"
                name="period_start"
                value={form.period_start}
                onChange={handleChange}
                className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-wide text-slate-400">
                Period End
              </label>
              <input
                type="date"
                name="period_end"
                value={form.period_end}
                onChange={handleChange}
                className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
              />
            </div>
          </div>

          <div>
            <label className="text-xs uppercase tracking-wide text-slate-400">
              Content
            </label>
            <textarea
              name="content"
              value={form.content}
              onChange={handleChange}
              rows={5}
              className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
              placeholder="Write your contextual note..."
            />
            <p className="text-xs text-slate-500 mt-1">
              Minimum 10 characters.
            </p>
          </div>
        </form>

        <div className="border-t border-slate-800 px-6 py-4 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300 text-sm font-semibold"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold"
          >
            {initialNote ? "Save Changes" : "Create Note"}
          </button>
        </div>
      </div>
    </div>
  );
}

NotePanel.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  services: PropTypes.arrayOf(PropTypes.object).isRequired,
  campaigns: PropTypes.arrayOf(PropTypes.object).isRequired,
  initialNote: PropTypes.object,
};
