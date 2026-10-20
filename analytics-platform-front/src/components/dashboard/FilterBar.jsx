import { useEffect, useMemo, useRef, useState } from "react";
import {
  Calendar,
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
} from "lucide-react";
import PropTypes from "prop-types";
import { useQuery } from "@tanstack/react-query";
import api from "../../services/api";
import { isDemoMode } from "../../demo/config";

const WEEKDAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];

function formatDate(d) {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function parseIsoDateToLocal(isoDate) {
  if (!isoDate) return null;
  const [y, m, d] = String(isoDate).split("-").map(Number);
  if (!y || !m || !d) return null;
  return new Date(y, m - 1, d, 12, 0, 0, 0);
}

function formatDisplayDate(value) {
  const date = parseIsoDateToLocal(value);
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
  return [
    ...Array.from({ length: firstDay.getDay() }, () => null),
    ...Array.from(
      { length: daysInMonth },
      (_, index) => new Date(year, month, index + 1),
    ),
  ];
}

function computeDates(period, customStart, customEnd, anchorDate) {
  const today = parseIsoDateToLocal(anchorDate) ?? new Date();
  switch (period) {
    case "all":
      return { start: null, end: null };
    case "today":
      return { start: formatDate(today), end: formatDate(today) };
    case "7days":
      return {
        start: formatDate(new Date(today - 7 * 864e5)),
        end: formatDate(today),
      };
    case "30days":
      return {
        start: formatDate(new Date(today - 30 * 864e5)),
        end: formatDate(today),
      };
    case "3months":
      return {
        start: formatDate(new Date(today - 90 * 864e5)),
        end: formatDate(today),
      };
    case "custom":
      return { start: customStart, end: customEnd };
    default:
      return { start: null, end: null };
  }
}

const PERIOD_OPTIONS = [
  { value: "all", label: "All time" },
  { value: "today", label: "Today" },
  { value: "7days", label: "Last 7 days" },
  { value: "30days", label: "Last 30 days" },
  { value: "3months", label: "Last 3 months" },
  { value: "custom", label: "Custom range" },
];

function Dropdown({ options, value, onChange, isOpen, onToggle }) {
  const selected = options.find((o) => o.value === value);
  return (
    <div className="relative">
      <button
        type="button"
        onClick={onToggle}
        className={`flex min-h-[2.625rem] items-center gap-2 rounded-full px-4 py-2 text-sm transition-all ${
          isOpen ? "ring-2 ring-[var(--color-primary-bg)]" : ""
        }`}
        style={{
          backgroundColor: "var(--color-bg-elevated)",
          border: "1px solid var(--color-border)",
          color: "var(--color-text-secondary)",
        }}
      >
        <span>{selected?.label ?? "Select"}</span>
        <ChevronDown
          size={14}
          className={`transition-transform ${isOpen ? "rotate-180" : ""}`}
          style={{ color: "var(--color-text-muted)" }}
        />
      </button>
      {isOpen && (
        <div
          className="absolute top-full z-50 mt-2 min-w-[210px] overflow-hidden rounded-xl shadow-xl"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
          }}
        >
          {options.map((opt) => (
            <button
              key={String(opt.value)}
              type="button"
              onClick={() => onChange(opt.value)}
              className="w-full px-4 py-2.5 text-left text-sm transition-colors hover:opacity-90"
              style={{
                backgroundColor:
                  value === opt.value ? "var(--color-primary)" : "transparent",
                color:
                  value === opt.value
                    ? "#ffffff"
                    : "var(--color-text-secondary)",
              }}
            >
              {opt.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export function CalendarPicker({
  label,
  value,
  min,
  max,
  isOpen,
  onToggle,
  onChange,
}) {
  const selectedDate = parseIsoDateToLocal(value);
  const [visibleMonth, setVisibleMonth] = useState(selectedDate || new Date());
  const monthDays = buildMonthDays(visibleMonth);
  const todayValue = formatDate(new Date());
  const minDate = parseIsoDateToLocal(min);
  const maxDate = parseIsoDateToLocal(max);

  const moveMonth = (offset) => {
    setVisibleMonth(
      (prev) => new Date(prev.getFullYear(), prev.getMonth() + offset, 1),
    );
  };

  const isDisabled = (date) => {
    if (minDate && date < minDate) return true;
    if (maxDate && date > maxDate) return true;
    return false;
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={onToggle}
        className={`flex min-h-[2.625rem] items-center gap-2 rounded-full px-4 py-2 text-sm transition-all ${
          isOpen ? "ring-2 ring-[var(--color-primary-bg)]" : ""
        }`}
        style={{
          backgroundColor: "var(--color-bg-elevated)",
          border: "1px solid var(--color-border)",
          color: value ? "var(--color-text-primary)" : "var(--color-text-muted)",
        }}
        aria-label={label}
      >
        <Calendar size={15} style={{ color: "var(--color-primary)" }} />
        <span>{formatDisplayDate(value)}</span>
      </button>

      {isOpen && (
        <div
          className="absolute left-0 top-full z-50 mt-2 w-[20rem] max-w-[calc(100vw-3rem)] rounded-xl p-4 shadow-2xl"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            boxShadow: "var(--color-card-shadow)",
          }}
        >
          <div className="mb-4 flex items-center justify-between">
            <button
              type="button"
              onClick={() => moveMonth(-1)}
              className="rounded-lg p-2 transition hover:opacity-80"
              style={{ color: "var(--color-text-muted)" }}
              aria-label="Previous month"
            >
              <ChevronLeft size={18} />
            </button>
            <p
              className="text-sm font-bold"
              style={{ color: "var(--color-text-primary)" }}
            >
              {visibleMonth.toLocaleDateString("en-US", {
                month: "long",
                year: "numeric",
              })}
            </p>
            <button
              type="button"
              onClick={() => moveMonth(1)}
              className="rounded-lg p-2 transition hover:opacity-80"
              style={{ color: "var(--color-text-muted)" }}
              aria-label="Next month"
            >
              <ChevronRight size={18} />
            </button>
          </div>

          <div
            className="grid grid-cols-7 gap-1 text-center text-[0.6875rem] font-bold uppercase tracking-[0.08em]"
            style={{ color: "var(--color-text-muted)" }}
          >
            {WEEKDAYS.map((day) => (
              <span key={day} className="py-1">
                {day}
              </span>
            ))}
          </div>

          <div className="mt-2 grid grid-cols-7 gap-1">
            {monthDays.map((date, index) => {
              if (!date) return <span key={`blank-${index}`} />;
              const dateValue = formatDate(date);
              const selected = dateValue === value;
              const today = dateValue === todayValue;
              const disabled = isDisabled(date);
              return (
                <button
                  type="button"
                  key={dateValue}
                  disabled={disabled}
                  onClick={() => {
                    onChange(dateValue);
                    onToggle();
                  }}
                  className="aspect-square rounded-lg text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-30"
                  style={{
                    background: selected
                      ? "linear-gradient(135deg, #60a5fa 0%, var(--color-primary) 100%)"
                      : "transparent",
                    color: selected ? "#ffffff" : "var(--color-text-primary)",
                    boxShadow: selected
                      ? "0 10px 24px rgba(37,99,235,0.24)"
                      : "none",
                    outline:
                      today && !selected
                        ? "1px solid var(--color-primary)"
                        : "none",
                  }}
                >
                  {date.getDate()}
                </button>
              );
            })}
          </div>

          <div
            className="mt-4 flex items-center justify-between border-t pt-3"
            style={{ borderColor: "var(--color-border)" }}
          >
            <button
              type="button"
              onClick={() => {
                onChange("");
                onToggle();
              }}
              className="text-xs font-bold transition hover:opacity-80"
              style={{ color: "var(--color-text-muted)" }}
            >
              Clear date
            </button>
            <button
              type="button"
              onClick={onToggle}
              className="rounded-lg px-3 py-1.5 text-xs font-bold transition hover:opacity-90"
              style={{
                backgroundColor: "var(--color-bg-elevated)",
                color: "var(--color-text-primary)",
              }}
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function ApplyingStatus({ active }) {
  if (!active) return null;
  return (
    <div
      className="relative overflow-hidden rounded-xl px-4 py-3"
      style={{
        backgroundColor: "var(--color-primary-bg)",
        border: "1px solid var(--color-border)",
      }}
    >
      <div className="flex items-center gap-3">
        <span
          className="h-2.5 w-2.5 rounded-full"
          style={{
            backgroundColor: "var(--color-primary)",
            boxShadow: "0 0 18px var(--color-primary)",
          }}
        />
        <p
          className="text-sm font-semibold"
          style={{ color: "var(--color-text-primary)" }}
        >
          Applying filters...
        </p>
        <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
          Updating date and service context
        </p>
      </div>
      <div className="dashboard-filter-sweep absolute inset-y-0 left-0 w-1/3 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
    </div>
  );
}

export default function FilterBar({
  onApply,
  defaultPeriod = "all",
  anchorDate = isDemoMode ? "2025-10-31" : null,
  appliedFilters = null,
}) {
  const effectiveToday = parseIsoDateToLocal(anchorDate) ?? new Date();
  const today = formatDate(effectiveToday);
  const initialStart = formatDate(new Date(effectiveToday.getTime() - 7 * 864e5));

  const [period, setPeriod] = useState(defaultPeriod);
  const [serviceId, setServiceId] = useState(appliedFilters?.service_id ?? null);
  const [customStart, setCustomStart] = useState(
    appliedFilters?.start_date ?? initialStart,
  );
  const [customEnd, setCustomEnd] = useState(appliedFilters?.end_date ?? today);
  const [openPeriod, setOpenPeriod] = useState(false);
  const [openService, setOpenService] = useState(false);
  const [openCalendar, setOpenCalendar] = useState(null);
  const [isApplying, setIsApplying] = useState(false);
  const applyingTimerRef = useRef(null);

  useEffect(
    () => () => {
      if (applyingTimerRef.current) {
        window.clearTimeout(applyingTimerRef.current);
      }
    },
    [],
  );

  const { data: services = [] } = useQuery({
    queryKey: ["services", "all"],
    queryFn: async () => {
      const res = await api.get("/services");
      return res.data ?? [];
    },
  });

  const serviceOptions = [
    { value: null, label: "All services" },
    ...services.map((s) => ({ value: s.id, label: s.name })),
  ];

  const draftPayload = useMemo(() => {
    const { start, end } = computeDates(
      period,
      customStart,
      customEnd,
      anchorDate,
    );
    return {
      start_date: start,
      end_date: end,
      service_id: serviceId,
    };
  }, [anchorDate, customEnd, customStart, period, serviceId]);

  const normalizedApplied = {
    start_date: appliedFilters?.start_date ?? null,
    end_date: appliedFilters?.end_date ?? null,
    service_id: appliedFilters?.service_id ?? null,
  };

  const hasPendingChanges =
    draftPayload.start_date !== normalizedApplied.start_date ||
    draftPayload.end_date !== normalizedApplied.end_date ||
    draftPayload.service_id !== normalizedApplied.service_id;

  const activeFilterCount = [
    normalizedApplied.start_date,
    normalizedApplied.end_date,
    normalizedApplied.service_id,
  ].filter(Boolean).length;

  const startFeedback = () => {
    if (applyingTimerRef.current) {
      window.clearTimeout(applyingTimerRef.current);
    }
    setIsApplying(true);
    applyingTimerRef.current = window.setTimeout(() => {
      setIsApplying(false);
      applyingTimerRef.current = null;
    }, 900);
  };

  const closePopovers = () => {
    setOpenPeriod(false);
    setOpenService(false);
    setOpenCalendar(null);
  };

  const handleApply = () => {
    closePopovers();
    startFeedback();
    onApply(draftPayload);
  };

  const handleReset = () => {
    setPeriod(defaultPeriod);
    setServiceId(null);
    setCustomStart(initialStart);
    setCustomEnd(today);
    closePopovers();
    startFeedback();
    const { start, end } = computeDates(defaultPeriod, null, null, anchorDate);
    onApply({ start_date: start, end_date: end, service_id: null });
  };

  return (
    <div className="space-y-3">
      <div
        className="rounded-xl p-4"
        style={{
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          boxShadow: "var(--color-card-shadow)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div>
            <p
              className="text-sm font-semibold"
              style={{ color: "var(--color-text-primary)" }}
            >
              Filter analytics context
            </p>
            <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
              {activeFilterCount
                ? `${activeFilterCount} active filter${activeFilterCount > 1 ? "s" : ""}`
                : "No filters applied"}
            </p>
          </div>
          {hasPendingChanges && (
            <span
              className="rounded-full px-3 py-1 text-xs font-bold"
              style={{
                backgroundColor: "var(--color-primary-bg)",
                color: "var(--color-primary)",
              }}
            >
              Pending changes
            </span>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Dropdown
            options={PERIOD_OPTIONS}
            value={period}
            onChange={(v) => {
              setPeriod(v);
              setOpenPeriod(false);
            }}
            isOpen={openPeriod}
            onToggle={() => {
              setOpenPeriod((p) => !p);
              setOpenService(false);
              setOpenCalendar(null);
            }}
          />

          {period === "custom" && (
            <div className="flex flex-wrap items-center gap-2">
              <CalendarPicker
                label="Start date"
                value={customStart}
                max={customEnd || today}
                isOpen={openCalendar === "start"}
                onToggle={() => {
                  setOpenCalendar((prev) =>
                    prev === "start" ? null : "start",
                  );
                  setOpenPeriod(false);
                  setOpenService(false);
                }}
                onChange={setCustomStart}
              />
              <span
                className="hidden text-sm sm:inline"
                style={{ color: "var(--color-text-muted)" }}
              >
                to
              </span>
              <CalendarPicker
                label="End date"
                value={customEnd}
                min={customStart}
                max={today}
                isOpen={openCalendar === "end"}
                onToggle={() => {
                  setOpenCalendar((prev) => (prev === "end" ? null : "end"));
                  setOpenPeriod(false);
                  setOpenService(false);
                }}
                onChange={setCustomEnd}
              />
            </div>
          )}

          <Dropdown
            options={serviceOptions}
            value={serviceId}
            onChange={(v) => {
              setServiceId(v);
              setOpenService(false);
            }}
            isOpen={openService}
            onToggle={() => {
              setOpenService((p) => !p);
              setOpenPeriod(false);
              setOpenCalendar(null);
            }}
          />

          <button
            type="button"
            onClick={handleApply}
            disabled={isApplying || !hasPendingChanges}
            className="inline-flex min-h-[2.625rem] items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold text-white transition hover:brightness-110 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
            style={{ backgroundColor: "var(--color-primary)" }}
          >
            {isApplying ? (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            ) : (
              <Check size={16} />
            )}
            {isApplying ? "Applying..." : "Apply filters"}
          </button>

          <button
            type="button"
            onClick={handleReset}
            disabled={isApplying && !activeFilterCount}
            className="inline-flex min-h-[2.625rem] items-center gap-2 rounded-full px-3 py-2 text-sm transition hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-50"
            style={{ color: "var(--color-text-muted)" }}
          >
            <RotateCcw size={15} />
            Reset
          </button>
        </div>
      </div>

      <ApplyingStatus active={isApplying} />
    </div>
  );
}

const optionType = PropTypes.shape({
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  label: PropTypes.string.isRequired,
});

Dropdown.propTypes = {
  options: PropTypes.arrayOf(optionType).isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func.isRequired,
  isOpen: PropTypes.bool.isRequired,
  onToggle: PropTypes.func.isRequired,
};

CalendarPicker.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.string,
  min: PropTypes.string,
  max: PropTypes.string,
  isOpen: PropTypes.bool.isRequired,
  onToggle: PropTypes.func.isRequired,
  onChange: PropTypes.func.isRequired,
};

ApplyingStatus.propTypes = {
  active: PropTypes.bool.isRequired,
};

FilterBar.propTypes = {
  onApply: PropTypes.func.isRequired,
  anchorDate: PropTypes.string,
  defaultPeriod: PropTypes.oneOf([
    "all",
    "today",
    "7days",
    "30days",
    "3months",
    "custom",
  ]),
  appliedFilters: PropTypes.shape({
    start_date: PropTypes.string,
    end_date: PropTypes.string,
    service_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  }),
};
