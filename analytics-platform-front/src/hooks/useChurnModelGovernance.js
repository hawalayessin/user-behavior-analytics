import { useQuery } from "@tanstack/react-query"
import api from "../services/api"

export function useChurnModelGovernance() {
    const { data, isLoading, error, refetch } = useQuery({
        queryKey: ["ml", "churn", "governance"],
        queryFn: async () => {
            const res = await api.get("/ml/churn/governance")
            return res.data ?? null
        },
        staleTime: 60 * 1000,
    })

    return {
        data,
        loading: isLoading,
        error: error?.response?.data?.detail ?? error?.message ?? null,
        refetch,
    }
}
