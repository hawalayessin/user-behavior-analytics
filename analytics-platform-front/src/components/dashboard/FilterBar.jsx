import { useState } from "react";
import { ChevronDown } from "lucide-react";
import PropTypes from "prop-types";
import { useQuery } from "@tanstack/react-query";
import api from "../../services/api";

function formatDate(d) {
  return d.toISOString().split("T")[0];
}

function parseIsoDateToLocal(isoDate) {
  if (!isoDate) return null;
  const [y, m, d] = String(isoDate).split("-").map(Number);
  if (!y || !m || !d) return null;
  return new Date(y, m - 1, d, 12, 0, 0, 0);
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
        onClick={onToggle}
        className="flex items-center gap-2 px-4 py-2 rounded-full text-sm transition-all"
        style={{
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          color: "var(--color-text-secondary)",
        }}
      >
        <span>{selected?.label ?? "Select"}</span>
        <ChevronDown
          size={14}
          className={`text-slate-500 transition-transform ${isOpen ? "rotate-180" : ""}`}
        />
      </button>
      {isOpen && (
        <div
          className="absolute top-full mt-2 min-w-[200px] rounded-xl shadow-xl z-50 overflow-hidden"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
          }}
        >
          {options.map((opt) => (
            <button
              key={String(opt.value)}
              onClick={() => onChange(opt.value)}
              className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${
                value === opt.value ? "text-white" : "hover:opacity-90"
              }`}
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

// ── FilterBar ─────────────────────────────────────────────────────────────────
export default function FilterBar({
  onApply,
  defaultPeriod = "all",
  anchorDate = null,
}) {
  const effectiveToday = parseIsoDateToLocal(anchorDate) ?? new Date();
  const today = formatDate(effectiveToday);

  const [period, setPeriod] = useState(defaultPeriod);
  const [serviceId, setServiceId] = useState(null);
  const [customStart, setCustomStart] = useState(
    formatDate(new Date(effectiveToday.getTime() - 7 * 864e5)),
  );
  const [customEnd, setCustomEnd] = useState(today);
  const [openPeriod, setOpenPeriod] = useState(false);
  const [openService, setOpenService] = useState(false);
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

  const handleApply = () => {
    const { start, end } = computeDates(
      period,
      customStart,
      customEnd,
      anchorDate,
    );
    setOpenPeriod(false);
    setOpenService(false);
    onApply({ start_date: start, end_date: end, service_id: serviceId });
  };

  const handleReset = () => {
    setPeriod(defaultPeriod);
    setServiceId(null);
    setOpenPeriod(false);
    setOpenService(false);
    const { start, end } = computeDates(defaultPeriod, null, null, anchorDate);
    onApply({ start_date: start, end_date: end, service_id: null });
  };

  return (
    <div className="space-y-3">
      {/* ── Filtres ── */}
      <div
        className="flex flex-wrap items-center gap-3 p-4 rounded-xl"
        style={{
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          boxShadow: "var(--color-card-shadow)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Période */}
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
          }}
        />

        {/* Custom date range */}
        {period === "custom" && (
          <div className="flex items-center gap-2">
            <input
              type="date"
              value={customStart}
              max={customEnd}
              onChange={(e) => setCustomStart(e.target.value)}
              className="px-3 py-1.5 text-sm rounded-full focus:outline-none"
              style={{
                backgroundColor: "var(--color-bg-elevated)",
                border: "1px solid var(--color-border)",
                color: "var(--color-text-primary)",
              }}
            />
            <span className="text-slate-500 text-sm">→</span>
            <input
              type="date"
              value={customEnd}
              min={customStart}
              max={today}
              onChange={(e) => setCustomEnd(e.target.value)}
              className="px-3 py-1.5 text-sm rounded-full focus:outline-none"
              style={{
                backgroundColor: "var(--color-bg-elevated)",
                border: "1px solid var(--color-border)",
                color: "var(--color-text-primary)",
              }}
            />
          </div>
        )}

        {/* Service */}
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
          }}
        />

        {/* Apply */}
        <button
          onClick={handleApply}
          className="px-4 py-2 text-white text-sm font-semibold rounded-full transition"
          style={{ backgroundColor: "var(--color-primary)" }}
        >
          Apply filters
        </button>

        {/* Reset */}
        <button
          onClick={handleReset}
          className="px-3 py-2 text-sm transition"
          style={{ color: "var(--color-text-muted)" }}
        >
          Reset
        </button>
      </div>
    </div>
  );
}

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
};
