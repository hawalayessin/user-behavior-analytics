import axios from "axios"

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",   // ✅ IMPORTANT
})

const inFlightGetRequests = new Map()
const getResponseCache = new Map()
const DEFAULT_GET_CACHE_TTL_MS = 15000

function toCanonicalParams(params = {}) {
  return Object.keys(params)
    .sort()
    .map((key) => {
      const value = params[key]
      if (value === null || value === undefined || value === "") return null
      return `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`
    })
    .filter(Boolean)
    .join("&")
}

function buildCacheKey(url, params = null) {
  const qs = params ? toCanonicalParams(params) : ""
  return qs ? `${url}?${qs}` : url
}

// Intercepteur JWT automatique
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function getWithCache(url, { params = null, force = false, ttlMs = DEFAULT_GET_CACHE_TTL_MS } = {}) {
  const cacheKey = buildCacheKey(url, params)

  if (!force) {
    const cached = getResponseCache.get(cacheKey)
    if (cached && Date.now() - cached.timestamp < ttlMs) {
      return cached.data
    }

    const pending = inFlightGetRequests.get(cacheKey)
    if (pending) {
      return pending
    }
  }

  const request = api
    .get(url, { params })
    .then((response) => {
      getResponseCache.set(cacheKey, { data: response.data, timestamp: Date.now() })
      return response.data
    })
    .finally(() => {
      inFlightGetRequests.delete(cacheKey)
    })

  inFlightGetRequests.set(cacheKey, request)
  return request
}

export async function getUsersPage({
  status,
  search,
  service_id,
  page_size = 10,
  cursor = null,
} = {}) {
  const params = {
    page_size,
  }

  if (status && status !== "Tous") params.status = status
  if (search) params.search = search
  if (service_id) params.service_id = service_id
  if (cursor?.created_at && cursor?.id) {
    params.cursor_created_at = cursor.created_at
    params.cursor_id = cursor.id
  }

  const response = await api.get("/users", { params })
  return response.data
}

export default api