import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Calendar,
  Check,
  ChevronLeft,
  ChevronRight,
  FileText,
  Plus,
  RotateCcw,
} from "lucide-react";
import NotePanel from "../components/notes/NotePanel";
import NotesList from "../components/notes/NotesList";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../hooks/useToast";

const METRIC_OPTIONS = ["DAU", "MAU", "WAU", "Churn", "MRR", "Conversion Rate"];
const FILTER_FIELDS = ["service_id", "metric", "period_start", "period_end"];
const WEEKDAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];

function formatDate(value) {
  if (!value) return "No date";
  return new Date(value).toLocaleDateString("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  });
}

function formatPeriod(note) {
  if (!note?.period_start && !note?.period_end) return "Open period";
  return `${note.period_start || "?"} - ${note.period_end || "?"}`;
}

function parseDateValue(value) {
  if (!value) return null;
  const [year, month, day] = value.split("-").map(Number);
  if (!year || !month || !day) return null;
  return new Date(year, month - 1, day);
}

function toDateValue(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatDisplayDate(value) {
  const date = parseDateValue(value);
  if (!date) return "Select date";
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  });
}

function buildMonthDays(monthDate) {
  const year = monthDate.getFullYear();
  const month = monthDate.getMonth();
  const firstDay = new Date(year, month, 1);
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const blanks = Array.from({ length: firstDay.getDay() }, () => null);
  const days = Array.from(
    { length: daysInMonth },
    (_, index) => new Date(year, month, index + 1),
  );
  return [...blanks, ...days];
}

