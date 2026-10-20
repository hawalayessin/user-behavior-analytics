/* eslint-disable react-hooks/set-state-in-effect */
import React, { useEffect, useMemo, useState } from "react";
import PropTypes from "prop-types";
import { X } from "lucide-react";

const METRICS = ["DAU", "MAU", "WAU", "Churn", "MRR", "Conversion Rate"];

const fieldClass =
  "mt-2 w-full rounded-t-lg border-0 border-b-2 border-[var(--notes-input-border)] bg-[var(--notes-input)] px-4 py-3 text-sm text-[var(--notes-text)] outline-none ring-0 transition focus:border-[var(--notes-primary)] focus:ring-0 disabled:cursor-not-allowed disabled:opacity-50";

const labelClass =
  "text-[0.6875rem] font-bold uppercase tracking-[0.14em] text-[var(--notes-subtle)]";

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
    <div className="notes-observatory fixed inset-0 z-50 flex items-center justify-center bg-[var(--notes-modal-backdrop)] px-4 backdrop-blur-sm">
      <button
        type="button"
        aria-label="Close note form"
        className="absolute inset-0 cursor-default"
        onClick={onClose}
      />

      <div className="relative flex max-h-[92vh] w-full max-w-xl flex-col overflow-hidden rounded-xl border border-[var(--notes-divider)] bg-[var(--notes-panel-glass)] shadow-[var(--notes-modal-shadow)] backdrop-blur-3xl">
        <div className="flex items-start justify-between px-8 pb-6 pt-8">
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-[var(--notes-text)]">
              {title}
            </h2>
            <p className="mt-1 text-sm font-medium text-[var(--notes-soft)] opacity-80">
              Add context to KPIs and reporting.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-2 text-[var(--notes-soft)] transition hover:bg-[var(--notes-surface-highest)] hover:text-[var(--notes-text)]"
            aria-label="Close"
          >
            <X size={22} />
          </button>
        </div>

        <form
          id="analyst-note-form"
          onSubmit={handleSubmit}
          className="flex-1 overflow-y-auto px-8 pb-8"
        >
          <div className="space-y-6">
            {error && (
              <div className="rounded-lg bg-[var(--notes-danger-bg)] p-3 text-sm text-[var(--notes-danger-text)]">
                {error}
              </div>
            )}

            <div className="flex items-center gap-3 py-1">
              <label className="relative inline-flex cursor-pointer items-center">
                <input
                  id="global-note"
                  type="checkbox"
                  checked={isGlobal}
                  onChange={handleGlobalToggle}
                  className="peer sr-only"
                />
                <span className="h-6 w-11 rounded-full bg-[var(--notes-surface-highest)] transition peer-checked:bg-[var(--notes-primary)] peer-focus:outline-none" />
                <span className="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white transition peer-checked:translate-x-5" />
              </label>
              <label
                htmlFor="global-note"
                className="text-sm font-medium tracking-wide text-[var(--notes-text)]"
              >
                Global note (no service, campaign, or metric)
              </label>
            </div>

            <div>
              <label className={labelClass}>Service</label>
              <select
                name="service_id"
                value={form.service_id}
                onChange={handleChange}
                disabled={isGlobal}
                className={fieldClass}
              >
                <option value="">Select service</option>
                {services.map((service) => (
                  <option key={service.id} value={service.id}>
                    {service.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label className={labelClass}>Campaign (optional)</label>
                <select
                  name="campaign_id"
                  value={form.campaign_id}
                  onChange={handleChange}
                  disabled={isGlobal}
                  className={fieldClass}
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
                <label className={labelClass}>Metric</label>
                <select
                  name="metric"
                  value={form.metric}
                  onChange={handleChange}
                  disabled={isGlobal}
                  className={fieldClass}
                >
                  <option value="">Select metric</option>
                  {METRICS.map((metric) => (
                    <option key={metric} value={metric}>
                      {metric}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label className={labelClass}>Period Start</label>
                <input
                  type="date"
                  name="period_start"
                  value={form.period_start}
                  onChange={handleChange}
                  className={fieldClass}
                />
              </div>
              <div>
                <label className={labelClass}>Period End</label>
                <input
                  type="date"
                  name="period_end"
                  value={form.period_end}
                  onChange={handleChange}
                  className={fieldClass}
                />
              </div>
            </div>

            <div>
              <div className="flex items-end justify-between gap-3">
                <label className={labelClass}>Content</label>
                <span
                  className={`text-[0.6875rem] font-bold ${
                    form.content.length > 0 && form.content.trim().length < 10
                      ? "text-[var(--notes-danger)]"
                      : "text-[var(--notes-muted)]"
                  }`}
                >
                  {form.content.length} / 2500
                </span>
              </div>
              <textarea
                name="content"
                value={form.content}
                onChange={handleChange}
                rows={5}
                className={`${fieldClass} resize-none`}
                placeholder="Write your contextual note..."
              />
              <p className="mt-2 text-[0.6875rem] italic text-[var(--notes-muted)]">
                Minimum 10 characters.
              </p>
            </div>
          </div>

        </form>

        <div className="flex justify-end gap-3 bg-[var(--notes-surface-low)]/60 px-8 py-6">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-[var(--notes-divider)] px-6 py-2.5 text-sm font-semibold tracking-wide text-[var(--notes-text)] transition hover:bg-[var(--notes-surface-highest)] active:scale-95"
          >
            Cancel
          </button>
          <button
            type="submit"
            form="analyst-note-form"
            className="rounded-lg bg-gradient-to-br from-[var(--notes-primary-strong)] to-[var(--notes-primary)] px-8 py-2.5 text-sm font-bold tracking-wide text-[var(--notes-cta-text)] shadow-lg transition hover:brightness-110 active:scale-95"
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
