import { useState } from "react";
import { ChevronLeft, ChevronRight, LogOut, Zap } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { navigationConfig } from "./navConfig";
import SidebarSection from "./SidebarSection";
import SidebarNavItem from "./SidebarNavItem";
import { ThemeToggleWithLabel } from "./ThemeToggle";

/**
 * Sidebar
 * Main navigation sidebar with collapsible state, admin-only sections,
 * and sticky header/footer with user info
 */
export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { full_name, logout, isAdmin } = useAuth();

  const getInitials = () => {
    if (!full_name) return "?";
    return full_name
      .split(" ")
      .map((part) => part[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleLabel = () => {
    return isAdmin() ? "System Admin" : "Analyst";
  };

  const sidebarWidth = isCollapsed ? "w-16" : "w-[220px]";

  return (
    <aside
      className={`${sidebarWidth} flex flex-col transition-all duration-200 ease-in-out h-screen overflow-hidden flex-shrink-0`}
      style={{
        backgroundColor: "var(--color-bg-card)",
        borderRight: "1px solid var(--color-border)",
      }}
    >
      {/* Header */}
      <div
        className="flex-shrink-0 p-4"
        style={{ borderBottom: "1px solid var(--color-border)" }}
      >
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            {!isCollapsed && (
              <div className="min-w-0">
                <h1
                  className="text-sm font-bold truncate"
                  style={{ color: "var(--color-text-primary)" }}
                >
                  InsightHub
                </h1>
                <p
                  className="text-xs truncate"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  SMS Services
                </p>
              </div>
            )}
          </div>
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center transition-all duration-200 ease-in-out"
            style={{
              backgroundColor: "var(--color-bg-elevated)",
              border: "1px solid var(--color-border)",
              color: "var(--color-text-muted)",
            }}
            aria-label="Toggle sidebar"
          >
            {isCollapsed ? (
              <ChevronRight size={16} />
            ) : (
              <ChevronLeft size={16} />
            )}
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto sidebar-nav">
        {navigationConfig.map((section) => {
          if (section.adminOnly && !isAdmin()) return null;

          return (
            <SidebarSection
              key={section.section}
              title={section.section}
              isCollapsed={isCollapsed}
            >
              {section.items.map((item) => (
                <SidebarNavItem
                  key={item.route}
                  icon={item.icon}
                  label={item.label}
                  route={item.route}
                  isCollapsed={isCollapsed}
                />
              ))}

              {!isCollapsed && section.section === "ADMIN" && (
                <div className="px-3 pt-2">
                  <ThemeToggleWithLabel />
                </div>
              )}
            </SidebarSection>
          );
        })}
      </nav>

      {/* Footer */}
      <div
        className="flex-shrink-0 p-4"
        style={{ borderTop: "1px solid var(--color-border)" }}
      >
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div
              className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold text-white"
              title={full_name || "User"}
            >
              {getInitials()}
            </div>
            {!isCollapsed && (
              <div className="min-w-0">
                <p className="text-sm font-medium text-slate-200 truncate">
                  {full_name}
                </p>
                <p
                  className="text-sm font-medium truncate"
                  style={{ color: "var(--color-text-secondary)" }}
                >
                  {full_name}
                </p>
                <p
                  className="text-xs truncate"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  {getRoleLabel()}
                </p>
              </div>
            )}
          </div>
          <button
            onClick={logout}
            className="flex-shrink-0 p-1 rounded transition-colors duration-200"
            style={{ color: "var(--color-text-muted)" }}
            aria-label="Logout"
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </aside>
  );
}
