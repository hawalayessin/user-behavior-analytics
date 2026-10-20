import React from "react";
import PropTypes from "prop-types";
import { Pencil, Trash2 } from "lucide-react";

function truncate(text = "", max = 88) {
  if (text.length <= max) return text;
  return `${text.slice(0, max)}...`;
}

function initials(name = "AN") {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function formatDate(value) {
  if (!value) return "No date";
  return new Date(value).toLocaleDateString("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  });
}

function periodLabel(note) {
  if (!note.period_start && !note.period_end) return "Open";
  return `${note.period_start || "?"} - ${note.period_end || "?"}`;
}

export default function NotesList({
  notes,
  role,
  onEdit,
  onDelete,
  analystFilter,
  analystOptions,
  onAnalystFilter,
}) {
  return (
    <div className="overflow-hidden rounded-xl bg-[var(--notes-panel-glass)] shadow-[var(--notes-glow)] backdrop-blur-xl">
      <div className="flex flex-wrap items-center justify-between gap-4 px-6 py-5">
        <div>
          <h2 className="text-lg font-bold text-[var(--notes-text)]">
            Recent Analytical Entries
          </h2>
          <p className="mt-1 text-xs text-[var(--notes-muted)]">
            Showing {notes.length} contextual notes
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <span className="rounded-full border border-[var(--notes-success-border)] bg-[var(--notes-success-bg)] px-3 py-1 text-[0.6875rem] font-bold text-[var(--notes-success-text)]">
            {notes.length} Entries
          </span>
          {role === "admin" && (
            <label className="flex items-center gap-3">
              <span className="text-[0.6875rem] font-bold uppercase tracking-[0.14em] text-[var(--notes-subtle)]">
                Analyst
              </span>
              <select
                value={analystFilter}
                onChange={(e) => onAnalystFilter(e.target.value)}
                className="rounded-lg border-0 bg-[var(--notes-surface-highest)] px-3 py-2 text-sm text-[var(--notes-text)] outline-none ring-0 focus:ring-1 focus:ring-[var(--notes-primary)]"
              >
                <option value="">All</option>
                {analystOptions.map((analyst) => (
                  <option key={analyst.id} value={analyst.id}>
                    {analyst.name || "Unknown"}
                  </option>
                ))}
              </select>
            </label>
          )}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[880px] border-collapse text-left text-sm">
          <thead className="bg-[var(--notes-surface-lowest)] text-[0.6875rem] font-bold uppercase tracking-[0.14em] text-[var(--notes-subtle)]">
            <tr>
              <th className="px-6 py-4">Date & Analyst</th>
              <th className="px-6 py-4">Service & Metric</th>
              <th className="px-6 py-4">Content Preview</th>
              <th className="px-6 py-4">Period</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {notes.length === 0 ? (
              <tr>
                <td className="px-6 py-10 text-center text-[var(--notes-muted)]" colSpan={5}>
                  No notes yet.
                </td>
              </tr>
            ) : (
              notes.map((note, index) => (
                <tr
                  key={note.id}
                  className={`group transition-colors hover:bg-[var(--notes-row-hover)] ${
                    index % 2 === 1 ? "bg-[var(--notes-row-alt)]" : ""
                  }`}
                >
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--notes-surface-highest)] text-xs font-bold text-[var(--notes-primary)]">
                        {initials(note.analyst_name || "AN")}
                      </div>
                      <div>
                        <p className="font-bold leading-none text-[var(--notes-heading)]">
                          {note.analyst_name || "Analyst"}
                        </p>
                        <p className="mt-1 text-[0.6875rem] text-[var(--notes-muted)]">
                          {formatDate(note.created_at)}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <p className="font-medium text-[var(--notes-heading)]">
                      {!note.service_name && !note.metric
                        ? "Global"
                        : note.service_name || "No service"}
                    </p>
                    <p className="mt-1 text-[0.6875rem] text-[var(--notes-subtle)]">
                      {note.metric || "No metric"}
                    </p>
                  </td>
                  <td className="px-6 py-5">
                    <p className="max-w-md text-xs italic text-[var(--notes-soft)]">
                      "{truncate(note.content)}"
                    </p>
                  </td>
                  <td className="px-6 py-5">
                    <span className="inline-flex rounded bg-[var(--notes-surface-high)] px-2.5 py-1 text-[0.6875rem] font-bold text-[var(--notes-text)]">
                      {periodLabel(note)}
                    </span>
                  </td>
                  <td className="px-6 py-5 text-right">
                    <div className="flex justify-end gap-3 opacity-100 transition-opacity sm:opacity-0 sm:group-hover:opacity-100">
                      <button
                        type="button"
                        onClick={() => onEdit(note)}
                        className="rounded-lg p-2 text-[var(--notes-muted)] transition hover:bg-[var(--notes-surface-highest)] hover:text-[var(--notes-primary)]"
                        aria-label="Edit note"
                      >
                        <Pencil size={17} />
                      </button>
                      <button
                        type="button"
                        onClick={() => onDelete(note)}
                        className="rounded-lg p-2 text-[var(--notes-muted)] transition hover:bg-[var(--notes-surface-highest)] hover:text-[var(--notes-danger)]"
                        aria-label="Delete note"
                      >
                        <Trash2 size={17} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

NotesList.propTypes = {
  notes: PropTypes.arrayOf(PropTypes.object).isRequired,
  role: PropTypes.string.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  analystFilter: PropTypes.string.isRequired,
  analystOptions: PropTypes.arrayOf(
    PropTypes.shape({ id: PropTypes.string, name: PropTypes.string }),
  ).isRequired,
  onAnalystFilter: PropTypes.func.isRequired,
};
