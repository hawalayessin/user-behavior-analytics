import { useState } from "react";
import {
  Home,
  ChevronRight,
  Search,
  Bell,
  Download,
  LogOut,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { ThemeToggle } from "./ThemeToggle";

/**
 * Topbar
 * Top navigation bar with breadcrumb, search, and action buttons
 * @param {Object} props
 * @param {string} props.pageTitle - Current page title for breadcrumb
 * @param {boolean} props.hasNotifications - Show red badge on bell icon
 * @param {boolean} props.showExportButton - Display export button
 */
export default function Topbar({
  pageTitle,
  hasNotifications = false,
  showExportButton = false,
}) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const { full_name, role, logout } = useAuth();
  const notifications = [];

  const getInitials = () => {
    if (!full_name) return "?";
    return full_name
      .split(" ")
      .map((part) => part[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleBadgeStyle = () => {
    return role === "admin"
      ? "bg-indigo-500/20 text-indigo-400"
      : "bg-slate-700 text-slate-400";
  };

  const getRoleLabel = () => {
    return role === "admin" ? "Admin" : "Analyst";
  };

  return (
    <div
      className="h-16 flex items-center justify-between px-8"
      style={{
        backgroundColor: "var(--color-topbar-blur)",
        backdropFilter: "blur(12px)",
        borderBottom: "1px solid var(--color-border)",
      }}
    >
      {/* Left: Breadcrumb */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <Home
          className="w-4 h-4"
          style={{ color: "var(--color-text-muted)" }}
        />
        <ChevronRight
          className="w-3 h-3"
          style={{ color: "var(--color-text-disabled)" }}
        />
        <span
          className="text-sm font-medium"
          style={{ color: "var(--color-text-secondary)" }}
        >
          {pageTitle}
        </span>
      </div>

      {/* Center: Search */}
      <div className="flex-1 max-w-xs mx-8">
        <div className="relative">
          <Search
            className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4"
            style={{ color: "var(--color-text-muted)" }}
          />
          <input
            type="text"
            placeholder="Search analytics..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 transition-colors duration-200"
            style={{
              backgroundColor: "var(--color-bg-elevated)",
              border: "1px solid var(--color-border)",
              color: "var(--color-text-primary)",
            }}
          />
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-4 flex-shrink-0">
        <ThemeToggle />

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-lg transition-colors duration-200"
            style={{ color: "var(--color-text-muted)" }}
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5" />
            {hasNotifications && (
              <div className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            )}
          </button>

          {showNotifications && (
            <div
              className="absolute right-0 mt-2 w-80 rounded-lg shadow-xl z-50 overflow-hidden"
              style={{
                backgroundColor: "var(--color-bg-card)",
                border: "1px solid var(--color-border)",
              }}
            >
              <div
                className="px-4 py-3"
                style={{ borderBottom: "1px solid var(--color-border)" }}
              >
                <h3
                  className="text-sm font-semibold"
                  style={{ color: "var(--color-text-primary)" }}
                >
                  Notifications
                </h3>
              </div>
              <div className="max-h-64 overflow-y-auto scrollbar-modern">
                {notifications.length === 0 ? (
                  <div
                    className="px-4 py-6 text-sm text-center"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    No notifications.
                  </div>
                ) : (
                  notifications.map((notif) => (
                    <div
                      key={notif.id}
                      className="px-4 py-3 transition-colors duration-200 cursor-pointer"
                      style={{ borderBottom: "1px solid var(--color-border)" }}
                    >
                      <p
                        className="text-sm"
                        style={{ color: "var(--color-text-secondary)" }}
                      >
                        {notif.title}
                      </p>
                      <p
                        className="text-xs mt-1"
                        style={{ color: "var(--color-text-muted)" }}
                      >
                        {notif.time}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Divider */}
        <div
          className="w-px h-6"
          style={{ backgroundColor: "var(--color-border)" }}
        />

        {/* User Info */}
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold text-white"
            title={full_name || "User"}
          >
            {getInitials()}
          </div>
          <div
            className="text-sm font-medium"
            style={{ color: "var(--color-text-secondary)" }}
          >
            {full_name}
          </div>
          <span
            className={`text-xs font-medium px-2 py-1 rounded ${getRoleBadgeStyle()}`}
          >
            {getRoleLabel()}
          </span>
        </div>

        {/* Export Button (conditional) */}
        {showExportButton && (
          <button
            className="flex items-center gap-2 px-3 py-1.5 text-white text-xs font-semibold rounded-lg transition-colors duration-200"
            style={{ backgroundColor: "var(--color-primary)" }}
          >
            <Download className="w-4 h-4" />
            Export
          </button>
        )}

        {/* Logout */}
        <button
          onClick={logout}
          className="p-2 rounded-lg transition-colors duration-200"
          style={{ color: "var(--color-text-muted)" }}
          aria-label="Logout"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
