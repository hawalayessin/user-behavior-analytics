import api from "./api"

export async function getAnomalyNotifications() {
  const res = await api.get("/notifications/anomalies")
  return res.data
}

export async function markAnomalyNotificationRead(id) {
  const res = await api.patch(`/notifications/anomalies/${id}/read`)
  return res.data
}
