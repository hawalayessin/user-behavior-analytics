import PropTypes from "prop-types";
import { Activity } from "lucide-react";

export default function PeakEvidenceCard({
  title,
  value,
  subtitle,
  icon: Icon = Activity,
  accent = "cyan",
}) {
  const tones = {
    cyan: "bg-cyan-500/10 text-cyan-300 border-cyan-500/25",
    emerald: "bg-emerald-500/10 text-emerald-300 border-emerald-500/25",
    amber: "bg-amber-500/10 text-amber-300 border-amber-500/25",
    rose: "bg-rose-500/10 text-rose-300 border-rose-500/25",
    violet: "bg-violet-500/10 text-violet-300 border-violet-500/25",
    slate: "bg-slate-700/40 text-slate-300 border-slate-600/50",
  };
  const tone = tones[accent] ?? tones.cyan;

  return (
    <div className={`rounded-xl border p-4 ${tone}`}>
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-black/15">
          <Icon size={18} />
        </div>
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide opacity-80">
            {title}
          </p>
          <p className="mt-1 truncate text-2xl font-bold text-slate-100">
            {value}
          </p>
          {subtitle && (
            <p className="mt-1 text-xs leading-5 text-slate-400">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  );
}

PeakEvidenceCard.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  subtitle: PropTypes.string,
  icon: PropTypes.elementType,
  accent: PropTypes.oneOf(["cyan", "emerald", "amber", "rose", "violet", "slate"]),
};
