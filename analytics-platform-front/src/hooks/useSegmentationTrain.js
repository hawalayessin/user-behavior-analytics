import { useCallback, useState } from "react";
import api from "../services/api";

export function useSegmentationTrain() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [job, setJob] = useState(null);

  const train = useCallback(async ({ start_date, end_date, service_id } = {}) => {
    setLoading(true);
    setError(null);
    setJob(null);
    try {
      const response = await api.post("/analytics/segmentation/train", null, {
        params: { start_date, end_date, service_id },
      });
      const result = response?.data ?? null;
      setJob(result);
      return result;
    } catch (err) {
      const detail = err?.response?.data?.detail;
      const msg =
        typeof detail === "string"
          ? detail
          : detail?.message ?? err.message ?? "Error training segmentation model";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { train, loading, error, job };
}
