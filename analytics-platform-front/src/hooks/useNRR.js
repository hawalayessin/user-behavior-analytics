import { useQuery } from "@tanstack/react-query"
import api from "../services/api"

export function useNRR() {
    const { data, isLoading, error, refetch } = useQuery({
        queryKey: ["analytics", "nrr"],
        queryFn: async () => {
            const res = await api.get("/analytics/nrr")
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
