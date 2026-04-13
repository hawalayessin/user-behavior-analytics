import { useMemo } from "react"
import { useQuery } from "@tanstack/react-query"
import { getWithCache } from "../services/api"

export function useReactivationKPIs(filters = {}) {
    const normalizedFilters = useMemo(() => ({
        start_date: filters?.start_date ?? null,
        end_date: filters?.end_date ?? null,
        service_id: filters?.service_id ?? null,
    }), [filters?.end_date, filters?.service_id, filters?.start_date])

    const { data, isLoading, error, refetch } = useQuery({
        queryKey: [
            "churn-reactivation-kpis",
            normalizedFilters.start_date,
            normalizedFilters.end_date,
            normalizedFilters.service_id,
        ],
        queryFn: async () => {
            const params = new URLSearchParams()
            if (normalizedFilters.start_date) params.set("start_date", normalizedFilters.start_date)
            if (normalizedFilters.end_date) params.set("end_date", normalizedFilters.end_date)
            if (normalizedFilters.service_id) params.set("service_id", String(normalizedFilters.service_id))

            const qs = params.toString()
            const url = `/analytics/churn/reactivation/kpis${qs ? `?${qs}` : ""}`
            return await getWithCache(url, { ttlMs: 30000 })
        },
        staleTime: 60 * 1000,
        retry: 1,
    })

    return {
        data: data ?? null,
        isLoading,
        error: error?.response?.data?.detail ?? error?.message ?? null,
        refetch,
    }
}
