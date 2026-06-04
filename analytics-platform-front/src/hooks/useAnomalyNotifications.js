import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  getAnomalyNotifications,
  markAnomalyNotificationRead,
} from "../services/notifications"

export const anomalyNotificationsKey = ["notifications", "anomalies"]

export function useAnomalyNotifications() {
  const queryClient = useQueryClient()
  const query = useQuery({
    queryKey: anomalyNotificationsKey,
    queryFn: getAnomalyNotifications,
    refetchInterval: 30_000,
    refetchIntervalInBackground: true,
    staleTime: 25_000,
    refetchOnMount: true,
  })

  const markReadMutation = useMutation({
    mutationFn: markAnomalyNotificationRead,
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: anomalyNotificationsKey })
      const previous = queryClient.getQueryData(anomalyNotificationsKey)
      queryClient.setQueryData(anomalyNotificationsKey, (items = []) =>
        items.map((item) => (item.id === id ? { ...item, read: true } : item)),
      )
      return { previous }
    },
    onError: (_error, _id, context) => {
      if (context?.previous) {
        queryClient.setQueryData(anomalyNotificationsKey, context.previous)
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: anomalyNotificationsKey })
    },
  })

  const notifications = Array.isArray(query.data) ? query.data : []
  const unreadCount = notifications.filter((item) => !item.read).length

  return {
    notifications,
    unreadCount,
    isLoading: query.isLoading,
    isFetching: query.isFetching,
    markRead: markReadMutation.mutate,
  }
}
