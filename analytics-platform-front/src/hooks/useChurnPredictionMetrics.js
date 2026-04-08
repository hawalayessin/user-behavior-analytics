import { useQuery } from "@tanstack/react-query"
import api from "../services/api"

export function useChurnPredictionMetrics() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["ml", "churn", "metrics"],
    queryFn: async () => {
      const res = await api.get("/ml/churn/metrics")
      return res.data ?? null
    },
  })

  return {
    data,
    loading: isLoading,
    error: error?.response?.data?.detail ?? error?.message ?? null,
    refetch,
  }
}

