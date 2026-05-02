import React from "react";
import PropTypes from "prop-types";
import { Pencil, Trash2 } from "lucide-react";

function truncate(text = "", max = 80) {
  if (text.length <= max) return text;
  return `${text.slice(0, max)}...`;
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
    <div className="space-y-4">
      {role === "admin" && (
        <div className="flex items-center gap-3">
          <label className="text-xs uppercase tracking-wide text-slate-400">
            Filter by analyst
          </label>
          <select
            value={analystFilter}
            onChange={(e) => onAnalystFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
          >
            <option value="">All</option>
            {analystOptions.map((analyst) => (
              <option key={analyst.id} value={analyst.id}>
                {analyst.name || "Unknown"}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-800/50 border-b border-slate-800">
            <tr className="text-xs text-slate-400 uppercase tracking-wide">
              <th className="px-4 py-3 text-left">Date</th>
              {role === "admin" && (
                <th className="px-4 py-3 text-left">Analyst</th>
              )}
              <th className="px-4 py-3 text-left">Service</th>
              <th className="px-4 py-3 text-left">Metric</th>
              <th className="px-4 py-3 text-left">Period</th>
              <th className="px-4 py-3 text-left">Content</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {notes.length === 0 ? (
              <tr>
                <td
                  colSpan={role === "admin" ? 7 : 6}
                  className="px-4 py-6 text-center text-slate-500"
                >
                  No notes yet.
                </td>
              </tr>
            ) : (
              notes.map((note) => (
                <tr
                  key={note.id}
                  className="border-b border-slate-800 hover:bg-slate-800/40"
                >
                  <td className="px-4 py-3 text-slate-200">
                    {note.created_at
                      ? new Date(note.created_at).toLocaleDateString("en-US")
                      : "—"}
                  </td>
                  {role === "admin" && (
                    <td className="px-4 py-3 text-slate-300">
                      {note.analyst_name || "—"}
                    </td>
                  )}
                  <td className="px-4 py-3 text-slate-300">
                    {!note.service_name && !note.metric ? "Global" : note.service_name || "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-300">
                    {note.metric || "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-300">
                    {note.period_start || note.period_end
                      ? `${note.period_start || "?"} → ${note.period_end || "?"}`
                      : "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-400 max-w-md">
                    {truncate(note.content)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => onEdit(note)}
                        className="p-1.5 text-slate-400 hover:text-indigo-400"
                      >
                        <Pencil size={16} />
                      </button>
                      <button
                        onClick={() => onDelete(note)}
                        className="p-1.5 text-slate-400 hover:text-red-400"
                      >
                        <Trash2 size={16} />
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
