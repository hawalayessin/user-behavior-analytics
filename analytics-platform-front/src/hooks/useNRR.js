import { useQuery } from "@tanstack/react-query"
import api from "../services/api"

export function useNRR(filters = {}) {
    const { data, isLoading, error, refetch } = useQuery({
        queryKey: ["analytics", "nrr", filters?.end_date ?? null, filters?.service_id ?? null],
        queryFn: async () => {
            const params = new URLSearchParams()
            if (filters?.end_date) params.set("end_date", filters.end_date)
            if (filters?.service_id) params.set("service_id", filters.service_id)
            const query = params.toString()
            const res = await api.get(`/analytics/nrr${query ? `?${query}` : ""}`)
            return res.data
        },
        staleTime: 5 * 60 * 1000,
    })

    return {
        data: data ?? null,
        loading: isLoading,
        error: error?.response?.data?.detail ?? error?.message ?? null,
        refetch,
    }
}
