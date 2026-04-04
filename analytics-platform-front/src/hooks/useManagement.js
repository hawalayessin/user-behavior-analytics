import { useCallback, useEffect, useState } from "react"
import api from "../services/api"
import { getApiErrorMessage } from "../utils/apiError"

export function useManagement() {
  const [services, setServices] = useState([])
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchAll = useCallback(async () => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      setServices([])
      setCampaigns([])
      setError("Unauthorized: please login as admin")
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)
    try {
      const [sv, cp] = await Promise.all([
        api.get("/admin/management/services"),
        api.get("/admin/management/campaigns"),
      ])
      setServices(sv.data ?? [])
      setCampaigns(cp.data ?? [])
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load management data"))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAll()
  }, [fetchAll])

  const createService = async (payload) => {
    const res = await api.post("/admin/management/services", payload)
    await fetchAll()
    return res.data
  }
  const updateService = async (id, payload) => {
    const res = await api.put(`/admin/management/services/${id}`, payload)
    await fetchAll()
    return res.data
  }
  const deleteService = async (id) => {
    const res = await api.delete(`/admin/management/services/${id}`)
    await fetchAll()
    return res.data
  }

  const createCampaign = async (payload) => {
    const res = await api.post("/admin/management/campaigns", payload)
    await fetchAll()
    return res.data
  }

  const uploadCampaignTargets = async (file) => {
    const formData = new FormData()
    formData.append("targets_file", file)
    const res = await api.post("/admin/management/campaigns/upload-targets", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    return res.data
  }
  const updateCampaign = async (id, payload) => {
    const res = await api.put(`/admin/management/campaigns/${id}`, payload)
    await fetchAll()
    return res.data
  }
  const deleteCampaign = async (id) => {
    const res = await api.delete(`/admin/management/campaigns/${id}`)
    await fetchAll()
    return res.data
  }

  return {
    services,
    campaigns,
    loading,
    error,
    refetch: fetchAll,
    createService,
    updateService,
    deleteService,
    createCampaign,
    uploadCampaignTargets,
    updateCampaign,
    deleteCampaign,
  }
}
