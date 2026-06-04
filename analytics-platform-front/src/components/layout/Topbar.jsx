import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ChevronDown,
  ChevronRight,
  Home,
  LogOut,
  Search,
  UserCog,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { ThemeToggle } from "./ThemeToggle";
import { navigationConfig } from "./navConfig";
import AnomalyNotifications from "./AnomalyNotifications";

const KPI_SEARCH_INDEX = [
  {
    kpi: "DAU",
    aliases: ["daily active users"],
    route: "/analytics/behaviors",
  },
  {
    kpi: "WAU",
    aliases: ["weekly active users"],
    route: "/analytics/behaviors",
  },
  {
    kpi: "MAU",
    aliases: ["monthly active users"],
    route: "/analytics/behaviors",
  },
  {
    kpi: "ARPU",
    aliases: ["average revenue per user"],
    route: "/analytics/cross-service",
  },
  {
    kpi: "MRR",
    aliases: ["monthly recurring revenue", "monthly revenue"],
    route: "/dashboard",
  },
  {
    kpi: "Churn Rate",
    aliases: ["churn", "monthly churn", "voluntary churn"],
    route: "/analytics/churn",
  },
  {
    kpi: "Retention D7",
    aliases: ["d7 retention", "week retention"],
    route: "/analytics/retention",
  },
  {
    kpi: "Retention D30",
    aliases: ["d30 retention", "month retention"],
    route: "/analytics/retention",
  },
  {
    kpi: "Trial Conversion",
    aliases: ["trial to paid", "conversion rate"],
    route: "/analytics/trial",
  },
  {
    kpi: "New Subscribers",
    aliases: ["subscriber growth"],
    route: "/analytics/campaigns",
  },
  {
    kpi: "Anomalies",
    aliases: ["anomaly score", "anomaly detection"],
    route: "/analytics/anomalies",
  },
  {
    kpi: "Churn Prediction",
    aliases: ["risk score", "predicted churn"],
    route: "/analytics/churn-prediction",
  },
  {
    kpi: "Segmentation ARPU",
    aliases: ["segment arpu", "premium arpu"],
    route: "/analytics/segmentation",
  },
  {
    kpi: "Subscribers ARPU",
    aliases: ["directory arpu"],
    route: "/management/subscribers",
  },
];

