import { useState, useEffect, useRef, useCallback } from "react";
import api from "../services/api";

const ETL_STEPS = [
  { key: "etl_service_types", label: "Types de services", icon: "⚙️" },
  { key: "etl_services", label: "Services", icon: "🏷️" },
  { key: "etl_users", label: "Utilisateurs", icon: "👥" },
  { key: "etl_subscriptions", label: "Abonnements", icon: "📋" },
  { key: "etl_billing_events", label: "Événements de facturation", icon: "💳" },
  { key: "etl_unsubscriptions", label: "Désabonnements", icon: "🚪" },
  { key: "etl_user_activities", label: "Activités utilisateurs", icon: "📊" },
  { key: "etl_sms_events", label: "Événements SMS", icon: "📱" },
  { key: "etl_cohorts", label: "Cohortes de rétention", icon: "🎯" },
];

export function useETLPipeline() {
  const [mode, setMode] = useState("demo");
  const [demoUsers, setDemoUsers] = useState(50000);
  const [truncate, setTruncate] = useState(true);
  const [dryRun, setDryRun] = useState(true);

  const [activeRun, setActiveRun] = useState(null);
  const [isLaunching, setIsLaunching] = useState(false);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState(null);

  const pollingRef = useRef(null);

  const fetchHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const res = await api.get("/admin/import/etl-history");
      setHistory(res.data ?? []);
    } catch (_err) {
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  const startPolling = useCallback(
    (id) => {
      if (pollingRef.current) clearInterval(pollingRef.current);

      pollingRef.current = setInterval(async () => {
        try {
          const res = await api.get(`/admin/import/run-etl/${id}/status`);
          setActiveRun(res.data);

          if (res.data.status === "success" || res.data.status === "failed") {
            clearInterval(pollingRef.current);
            pollingRef.current = null;
            fetchHistory();
          }
        } catch (_err) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
      }, 2000);
    },
    [fetchHistory],
  );

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  const launchETL = useCallback(async () => {
    setError(null);
    setIsLaunching(true);
    setActiveRun(null);
    try {
      const res = await api.post("/admin/import/run-etl", null, {
        params: {
          mode,
          demo_users: demoUsers,
          truncate: dryRun ? false : truncate,
          dry_run: dryRun,
        },
      });
      const id = res.data.log_id;
      setActiveRun({
        log_id: id,
        status: "running",
        mode,
        dry_run: dryRun,
        truncate: dryRun ? false : truncate,
        demo_users: mode === "demo" ? demoUsers : null,
        current_step: "etl_service_types",
        current_step_num: 1,
        current_step_label: "Types de services",
        total_steps: 9,
        progress_pct: 0,
        rows_inserted: 0,
        rows_skipped: 0,
        duration_sec: 0,
        steps_done: [],
      });
      startPolling(id);
    } catch (err) {
      setError(err?.response?.data?.detail || "Erreur lors du lancement du pipeline ETL.");
    } finally {
      setIsLaunching(false);
    }
  }, [mode, demoUsers, truncate, dryRun, startPolling]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return {
    mode,
    setMode,
    demoUsers,
    setDemoUsers,
    truncate,
    setTruncate,
    dryRun,
    setDryRun,
    activeRun,
    isLaunching,
    launchETL,
    history,
    historyLoading,
    fetchHistory,
    error,
    ETL_STEPS,
  };
}
