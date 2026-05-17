import { useState, useEffect, useRef, useCallback } from "react";
import api from "../services/api";

const ETL_STEPS = [
  { key: "etl_service_types", label: "Service Types", icon: "settings" },
  { key: "etl_services", label: "Services", icon: "tag" },
  { key: "etl_users", label: "Users", icon: "users" },
  { key: "etl_subscriptions", label: "Subscriptions", icon: "clipboard-list" },
  { key: "etl_billing_events", label: "Billing Events", icon: "credit-card" },
  { key: "etl_unsubscriptions", label: "Unsubscriptions", icon: "door-open" },
  { key: "etl_user_activities", label: "User Activities", icon: "bar-chart-3" },
  { key: "etl_sms_events", label: "SMS Events", icon: "smartphone" },
  { key: "etl_cohorts", label: "Retention Cohorts", icon: "target" },
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
  const [runLog, setRunLog] = useState("");
  const [isStopping, setIsStopping] = useState(false);

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
          try {
            const logRes = await api.get(`/admin/import/run-etl/${id}/log`, {
              params: { limit: 200 },
            });
            setRunLog(logRes.data?.log || "");
          } catch {
            // Ignore transient log fetch errors during polling.
          }

          if (["success", "failed", "stopped"].includes(res.data.status)) {
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
    setRunLog("");
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
        current_step_label: "Service Types",
        total_steps: 9,
        progress_pct: 0,
        rows_inserted: 0,
        rows_skipped: 0,
        duration_sec: 0,
        steps_done: [],
      });
      startPolling(id);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to start ETL pipeline.");
    } finally {
      setIsLaunching(false);
    }
  }, [mode, demoUsers, truncate, dryRun, startPolling]);

  const stopETL = useCallback(async () => {
    if (!activeRun?.log_id) return;
    setError(null);
    setIsStopping(true);
    try {
      await api.post(`/admin/import/run-etl/${activeRun.log_id}/stop`);
      setActiveRun((prev) => (prev ? { ...prev, status: "stopping" } : prev));
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to stop ETL pipeline.");
    } finally {
      setIsStopping(false);
    }
  }, [activeRun]);

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
    runLog,
    stopETL,
    isStopping,
  };
}