export default function Topbar({ pageTitle }) {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const { full_name, role, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const menuRef = useRef(null);
  const searchRef = useRef(null);

  const searchableRoutes = useMemo(() => {
    const navItems = navigationConfig
      .filter((section) => !section.adminOnly || isAdmin())
      .flatMap((section) =>
        section.items.map((item) => ({
          type: "page",
          section: section.section,
          label: item.label.trim(),
          route: item.route,
          searchText:
            `${item.label} ${section.section} ${item.route}`.toLowerCase(),
        })),
      );

    const accessibleRoutes = new Set(navItems.map((item) => item.route));
    const kpiItems = KPI_SEARCH_INDEX.filter((item) =>
      accessibleRoutes.has(item.route),
    ).map((item) => ({
      type: "kpi",
      section: "KPI",
      label: item.kpi,
      route: item.route,
      searchText:
        `${item.kpi} ${item.aliases.join(" ")} ${item.route}`.toLowerCase(),
    }));

    return [...navItems, ...kpiItems];
  }, [isAdmin]);

  const filteredRoutes = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return [];
    return searchableRoutes
      .filter((item) => item.searchText.includes(q))
      .slice(0, 6);
  }, [searchQuery, searchableRoutes]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSearchResults(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const navigateFromSearch = (targetRoute) => {
    navigate(targetRoute);
    setSearchQuery("");
    setShowSearchResults(false);
  };

  const handleSearchKeyDown = (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      if (filteredRoutes.length > 0) {
        navigateFromSearch(filteredRoutes[0].route);
      }
      return;
    }
    if (event.key === "Escape") {
      setShowSearchResults(false);
    }
  };

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

      <div className="flex-1 max-w-xs mx-8" ref={searchRef}>
        <div className="relative">
          <Search
            className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4"
            style={{ color: "var(--color-text-muted)" }}
          />
          <input
            type="text"
            placeholder="Search analytics..."
            value={searchQuery}
            onFocus={() => setShowSearchResults(true)}
            onKeyDown={handleSearchKeyDown}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setShowSearchResults(true);
            }}
            className="w-full pl-10 pr-4 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 transition-colors duration-200"
            style={{
              backgroundColor: "var(--color-bg-elevated)",
              border: "1px solid var(--color-border)",
              color: "var(--color-text-primary)",
            }}
          />

          {showSearchResults && searchQuery.trim() && (
            <div
              className="absolute left-0 right-0 mt-2 rounded-lg shadow-xl z-50 overflow-hidden"
              style={{
                backgroundColor: "var(--color-bg-card)",
                border: "1px solid var(--color-border)",
              }}
            >
              {filteredRoutes.length > 0 ? (
                filteredRoutes.map((item, index) => (
                  <button
                    key={`${item.type}-${item.route}-${item.label}-${index}`}
                    onClick={() => navigateFromSearch(item.route)}
                    className="w-full px-3 py-2 text-left hover:bg-slate-800/60 transition"
                  >
                    <div
                      className="text-sm font-medium"
                      style={{ color: "var(--color-text-primary)" }}
                    >
                      {item.label}
                    </div>
                    <div
                      className="text-xs mt-0.5"
                      style={{ color: "var(--color-text-muted)" }}
                    >
                      {item.section} � {item.route}
                    </div>
                  </button>
                ))
              ) : (
                <div
                  className="px-3 py-2 text-sm"
                  style={{ color: "var(--color-text-muted)" }}
                >
                  No matching page
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4 flex-shrink-0">
        <ThemeToggle />

        <AnomalyNotifications />

        <div
          className="w-px h-6"
          style={{ backgroundColor: "var(--color-border)" }}
        />

        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setShowUserMenu((prev) => !prev)}
            className="group flex items-center gap-3 rounded-xl px-2.5 py-1.5 transition"
            style={{
              color: "var(--color-text-secondary)",
              backgroundColor: showUserMenu
                ? "var(--color-bg-elevated)"
                : "transparent",
              boxShadow: showUserMenu
                ? "inset 0 0 0 1px var(--color-border)"
                : "none",
            }}
            aria-label="Open user menu"
            aria-expanded={showUserMenu}
          >
            <div
              className="w-9 h-9 rounded-full bg-indigo-600 flex items-center justify-center text-sm font-extrabold text-white shadow-lg shadow-indigo-950/20"
              title={full_name || "User"}
            >
              {getInitials()}
            </div>
            <div className="hidden min-w-0 text-left md:block">
              <div
                className="max-w-40 truncate text-sm font-bold"
                style={{ color: "var(--color-text-primary)" }}
              >
                {full_name}
              </div>
            </div>
            <span
              className={`hidden text-xs font-bold px-2.5 py-1 rounded-lg md:inline-flex ${getRoleBadgeStyle()}`}
            >
              {getRoleLabel()}
            </span>
            <ChevronDown
              size={15}
              className="transition-transform"
              style={{
                color: "var(--color-text-muted)",
                transform: showUserMenu ? "rotate(180deg)" : "rotate(0deg)",
              }}
            />
          </button>

          {showUserMenu && (
            <div
              className="absolute right-0 mt-3 w-72 rounded-xl shadow-2xl z-50 overflow-hidden"
              style={{
                backgroundColor: "var(--color-bg-card)",
                border: "1px solid var(--color-border)",
                boxShadow:
                  "0 20px 50px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.04)",
              }}
            >
              <div
                className="absolute -top-1 right-8 h-3 w-3 rotate-45"
                style={{
                  backgroundColor: "var(--color-bg-card)",
                  borderLeft: "1px solid var(--color-border)",
                  borderTop: "1px solid var(--color-border)",
                }}
              />
              <div
                className="px-4 py-4"
                style={{
                  background:
                    "linear-gradient(135deg, rgba(59,130,246,0.10), transparent 62%)",
                  borderBottom: "1px solid var(--color-border-subtle)",
                }}
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-full bg-indigo-600 text-sm font-extrabold text-white">
                    {getInitials()}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p
                      className="truncate text-sm font-extrabold"
                      style={{ color: "var(--color-text-primary)" }}
                    >
                      {full_name}
                    </p>
                    <span
                      className={`mt-1 inline-flex text-xs font-bold px-2.5 py-1 rounded-lg ${getRoleBadgeStyle()}`}
                    >
                      {getRoleLabel()}
                    </span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => {
                  setShowUserMenu(false);
                  navigate("/account/profile");
                }}
                className="group flex w-full items-center gap-3 px-4 py-3 text-left text-sm transition hover:bg-slate-800/60"
                style={{ color: "var(--color-text-primary)" }}
              >
                <span
                  className="flex h-9 w-9 items-center justify-center rounded-lg"
                  style={{
                    backgroundColor: "var(--color-primary-bg)",
                    color: "var(--color-primary)",
                  }}
                >
                  <UserCog size={17} />
                </span>
                <span className="flex-1 font-bold">Profile Settings</span>
                <ChevronRight
                  size={15}
                  style={{ color: "var(--color-text-muted)" }}
                />
              </button>
              <button
                onClick={() => {
                  setShowUserMenu(false);
                  logout();
                }}
                className="flex w-full items-center gap-3 px-4 py-3 text-left text-sm transition hover:bg-slate-800/60"
                style={{
                  color: "var(--color-text-muted)",
                  borderTop: "1px solid var(--color-border-subtle)",
                }}
              >
                <span
                  className="flex h-9 w-9 items-center justify-center rounded-lg"
                  style={{
                    backgroundColor: "var(--color-danger-bg)",
                    color: "var(--color-danger)",
                  }}
                >
                  <LogOut size={17} />
                </span>
                <span className="flex-1 font-bold">Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
