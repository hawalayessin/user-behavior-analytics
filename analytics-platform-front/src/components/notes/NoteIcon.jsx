import React from "react";
import PropTypes from "prop-types";

export default function NoteIcon({ notes, date }) {
  const match = notes.find((note) => note.period_start === date);
  if (!match) return null;

  return (
    <div className="relative group inline-flex items-center">
      <span className="text-xs px-1.5 py-0.5 rounded-full bg-indigo-600/20 text-indigo-300">
        💬
      </span>
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-64 z-20">
        <div className="rounded-lg border border-slate-700 bg-slate-900 text-slate-200 text-xs p-2 shadow-xl">
          {match.content}
        </div>
      </div>
    </div>
  );
}

NoteIcon.propTypes = {
  notes: PropTypes.arrayOf(PropTypes.object).isRequired,
  date: PropTypes.string.isRequired,
};
