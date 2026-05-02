import { useEffect, useMemo, useState } from "react";
import PropTypes from "prop-types";

const ROWS_PER_PAGE = 10;

function getCellClasses(value) {
  if (value >= 50) return "bg-emerald-500/30 text-emerald-300";
  if (value >= 30) return "bg-yellow-500/30 text-yellow-300";
  if (value > 0) return "bg-red-500/30 text-red-300";
  return "";
}

export default function CohortHeatmap({ data }) {
  const [page, setPage] = useState(1);

  if (!data?.length) {
    return (
      <div
        className="rounded-xl p-6 h-full flex items-center justify-center text-sm"
        style={{
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          color: "var(--color-text-muted)",
          boxShadow: "var(--color-card-shadow)",
        }}
      >
        No cohort data available
      </div>
    );
  }

  const rows = useMemo(() => data, [data]);
  const totalPages = Math.max(1, Math.ceil(rows.length / ROWS_PER_PAGE));
  const currentPage = Math.min(page, totalPages);

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  const pageRows = useMemo(() => {
    const start = (currentPage - 1) * ROWS_PER_PAGE;
    return rows.slice(start, start + ROWS_PER_PAGE);
  }, [currentPage, rows]);

  return (
    <div
      className="rounded-xl p-4 h-full flex flex-col"
      style={{
        backgroundColor: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
        boxShadow: "var(--color-card-shadow)",
      }}
    >
      <h3
        className="text-sm font-semibold mb-3"
        style={{ color: "var(--color-text-primary)" }}
      >
        Cohort Retention Heatmap
      </h3>
      <div className="overflow-auto max-h-[420px]">
        <table className="w-full text-[11px] text-center border-collapse">
          <thead>
            <tr>
              <th
                className="px-2.5 py-1.5 text-left"
                style={{ color: "var(--color-text-muted)" }}
              >
                Cohort
              </th>
              <th
                className="px-2.5 py-1.5 text-left"
                style={{ color: "var(--color-text-muted)" }}
              >
                Service
              </th>
              <th
                className="px-1.5 py-1.5"
                style={{ color: "var(--color-text-muted)" }}
              >
                D7
              </th>
              <th
                className="px-1.5 py-1.5"
                style={{ color: "var(--color-text-muted)" }}
              >
                D14
              </th>
              <th
                className="px-1.5 py-1.5"
                style={{ color: "var(--color-text-muted)" }}
              >
                D30
              </th>
            </tr>
          </thead>
          <tbody>
            {pageRows.map((row, idx) => (
              <tr
                key={`${row.cohort}-${row.service}-${idx}`}
                style={{ borderTop: "1px solid var(--color-border-subtle)" }}
              >
                <td
                  className="px-2.5 py-1.5 text-left whitespace-nowrap"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  {row.cohort}
                </td>
                <td
                  className="px-2.5 py-1.5 text-left whitespace-nowrap"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  {row.service}
                </td>
                {["d7", "d14", "d30"].map((k) => (
                  <td key={k} className="px-1 py-0.5">
                    <div
                      className={`relative group rounded px-1.5 py-1 text-[10px] font-medium ${getCellClasses(row[k])}`}
                      style={
                        row[k] > 0
                          ? undefined
                          : {
                              backgroundColor: "var(--color-bg-elevated)",
                              color: "var(--color-text-muted)",
                            }
                      }
                    >
                      <span>{row[k].toFixed(1)}%</span>
                      <div className="pointer-events-none absolute -top-1 left-1/2 -translate-x-1/2 -translate-y-full opacity-0 group-hover:opacity-100 transition-opacity">
                        <div
                          className="px-2 py-1 text-[10px] rounded shadow-lg whitespace-nowrap"
                          style={{
                            backgroundColor: "var(--chart-tooltip-bg)",
                            border: "1px solid var(--chart-tooltip-border)",
                            color: "var(--color-text-secondary)",
                          }}
                        >
                          {row.service} — {row.cohort} · {k.toUpperCase()}{" "}
                          {row[k].toFixed(1)}% · {row.total_users} users
                        </div>
                      </div>
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div
        className="mt-3 flex items-center justify-between text-xs"
        style={{ color: "var(--color-text-muted)" }}
      >
        <span>
          Showing {(currentPage - 1) * ROWS_PER_PAGE + 1}-
          {Math.min(currentPage * ROWS_PER_PAGE, rows.length)} of {rows.length}
        </span>
        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={currentPage <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            className="px-2 py-1 rounded border disabled:opacity-40"
            style={{
              borderColor: "var(--color-border)",
              color: "var(--color-text-secondary)",
            }}
          >
            Prev
          </button>
          <span>
            Page {currentPage}/{totalPages}
          </span>
          <button
            type="button"
            disabled={currentPage >= totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            className="px-2 py-1 rounded border disabled:opacity-40"
            style={{
              borderColor: "var(--color-border)",
              color: "var(--color-text-secondary)",
            }}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

CohortHeatmap.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      cohort: PropTypes.string.isRequired,
      service: PropTypes.string.isRequired,
      total_users: PropTypes.number.isRequired,
      d7: PropTypes.number.isRequired,
      d14: PropTypes.number.isRequired,
      d30: PropTypes.number.isRequired,
    }),
  ),
};
