import { useEffect, useRef, useState } from "react"
import {
  AlertTriangle,
  Bell,
  CheckCircle2,
  TrendingDown,
  TrendingUp,
  X,
} from "lucide-react"
import { useAnomalyNotifications } from "../../hooks/useAnomalyNotifications"

function formatDate(value) {
  if (!value) return "Date inconnue"
  return new Intl.DateTimeFormat("fr-FR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value))
}

function formatNumber(value) {
  return new Intl.NumberFormat("fr-FR", {
    maximumFractionDigits: 2,
  }).format(Number(value || 0))
}

function toneFor(notification) {
  const positive = notification.direction === "positive"
  return positive
    ? {
        icon: TrendingUp,
        border: "border-emerald-500/70",
        bg: "bg-emerald-500/10",
        text: "text-emerald-300",
        badge: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
      }
    : {
        icon: TrendingDown,
        border: "border-red-500/70",
        bg: "bg-red-500/10",
        text: "text-red-300",
        badge: "bg-red-500/15 text-red-300 border-red-500/30",
      }
}

function severityBadge(severity) {
  return severity === "CRITICAL"
    ? "bg-red-500/15 text-red-300 border-red-500/30"
    : "bg-orange-500/15 text-orange-300 border-orange-500/30"
}

export default function AnomalyNotifications() {
  const [open, setOpen] = useState(false)
  const [selected, setSelected] = useState(null)
  const wrapperRef = useRef(null)
  const { notifications, unreadCount, isLoading, markRead } =
    useAnomalyNotifications()

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const openNotification = (notification) => {
    setSelected(notification)
    setOpen(false)
    if (!notification.read) {
      markRead(notification.id)
    }
  }

  return (
    <div className="relative" ref={wrapperRef}>
      <button
        onClick={() => setOpen((value) => !value)}
        className="relative p-2 rounded-lg transition-colors duration-200 hover:bg-slate-800/60"
        style={{ color: "var(--color-text-muted)" }}
        aria-label="Notifications"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 min-w-5 h-5 px-1 rounded-full bg-red-500 text-white text-[11px] leading-5 text-center shadow-lg shadow-red-500/30">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      <div
        className={`absolute right-0 mt-2 w-[22rem] max-w-[calc(100vw-2rem)] origin-top-right rounded-lg shadow-2xl z-50 overflow-hidden transition-all duration-200 ${
          open
            ? "opacity-100 translate-y-0 scale-100 pointer-events-auto"
            : "opacity-0 -translate-y-2 scale-95 pointer-events-none"
        }`}
        style={{
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
        }}
      >
        <div
          className="px-4 py-3 flex items-center justify-between"
          style={{ borderBottom: "1px solid var(--color-border)" }}
        >
          <div>
            <h3
              className="text-sm font-semibold"
              style={{ color: "var(--color-text-primary)" }}
            >
              Notifications
            </h3>
            <p className="text-xs mt-0.5" style={{ color: "var(--color-text-muted)" }}>
              Anomalies critiques et elevees
            </p>
          </div>
          {unreadCount > 0 && (
            <span className="text-xs px-2 py-1 rounded-full bg-red-500/15 text-red-300 border border-red-500/30">
              {unreadCount} non lue{unreadCount > 1 ? "s" : ""}
            </span>
          )}
        </div>

        <div className="max-h-80 overflow-y-auto scrollbar-modern">
          {isLoading ? (
            <div className="px-4 py-6 text-sm text-center" style={{ color: "var(--color-text-muted)" }}>
              Chargement...
            </div>
          ) : notifications.length === 0 ? (
            <div className="px-4 py-6 text-sm text-center" style={{ color: "var(--color-text-muted)" }}>
              Aucune anomalie critique recente.
            </div>
          ) : (
            notifications.map((notification) => {
              const tone = toneFor(notification)
              const Icon = tone.icon
              return (
                <button
                  key={notification.id}
                  onClick={() => openNotification(notification)}
                  className={`w-full px-4 py-3 text-left border-l-4 ${tone.border} ${tone.bg} hover:bg-slate-800/60 transition-all duration-200`}
                  style={{ borderBottom: "1px solid var(--color-border)" }}
                >
                  <div className="flex items-start gap-3">
                    <div className={`mt-0.5 ${tone.text}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <p className="truncate text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>
                          {notification.metric_name}
                        </p>
                        {!notification.read && (
                          <span className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0" />
                        )}
                      </div>
                      <p className="text-xs mt-1 line-clamp-2" style={{ color: "var(--color-text-secondary)" }}>
                        {notification.message}
                      </p>
                      <div className="mt-2 flex items-center gap-2">
                        <span className={`text-[11px] px-2 py-0.5 rounded-full border ${severityBadge(notification.severity)}`}>
                          {notification.severity}
                        </span>
                        <span className="text-[11px]" style={{ color: "var(--color-text-muted)" }}>
                          {formatDate(notification.detected_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                </button>
              )
            })
          )}
        </div>
      </div>

      {selected && (
        <div className="fixed inset-0 z-[90] flex items-start justify-center px-4 pt-24 pb-6 bg-slate-950/75 backdrop-blur-sm animate-[fadeIn_160ms_ease-out]">
          <div
            className={`w-full max-w-lg max-h-[calc(100vh-7.5rem)] rounded-lg shadow-2xl overflow-y-auto scrollbar-modern border-l-4 ${toneFor(selected).border} animate-[popIn_180ms_ease-out]`}
            style={{
              backgroundColor: "var(--color-bg-card)",
              borderTop: "1px solid var(--color-border)",
              borderRight: "1px solid var(--color-border)",
              borderBottom: "1px solid var(--color-border)",
            }}
          >
            <div className="px-5 py-4 flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg ${toneFor(selected).bg} ${toneFor(selected).text}`}>
                  {selected.direction === "positive" ? (
                    <TrendingUp className="w-5 h-5" />
                  ) : (
                    <AlertTriangle className="w-5 h-5" />
                  )}
                </div>
                <div>
                  <h2 className="text-lg font-bold leading-tight">
                    {selected.metric_name}
                  </h2>
                  <p className="text-sm mt-1" style={{ color: "var(--color-text-muted)" }}>
                    {formatDate(selected.detected_at)}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="p-2 rounded-lg hover:bg-slate-800/60 transition"
                style={{ color: "var(--color-text-muted)" }}
                aria-label="Fermer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="px-5 pb-5 space-y-4">
              <div className="flex flex-wrap gap-2">
                <span className={`text-xs px-2.5 py-1 rounded-full border ${severityBadge(selected.severity)}`}>
                  {selected.severity}
                </span>
                <span className={`text-xs px-2.5 py-1 rounded-full border ${toneFor(selected).badge}`}>
                  {selected.direction === "positive" ? "Impact positif" : "Impact negatif"}
                </span>
                <span className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full bg-slate-500/10 text-slate-300 border border-slate-500/20">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Lue
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="rounded-lg bg-slate-900/40 border border-slate-700/50 p-3">
                  <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                    Z-Score
                  </p>
                  <p className="mt-1 text-lg font-bold">{formatNumber(selected.z_score)}</p>
                </div>
                <div className="rounded-lg bg-slate-900/40 border border-slate-700/50 p-3">
                  <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                    Valeur actuelle
                  </p>
                  <p className="mt-1 text-lg font-bold">{formatNumber(selected.current_value)}</p>
                </div>
                <div className="rounded-lg bg-slate-900/40 border border-slate-700/50 p-3">
                  <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
                    Valeur attendue
                  </p>
                  <p className="mt-1 text-lg font-bold">{formatNumber(selected.expected_value)}</p>
                </div>
              </div>

              <div className={`rounded-lg ${toneFor(selected).bg} border ${toneFor(selected).border} p-4`}>
                <p className="text-sm leading-6" style={{ color: "var(--color-text-secondary)" }}>
                  {selected.interpretation}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
