import { useState, useRef, useCallback, useEffect } from "react";
import { ChevronLeft, ChevronRight, LogOut, Zap, ChevronDown } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { navigationConfig } from "./navConfig";
import { ThemeToggleWithLabel } from "./ThemeToggle";

export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [expandedSections, setExpandedSections] = useState({});
  const navRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { full_name, logout, isAdmin } = useAuth();
  const sidebarScrollKey = "sidebar-nav-scroll";

  useEffect(() => {
    const mainContent = document.querySelector('main');
    if (!mainContent) return;

    const handleScroll = () => {
      sessionStorage.setItem(`scroll-${location.pathname}`, mainContent.scrollTop);
    };

    mainContent.addEventListener('scroll', handleScroll);

    const savedScroll = sessionStorage.getItem(`scroll-${location.pathname}`);
    if (savedScroll) {
      mainContent.scrollTop = parseInt(savedScroll, 10);
    }

    return () => {
      mainContent.removeEventListener('scroll', handleScroll);
    };
  }, [location.pathname]);

  useEffect(() => {
    const navEl = navRef.current;
    if (!navEl) return;

    const saved = sessionStorage.getItem(sidebarScrollKey);
    if (saved) {
      navEl.scrollTop = parseInt(saved, 10);
    }

    const handleNavScroll = () => {
      sessionStorage.setItem(sidebarScrollKey, String(navEl.scrollTop));
    };

    navEl.addEventListener("scroll", handleNavScroll, { passive: true });
    return () => {
      navEl.removeEventListener("scroll", handleNavScroll);
    };
  }, [location.pathname]);

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

  const handleNavClick = useCallback((route) => (e) => {
    e.preventDefault();
    if (navRef.current) {
      sessionStorage.setItem(sidebarScrollKey, String(navRef.current.scrollTop));
    }

    const mainContent = document.querySelector('main');
    if (mainContent) {
      const scrollPos = mainContent.scrollTop;
      const currentPath = location.pathname;

      sessionStorage.setItem(`scroll-${currentPath}`, scrollPos);
      navigate(route);

      requestAnimationFrame(() => {
        const savedScroll = sessionStorage.getItem(`scroll-${route}`);
        if (mainContent && savedScroll) {
          mainContent.scrollTop = parseInt(savedScroll, 10);
        }
      });
    } else {
      navigate(route);
    }
  }, [navigate, location.pathname]);

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
      <nav
        ref={navRef}
        className="flex-1 overflow-y-auto sidebar-nav"
      >
        {navigationConfig.map((section) => {
          if (section.adminOnly && !isAdmin()) return null;

          const isCollapsible = section.collapsible;
          const isExpanded = expandedSections[section.section] ?? true;

          return (
            <div key={section.section} className="py-4">
              {isCollapsible && !isCollapsed ? (
                <button
                  onClick={() =>
                    setExpandedSections((prev) => ({
                      ...prev,
                      [section.section]: !prev[section.section],
                    }))
                  }
                  className="w-full flex items-center justify-between px-4 mb-2 text-xs font-semibold uppercase tracking-widest hover:text-[var(--color-text-secondary)] transition-colors"
                  style={{ color: "var(--color-text-disabled)" }}
                >
                  <span>{section.section}</span>
                  <ChevronDown
                    size={14}
                    className={`transition-transform duration-200 ${isExpanded ? "rotate-0" : "-rotate-90"}`}
                  />
                </button>
              ) : (
                !isCollapsed && (
                  <h3
                    className="px-4 mb-2 text-xs font-semibold uppercase tracking-widest"
                    style={{ color: "var(--color-text-disabled)" }}
                  >
                    {section.section}
                  </h3>
                )
              )}

              {(!isCollapsible || isExpanded || isCollapsed) && (
                <div className="space-y-1">
                  {section.items.map((item) => {
                    const isActive = location.pathname === item.route;
                    return (
                      <a
                        key={item.route}
                        href={item.route}
                        onClick={handleNavClick(item.route)}
                        className="group relative flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 border-l-2 cursor-pointer"
                        style={{
                          backgroundColor: isActive ? "var(--color-primary-bg)" : "transparent",
                          color: isActive ? "var(--color-primary)" : "var(--color-text-muted)",
                          borderLeftColor: isActive ? "var(--color-primary)" : "transparent",
                        }}
                      >
                        <item.icon
                          className="w-5 h-5 flex-shrink-0 transition-colors duration-200"
                          style={{
                            color: isActive
                              ? "var(--color-primary)"
                              : "var(--color-text-muted)",
                          }}
                        />
                        {!isCollapsed && (
                          <span className="text-sm font-medium truncate">{item.label}</span>
                        )}
                      </a>
                    );
                  })}

                  {!isCollapsed && section.section === "ADMIN" && (
                    <div className="px-3 pt-2">
                      <ThemeToggleWithLabel />
                    </div>
                  )}
                </div>
              )}
            </div>
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
