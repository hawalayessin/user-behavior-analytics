import { useMemo } from "react"
import { useQuery } from "@tanstack/react-query"
import api from "../services/api"

/**
 * useCrossService
 * Fetches all 4 cross-service endpoints in parallel.
 * Accepts optional filters: { start_date, end_date, service_id }
 * Returns { overview, coSubscriptions, migrations, distribution, loading, error, refetch }
 */
export function useCrossService({ start_date, end_date, service_id } = {}) {
    const normalized = useMemo(() => ({
        start_date: start_date ?? null,
        end_date: end_date ?? null,
        service_id: service_id ?? null,
    }), [start_date, end_date, service_id])

    const { data, isLoading, error, refetch } = useQuery({
        queryKey: [
            "analytics",
            "cross-service",
            normalized.start_date,
            normalized.end_date,
            normalized.service_id,
        ],
        queryFn: async () => {
            const res = await api.get("/analytics/cross-service/all", {
                params: {
                    start_date: normalized.start_date,
                    end_date: normalized.end_date,
                    service_id: normalized.service_id,
                },
            })
            return res.data ?? null
        },
        staleTime: 60 * 1000,
        gcTime: 10 * 60 * 1000,
    })

    return {
        overview: data?.overview ?? null,
        coSubscriptions: data?.co_subscriptions ?? null,
        migrations: data?.migrations ?? null,
        distribution: data?.distribution ?? null,
        loading: isLoading,
        error: error?.response?.data?.detail ?? error?.message ?? null,
        refetch,
    }
}
