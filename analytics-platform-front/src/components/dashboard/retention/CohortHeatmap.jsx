import PropTypes from "prop-types";

function getCellClasses(value) {
  if (value >= 50) return "bg-emerald-500/30 text-emerald-300";
  if (value >= 30) return "bg-yellow-500/30 text-yellow-300";
  if (value > 0) return "bg-red-500/30 text-red-300";
  return "";
}

export default function CohortHeatmap({ data }) {
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

  const rows = data;

  return (
    <div
      className="rounded-xl p-6 h-full flex flex-col"
      style={{
        backgroundColor: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
        boxShadow: "var(--color-card-shadow)",
      }}
    >
      <h3
        className="text-sm font-semibold mb-4"
        style={{ color: "var(--color-text-primary)" }}
      >
        Cohort Retention Heatmap
      </h3>
      <div className="overflow-auto">
        <table className="w-full text-xs text-center border-collapse">
          <thead>
            <tr>
              <th
                className="px-3 py-2 text-left"
                style={{ color: "var(--color-text-muted)" }}
              >
                Cohort
              </th>
              <th
                className="px-3 py-2 text-left"
                style={{ color: "var(--color-text-muted)" }}
              >
                Service
              </th>
              <th
                className="px-2 py-2"
                style={{ color: "var(--color-text-muted)" }}
              >
                D7
              </th>
              <th
                className="px-2 py-2"
                style={{ color: "var(--color-text-muted)" }}
              >
                D14
              </th>
              <th
                className="px-2 py-2"
                style={{ color: "var(--color-text-muted)" }}
              >
                D30
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr
                key={`${row.cohort}-${row.service}-${idx}`}
                style={{ borderTop: "1px solid var(--color-border-subtle)" }}
              >
                <td
                  className="px-3 py-2 text-left whitespace-nowrap"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  {row.cohort}
                </td>
                <td
                  className="px-3 py-2 text-left whitespace-nowrap"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  {row.service}
                </td>
                {["d7", "d14", "d30"].map((k) => (
                  <td key={k} className="px-1 py-1">
                    <div
                      className={`relative group rounded-md px-2 py-1 text-[11px] font-medium ${getCellClasses(row[k])}`}
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
