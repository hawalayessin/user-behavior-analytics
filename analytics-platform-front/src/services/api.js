import axios from "axios"

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",   // ✅ IMPORTANT
})

const inFlightGetRequests = new Map()
const getResponseCache = new Map()
const DEFAULT_GET_CACHE_TTL_MS = 15000

// Intercepteur JWT automatique
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function getWithCache(url, { force = false, ttlMs = DEFAULT_GET_CACHE_TTL_MS } = {}) {
  if (!force) {
    const cached = getResponseCache.get(url)
    if (cached && Date.now() - cached.timestamp < ttlMs) {
      return cached.data
    }

    const pending = inFlightGetRequests.get(url)
    if (pending) {
      return pending
    }
  }

  const request = api
    .get(url)
    .then((response) => {
      getResponseCache.set(url, { data: response.data, timestamp: Date.now() })
      return response.data
    })
    .finally(() => {
      inFlightGetRequests.delete(url)
    })

  inFlightGetRequests.set(url, request)
  return request
}

export default api