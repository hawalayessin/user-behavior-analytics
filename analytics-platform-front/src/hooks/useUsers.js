import { useMemo } from "react"
import { useQuery } from "@tanstack/react-query"
import { getUsersPage } from "../services/api"

export function useUsers({ status, search, service_id, cursor = null, limit = 10 }) {
  const normalizedCursor = useMemo(() => ({
    created_at: cursor?.created_at ?? null,
    id: cursor?.id ?? null,
  }), [cursor?.created_at, cursor?.id])

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: [
      "users",
      "activity-v2",
      status ?? null,
      search ?? null,
      service_id ?? null,
      limit,
      normalizedCursor.created_at,
      normalizedCursor.id,
    ],
    queryFn: () => getUsersPage({
      status,
      search,
      service_id,
      page_size: limit,
      cursor,
    }),
    staleTime: 30 * 1000,
    gcTime: 10 * 60 * 1000,
    refetchOnMount: "always",
  })

  return {
    data: data ?? null,
    loading: isLoading,
    error: error?.response?.data?.detail ?? error?.message ?? null,
    refetch,
  }
}