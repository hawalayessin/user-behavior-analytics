import { useCallback, useState } from "react";
import api from "../services/api";

export function useRetentionRecompute() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const recompute = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await api.post("/analytics/retention/recompute");
            return res.data ?? null;
        } catch (err) {
            const msg =
                err?.response?.data?.detail ??
                err?.message ??
                "Erreur lors du recalcul des cohortes";
            setError(msg);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    return { recompute, loading, error };
}
