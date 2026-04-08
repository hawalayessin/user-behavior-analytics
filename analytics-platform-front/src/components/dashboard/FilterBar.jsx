import { useState } from "react";
import { ChevronDown } from "lucide-react";
import PropTypes from "prop-types";
import { useQuery } from "@tanstack/react-query";
import api from "../../services/api";

function formatDate(d) {
  return d.toISOString().split("T")[0];
}

function computeDates(period, customStart, customEnd) {
  const today = new Date();
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
        className="flex items-center gap-2 px-4 py-2 bg-[#1A1D27] border border-slate-700 rounded-full text-sm text-slate-300 hover:bg-slate-800 transition-all"
      >
        <span>{selected?.label ?? "Select"}</span>
        <ChevronDown
          size={14}
          className={`text-slate-500 transition-transform ${isOpen ? "rotate-180" : ""}`}
        />
      </button>
      {isOpen && (
        <div className="absolute top-full mt-2 min-w-[200px] bg-[#1A1D27] border border-slate-700 rounded-xl shadow-xl z-50 overflow-hidden">
          {options.map((opt) => (
            <button
              key={String(opt.value)}
              onClick={() => onChange(opt.value)}
              className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${
                value === opt.value
                  ? "bg-violet-700 text-white"
                  : "text-slate-300 hover:bg-slate-800"
              }`}
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
export default function FilterBar({ onApply, defaultPeriod = "all" }) {
  const today = formatDate(new Date());

  const [period, setPeriod] = useState(defaultPeriod);
  const [serviceId, setServiceId] = useState(null);
  const [customStart, setCustomStart] = useState(
    formatDate(new Date(Date.now() - 7 * 864e5)),
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
    const { start, end } = computeDates(period, customStart, customEnd);
    setOpenPeriod(false);
    setOpenService(false);
    onApply({ start_date: start, end_date: end, service_id: serviceId });
  };

  const handleReset = () => {
    setPeriod(defaultPeriod);
    setServiceId(null);
    setOpenPeriod(false);
    setOpenService(false);
    const { start, end } = computeDates(defaultPeriod, null, null);
    onApply({ start_date: start, end_date: end, service_id: null });
  };

  return (
    <div className="space-y-3">
      {/* ── Filtres ── */}
      <div
        className="flex flex-wrap items-center gap-3 p-4 bg-[#1A1D27] border border-slate-800 rounded-xl"
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
              className="px-3 py-1.5 text-sm bg-[#0F1117] border border-slate-700 rounded-full text-slate-300 focus:outline-none focus:border-violet-500"
            />
            <span className="text-slate-500 text-sm">→</span>
            <input
              type="date"
              value={customEnd}
              min={customStart}
              max={today}
              onChange={(e) => setCustomEnd(e.target.value)}
              className="px-3 py-1.5 text-sm bg-[#0F1117] border border-slate-700 rounded-full text-slate-300 focus:outline-none focus:border-violet-500"
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
          className="px-4 py-2 bg-violet-700 hover:bg-violet-800 text-white text-sm font-semibold rounded-full transition"
        >
          Apply filters
        </button>

        {/* Reset */}
        <button
          onClick={handleReset}
          className="px-3 py-2 text-sm text-slate-500 hover:text-slate-300 transition"
        >
          Reset
        </button>
      </div>
    </div>
  );
}

FilterBar.propTypes = {
  onApply: PropTypes.func.isRequired,
  defaultPeriod: PropTypes.oneOf([
    "all",
    "today",
    "7days",
    "30days",
    "3months",
    "custom",
  ]),
};