function DatePickerField({ label, value, isOpen, onToggle, onChange }) {
  const selectedDate = parseDateValue(value);
  const [visibleMonth, setVisibleMonth] = useState(selectedDate || new Date());
  const monthDays = buildMonthDays(visibleMonth);
  const todayValue = toDateValue(new Date());

  const moveMonth = (offset) => {
    setVisibleMonth(
      (prev) => new Date(prev.getFullYear(), prev.getMonth() + offset, 1),
    );
  };

  return (
    <div className="relative space-y-2">
      <span className="ml-1 text-[0.6875rem] font-bold uppercase tracking-[0.14em] text-[var(--notes-subtle)]">
        {label}
      </span>
      <button
        type="button"
        onClick={onToggle}
        className={`flex w-full items-center justify-between rounded-lg border px-4 py-3 text-left text-sm outline-none transition ${
          isOpen
            ? "border-[var(--notes-primary)] bg-[var(--notes-surface-highest)] shadow-[0_0_0_3px_var(--notes-primary-soft)]"
            : "border-transparent bg-[var(--notes-surface-highest)]"
        } text-[var(--notes-text)]`}
      >
        <span className={value ? "font-medium" : "text-[var(--notes-muted)]"}>
          {formatDisplayDate(value)}
        </span>
        <Calendar size={18} className="text-[var(--notes-primary)]" />
      </button>

      {isOpen && (
        <div className="absolute left-0 top-full z-30 mt-2 w-[20rem] max-w-[calc(100vw-3rem)] rounded-xl border border-[var(--notes-divider)] bg-[var(--notes-panel-glass)] p-4 shadow-[var(--notes-modal-shadow)] backdrop-blur-2xl">
          <div className="mb-4 flex items-center justify-between">
            <button
              type="button"
              onClick={() => moveMonth(-1)}
              className="rounded-lg p-2 text-[var(--notes-muted)] transition hover:bg-[var(--notes-surface-highest)] hover:text-[var(--notes-primary)]"
              aria-label="Previous month"
            >
              <ChevronLeft size={18} />
            </button>
            <p className="text-sm font-bold text-[var(--notes-heading)]">
              {visibleMonth.toLocaleDateString("en-US", {
                month: "long",
                year: "numeric",
              })}
            </p>
            <button
              type="button"
              onClick={() => moveMonth(1)}
              className="rounded-lg p-2 text-[var(--notes-muted)] transition hover:bg-[var(--notes-surface-highest)] hover:text-[var(--notes-primary)]"
              aria-label="Next month"
            >
              <ChevronRight size={18} />
            </button>
          </div>

          <div className="grid grid-cols-7 gap-1 text-center text-[0.6875rem] font-bold uppercase tracking-[0.08em] text-[var(--notes-muted)]">
            {WEEKDAYS.map((day) => (
              <span key={day} className="py-1">
                {day}
              </span>
            ))}
          </div>

          <div className="mt-2 grid grid-cols-7 gap-1">
            {monthDays.map((date, index) => {
              if (!date) return <span key={`blank-${index}`} />;
              const dateValue = toDateValue(date);
              const selected = dateValue === value;
              const today = dateValue === todayValue;
              return (
                <button
                  type="button"
                  key={dateValue}
                  onClick={() => {
                    onChange(dateValue);
                    onToggle();
                  }}
                  className={`aspect-square rounded-lg text-sm font-semibold transition ${
                    selected
                      ? "bg-gradient-to-br from-[var(--notes-primary-strong)] to-[var(--notes-primary)] text-[var(--notes-cta-text)] shadow-[var(--notes-glow)]"
                      : "text-[var(--notes-text)] hover:bg-[var(--notes-surface-highest)]"
                  } ${today && !selected ? "ring-1 ring-[var(--notes-primary-border)]" : ""}`}
                >
                  {date.getDate()}
                </button>
              );
            })}
          </div>

          <div className="mt-4 flex items-center justify-between border-t border-[var(--notes-divider)] pt-3">
            <button
              type="button"
              onClick={() => {
                onChange("");
                onToggle();
              }}
              className="text-xs font-bold text-[var(--notes-muted)] transition hover:text-[var(--notes-primary)]"
            >
              Clear date
            </button>
            <button
              type="button"
              onClick={onToggle}
              className="rounded-lg bg-[var(--notes-surface-highest)] px-3 py-1.5 text-xs font-bold text-[var(--notes-text)] transition hover:text-[var(--notes-primary)]"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function FilterLoadingPanel() {
  return (
    <div className="relative overflow-hidden rounded-xl bg-[var(--notes-panel-glass)] p-6 shadow-[var(--notes-glow)]">
      <div className="mb-5 flex items-center gap-3">
        <span className="h-3 w-3 rounded-full bg-[var(--notes-primary)] shadow-[0_0_18px_var(--notes-primary)]" />
        <p className="text-sm font-bold text-[var(--notes-heading)]">
          Applying filters...
        </p>
        <p className="text-xs text-[var(--notes-muted)]">
          Synchronizing service and date context
        </p>
      </div>
      <div className="space-y-3">
        {[0, 1, 2].map((row) => (
          <div
            key={row}
            className="grid animate-pulse grid-cols-12 gap-4 rounded-lg bg-[var(--notes-row-alt)] p-4"
          >
            <span className="col-span-3 h-4 rounded bg-[var(--notes-surface-highest)]" />
            <span className="col-span-2 h-4 rounded bg-[var(--notes-surface-highest)]" />
            <span className="col-span-5 h-4 rounded bg-[var(--notes-surface-highest)]" />
            <span className="col-span-2 h-4 rounded bg-[var(--notes-surface-highest)]" />
          </div>
        ))}
      </div>
      <div className="notes-filter-sweep absolute inset-y-0 left-0 w-1/3 bg-gradient-to-r from-transparent via-[var(--notes-primary-soft)] to-transparent" />
    </div>
  );
}

export default function NotesPage() {
  const { role } = useAuth();
  const { showToast, Toast } = useToast();

  const [notes, setNotes] = useState([]);
  const [services, setServices] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(false);

  const [panelOpen, setPanelOpen] = useState(false);
  const [editingNote, setEditingNote] = useState(null);

  const [filters, setFilters] = useState({
    service_id: "",
    metric: "",
    period_start: "",
    period_end: "",
    analyst_id: "",
  });
  const [draftFilters, setDraftFilters] = useState({
    service_id: "",
    metric: "",
    period_start: "",
    period_end: "",
  });
  const [openCalendar, setOpenCalendar] = useState(null);
  const [filterAnimation, setFilterAnimation] = useState(false);
  const filterAnimationTimerRef = useRef(null);

  const analystOptions = useMemo(() => {
    const map = new Map();
    notes.forEach((note) => {
      if (!note.analyst_id) return;
      if (!map.has(note.analyst_id)) {
        map.set(note.analyst_id, note.analyst_name || "Unknown");
      }
    });
    return Array.from(map.entries()).map(([id, name]) => ({ id, name }));
  }, [notes]);

  const featuredNote = notes[0] || null;
  const globalNotesCount = useMemo(
    () =>
      notes.filter(
        (note) => !note.service_id && !note.campaign_id && !note.metric,
      ).length,
    [notes],
  );
  const filtersDirty = FILTER_FIELDS.some(
    (field) => draftFilters[field] !== filters[field],
  );
  const activeFilterCount = FILTER_FIELDS.filter((field) => filters[field]).length;
  const showFilterFeedback = loading || filterAnimation;

  useEffect(
    () => () => {
      if (filterAnimationTimerRef.current) {
        window.clearTimeout(filterAnimationTimerRef.current);
      }
    },
    [],
  );

  const fetchServices = useCallback(async () => {
    try {
      const res = await api.get("/services");
      setServices(res.data || []);
    } catch {
      showToast("Failed to load services", "error");
    }
  }, [showToast]);

  const fetchCampaigns = useCallback(async () => {
    try {
      const res = await api.get("/analytics/campaigns/list", {
        params: { page: 1, limit: 200 },
      });
      setCampaigns(res.data?.campaigns || []);
    } catch {
      setCampaigns([]);
    }
  }, []);

  const fetchNotes = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.service_id) params.service_id = filters.service_id;
      if (filters.metric) params.metric = filters.metric;
      if (filters.period_start) params.period_start = filters.period_start;
      if (filters.period_end) params.period_end = filters.period_end;
      if (role === "admin" && filters.analyst_id) {
        params.analyst_id = filters.analyst_id;
      }

      const res = await api.get("/notes", { params });
      setNotes(res.data || []);
    } catch {
      showToast("Failed to load notes", "error");
    } finally {
      setLoading(false);
    }
  }, [filters, role, showToast]);

  useEffect(() => {
    fetchServices();
    fetchCampaigns();
  }, [fetchServices, fetchCampaigns]);

  useEffect(() => {
    fetchNotes();
  }, [fetchNotes]);

  const handleSubmit = async (payload) => {
    try {
      if (editingNote) {
        await api.put(`/notes/${editingNote.id}`, payload);
        showToast("Note updated", "success");
      } else {
        await api.post("/notes", payload);
        showToast("Note created", "success");
      }
      setPanelOpen(false);
      setEditingNote(null);
      fetchNotes();
    } catch (err) {
      showToast(err.response?.data?.detail || "Failed to save note", "error");
    }
  };

  const handleDelete = async (note) => {
    try {
      await api.delete(`/notes/${note.id}`);
      showToast("Note deleted", "success");
      fetchNotes();
    } catch (err) {
      showToast(err.response?.data?.detail || "Failed to delete note", "error");
    }
  };

  const updateDraftFilter = (name, value) => {
    setDraftFilters((prev) => ({ ...prev, [name]: value }));
  };

  const startFilterFeedback = () => {
    if (filterAnimationTimerRef.current) {
      window.clearTimeout(filterAnimationTimerRef.current);
    }
    setFilterAnimation(true);
    filterAnimationTimerRef.current = window.setTimeout(() => {
      setFilterAnimation(false);
      filterAnimationTimerRef.current = null;
    }, 850);
  };

  const handleApplyFilters = () => {
    setOpenCalendar(null);
    startFilterFeedback();
    setFilters((prev) => ({
      ...prev,
      service_id: draftFilters.service_id,
      metric: draftFilters.metric,
      period_start: draftFilters.period_start,
      period_end: draftFilters.period_end,
    }));
  };

  const handleResetFilters = () => {
    const cleared = {
      service_id: "",
      metric: "",
      period_start: "",
      period_end: "",
    };
    setOpenCalendar(null);
    if (activeFilterCount || filtersDirty) {
      startFilterFeedback();
    }
    setDraftFilters(cleared);
    setFilters((prev) => ({ ...prev, ...cleared }));
  };

  return (
    <>
      <div className="notes-observatory -m-6 min-h-full bg-[var(--notes-bg)] p-6 text-[var(--notes-text)] lg:p-8">
        <div className="mx-auto max-w-7xl space-y-8">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <h1 className="mb-2 text-3xl font-extrabold tracking-tight text-[var(--notes-heading)]">
                Analyst Notes
              </h1>
              <p className="text-sm text-[var(--notes-subtle)]">
                Capture analytical context for reports and dashboards to bridge
                data gaps.
              </p>
            </div>
            <button
              onClick={() => {
                setEditingNote(null);
                setPanelOpen(true);
              }}
              className="inline-flex items-center gap-3 rounded-lg bg-gradient-to-br from-[var(--notes-primary-strong)] to-[var(--notes-primary)] px-6 py-3 text-sm font-bold text-[var(--notes-cta-text)] shadow-[var(--notes-glow)] transition hover:brightness-110 active:scale-95"
            >
              <Plus size={20} />
              Add Note
            </button>
          </div>

          <div className="rounded-xl bg-[var(--notes-surface-low)] p-4 shadow-[var(--notes-glow)]">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm font-bold text-[var(--notes-heading)]">
                  Filter analytical context
                </p>
                <p className="mt-1 text-xs text-[var(--notes-muted)]">
                  {activeFilterCount
                    ? `${activeFilterCount} active filter${activeFilterCount > 1 ? "s" : ""}`
                    : "No filters applied"}
                </p>
              </div>
              {filtersDirty && (
                <span className="rounded-full bg-[var(--notes-primary-soft)] px-3 py-1 text-xs font-bold text-[var(--notes-primary)]">
                  Pending changes
                </span>
              )}
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-5">
            <label className="space-y-2">
              <span className="ml-1 text-[0.6875rem] font-bold uppercase tracking-[0.14em] text-[var(--notes-subtle)]">
                Service Type
              </span>
              <select
                value={draftFilters.service_id}
                onChange={(e) => updateDraftFilter("service_id", e.target.value)}
                className="w-full rounded-lg border-0 bg-[var(--notes-surface-highest)] px-4 py-3 text-sm text-[var(--notes-text)] outline-none ring-0 focus:ring-1 focus:ring-[var(--notes-primary)]"
              >
                <option value="">All services</option>
                {services.map((service) => (
                  <option key={service.id} value={service.id}>
                    {service.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2">
              <span className="ml-1 text-[0.6875rem] font-bold uppercase tracking-[0.14em] text-[var(--notes-subtle)]">
                Metrics Category
              </span>
              <select
                value={draftFilters.metric}
                onChange={(e) => updateDraftFilter("metric", e.target.value)}
                className="w-full rounded-lg border-0 bg-[var(--notes-surface-highest)] px-4 py-3 text-sm text-[var(--notes-text)] outline-none ring-0 focus:ring-1 focus:ring-[var(--notes-primary)]"
              >
                <option value="">All metrics</option>
                {METRIC_OPTIONS.map((metric) => (
                  <option key={metric} value={metric}>
                    {metric}
                  </option>
                ))}
              </select>
            </label>

            <DatePickerField
              label="Start Date"
              value={draftFilters.period_start}
              isOpen={openCalendar === "start"}
              onToggle={() =>
                setOpenCalendar((prev) => (prev === "start" ? null : "start"))
              }
              onChange={(value) => updateDraftFilter("period_start", value)}
            />

            <DatePickerField
              label="End Date"
              value={draftFilters.period_end}
              isOpen={openCalendar === "end"}
              onToggle={() =>
                setOpenCalendar((prev) => (prev === "end" ? null : "end"))
              }
              onChange={(value) => updateDraftFilter("period_end", value)}
            />

            <div className="flex items-end gap-2">
              <button
                type="button"
                onClick={handleApplyFilters}
                disabled={!filtersDirty || showFilterFeedback}
                className="inline-flex min-h-[2.875rem] flex-1 items-center justify-center gap-2 rounded-lg bg-gradient-to-br from-[var(--notes-primary-strong)] to-[var(--notes-primary)] px-4 py-3 text-sm font-bold text-[var(--notes-cta-text)] shadow-[var(--notes-glow)] transition hover:brightness-110 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {showFilterFeedback ? (
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                ) : (
                  <Check size={17} />
                )}
                {showFilterFeedback ? "Applying..." : "Apply Filters"}
              </button>
              <button
                type="button"
                onClick={handleResetFilters}
                disabled={showFilterFeedback && !activeFilterCount}
                className="inline-flex min-h-[2.875rem] items-center justify-center rounded-lg border border-[var(--notes-divider)] bg-[var(--notes-surface-highest)] px-3 text-[var(--notes-muted)] transition hover:text-[var(--notes-primary)] disabled:cursor-not-allowed disabled:opacity-50"
                aria-label="Reset filters"
              >
                <RotateCcw size={17} />
              </button>
            </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 xl:grid-cols-12">
            <section className="rounded-xl bg-[var(--notes-surface-high)] p-6 shadow-[var(--notes-glow)] xl:col-span-8">
              {featuredNote ? (
                <>
                  <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[var(--notes-primary-soft)] text-[var(--notes-primary)]">
                        <FileText size={24} />
                      </div>
                      <div>
                        <h2 className="text-lg font-bold text-[var(--notes-heading)]">
                          {featuredNote.metric || "Contextual Analysis"}
                        </h2>
                        <p className="text-[0.6875rem] font-semibold uppercase tracking-[0.14em] text-[var(--notes-subtle)]">
                          {featuredNote.service_name || "Global context"}
                        </p>
                      </div>
                    </div>
                    <span className="rounded-full bg-[var(--notes-surface-lowest)] px-3 py-1 text-[0.6875rem] font-bold uppercase tracking-[0.12em] text-[var(--notes-primary)]">
                      Latest note
                    </span>
                  </div>
                  <p className="mb-7 text-sm leading-7 text-[var(--notes-text)]">
                    {featuredNote.content}
                  </p>
                  <div className="flex flex-wrap items-center justify-between gap-4 border-t border-[var(--notes-divider)] pt-5">
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--notes-surface-highest)] text-xs font-bold text-[var(--notes-primary)]">
                        {(featuredNote.analyst_name || "AN")
                          .split(" ")
                          .map((part) => part[0])
                          .join("")
                          .slice(0, 2)
                          .toUpperCase()}
                      </div>
                      <div>
                        <p className="text-sm font-bold text-[var(--notes-heading)]">
                          {featuredNote.analyst_name || "Analyst"}
                        </p>
                        <p className="text-[0.6875rem] uppercase tracking-[0.12em] text-[var(--notes-muted)]">
                          Created: {formatDate(featuredNote.created_at)}
                        </p>
                      </div>
                    </div>
                    <p className="text-[0.6875rem] font-bold uppercase tracking-[0.14em] text-[var(--notes-subtle)]">
                      Period: {formatPeriod(featuredNote)}
                    </p>
                  </div>
                </>
              ) : (
                <div className="flex min-h-56 flex-col items-center justify-center text-center">
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-[var(--notes-primary-soft)] text-[var(--notes-primary)]">
                    <FileText size={24} />
                  </div>
                  <h2 className="text-lg font-bold text-[var(--notes-heading)]">
                    No analytical context yet
                  </h2>
                  <p className="mt-2 max-w-md text-sm text-[var(--notes-subtle)]">
                    Create the first analyst note to document context behind KPI
                    changes and reporting assumptions.
                  </p>
                </div>
              )}
            </section>

            <aside className="rounded-xl border border-[var(--notes-primary-border)] bg-[var(--notes-primary-card)] p-6 xl:col-span-4">
              <p className="text-[0.6875rem] font-black uppercase tracking-[0.16em] text-[var(--notes-primary)]">
                Intelligence Summary
              </p>
              <h2 className="mt-3 max-w-xs text-xl font-bold leading-tight text-[var(--notes-heading)]">
                Context available across {notes.length} analytical entries
              </h2>
              <div className="py-6">
                <p className="text-5xl font-black tracking-tight text-[var(--notes-primary)]">
                  {globalNotesCount}
                </p>
                <p className="mt-1 text-sm text-[var(--notes-subtle)]">
                  Global notes without service, campaign, or metric scope
                </p>
              </div>
              <div className="flex h-20 items-end gap-2 rounded-lg bg-gradient-to-t from-[var(--notes-primary-soft)] to-transparent p-3">
                {[58, 42, 78, 64].map((height, index) => (
                  <span
                    key={index}
                    className="flex-1 rounded-sm bg-[var(--notes-primary)] opacity-40"
                    style={{ height: `${height}%` }}
                  />
                ))}
              </div>
            </aside>
          </div>

          {showFilterFeedback ? (
            <FilterLoadingPanel />
          ) : (
            <NotesList
              notes={notes}
              role={role}
              onEdit={(note) => {
                setEditingNote(note);
                setPanelOpen(true);
              }}
              onDelete={handleDelete}
              analystFilter={filters.analyst_id}
              analystOptions={analystOptions}
              onAnalystFilter={(value) =>
                setFilters((prev) => ({ ...prev, analyst_id: value }))
              }
            />
          )}
        </div>
      </div>

      <NotePanel
        open={panelOpen}
        onClose={() => setPanelOpen(false)}
        onSubmit={handleSubmit}
        services={services}
        campaigns={campaigns}
        initialNote={editingNote}
      />

      {Toast}
    </>
  );
}
