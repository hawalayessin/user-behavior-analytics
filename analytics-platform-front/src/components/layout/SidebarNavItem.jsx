import { NavLink } from "react-router-dom";

/**
 * SidebarNavItem
 * @param {Object} props
 * @param {React.ElementType} props.icon - lucide-react icon component
 * @param {string} props.label - item label text
 * @param {string} props.route - target route path
 * @param {boolean} props.isCollapsed - sidebar collapse state
 */
export default function SidebarNavItem({
  icon: IconComponent,
  label,
  route,
  isCollapsed,
  badgeCount = 0,
}) {
  const tooltipVisibleClass = isCollapsed ? "group-hover:visible" : "invisible";
  const showBadge = Number(badgeCount || 0) > 0;

  return (
    <NavLink
      to={route}
      className={({ isActive }) =>
        `group relative flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 border-l-2 ${
          isActive ? "text-slate-100" : "border-transparent"
        }`
      }
      style={({ isActive }) => ({
        backgroundColor: isActive ? "var(--color-primary-bg)" : "transparent",
        color: isActive ? "var(--color-primary)" : "var(--color-text-muted)",
        borderLeftColor: isActive ? "var(--color-primary)" : "transparent",
      })}
    >
      {({ isActive }) => (
        <>
          <IconComponent
            className={`w-5 h-5 flex-shrink-0 transition-colors duration-200 ${
              isActive ? "" : ""
            }`}
            style={{
              color: isActive
                ? "var(--color-primary)"
                : "var(--color-text-muted)",
            }}
          />
          {!isCollapsed && (
            <span className="text-sm font-medium truncate">{label}</span>
          )}

          {!isCollapsed && showBadge && (
            <span className="ml-auto inline-flex items-center justify-center min-w-5 h-5 px-1 rounded-full bg-red-500/20 border border-red-500/40 text-red-300 text-[10px] font-bold">
              {Number(badgeCount) > 99 ? "99+" : Number(badgeCount)}
            </span>
          )}

          {isCollapsed && showBadge && (
            <span className="absolute top-2 right-2 w-2.5 h-2.5 rounded-full bg-red-400 border border-slate-900" />
          )}

          {isCollapsed && (
            <div
              className={`absolute left-full ml-2 px-3 py-1.5 bg-slate-800 text-slate-200 text-xs whitespace-nowrap rounded shadow-lg pointer-events-none ${tooltipVisibleClass} transition-visibility duration-200`}
              style={{
                backgroundColor: "var(--color-bg-card)",
                color: "var(--color-text-secondary)",
                border: "1px solid var(--color-border)",
              }}
            >
              {label}
              {showBadge ? ` (${Number(badgeCount)})` : ""}
            </div>
          )}
        </>
      )}
    </NavLink>
  );
}
