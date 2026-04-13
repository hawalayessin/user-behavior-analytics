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
    <div className="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-8">
      {/* Left: Breadcrumb */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <Home className="w-4 h-4 text-slate-400" />
        <ChevronRight className="w-3 h-3 text-slate-600" />
        <span className="text-sm font-medium text-slate-300">{pageTitle}</span>
      </div>

      {/* Center: Search */}
      <div className="flex-1 max-w-xs mx-8">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search analytics..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-colors duration-200"
          />
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-4 flex-shrink-0">
        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-300 transition-colors duration-200"
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5" />
            {hasNotifications && (
              <div className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50 overflow-hidden">
              <div className="px-4 py-3 border-b border-slate-700">
                <h3 className="text-sm font-semibold text-slate-200">
                  Notifications
                </h3>
              </div>
              <div className="max-h-64 overflow-y-auto scrollbar-modern">
                {notifications.length === 0 ? (
                  <div className="px-4 py-6 text-sm text-slate-400 text-center">
                    No notifications.
                  </div>
                ) : (
                  notifications.map((notif) => (
                    <div
                      key={notif.id}
                      className="px-4 py-3 border-b border-slate-700 hover:bg-slate-700/50 transition-colors duration-200 cursor-pointer"
                    >
                      <p className="text-sm text-slate-200">{notif.title}</p>
                      <p className="text-xs text-slate-500 mt-1">
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
        <div className="w-px h-6 bg-slate-700" />

        {/* User Info */}
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold text-white"
            title={full_name || "User"}
          >
            {getInitials()}
          </div>
          <div className="text-sm font-medium text-slate-200">{full_name}</div>
          <span
            className={`text-xs font-medium px-2 py-1 rounded ${getRoleBadgeStyle()}`}
          >
            {getRoleLabel()}
          </span>
        </div>

        {/* Export Button (conditional) */}
        {showExportButton && (
          <button className="flex items-center gap-2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg transition-colors duration-200">
            <Download className="w-4 h-4" />
            Export
          </button>
        )}

        {/* Logout */}
        <button
          onClick={logout}
          className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-300 transition-colors duration-200"
          aria-label="Logout"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
