import axios from "axios"

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  withCredentials: true,
})

let inMemoryAccessToken = null
let authRefreshHandler = null
let authFailureHandler = null

export function setAccessToken(token) {
  inMemoryAccessToken = token || null
}

export function getAccessToken() {
  return inMemoryAccessToken
}

export function setAuthRefreshHandler(handler) {
  authRefreshHandler = typeof handler === "function" ? handler : null
}

export function setAuthFailureHandler(handler) {
  authFailureHandler = typeof handler === "function" ? handler : null
}

const inFlightGetRequests = new Map()
const getResponseCache = new Map()
const DEFAULT_GET_CACHE_TTL_MS = 5 * 60 * 1000
const GET_CACHE_STORAGE_KEY = "digmaco:get-cache:v1"

function loadPersistedGetCache() {
  try {
    const raw = sessionStorage.getItem(GET_CACHE_STORAGE_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return
    parsed.forEach(([key, value]) => {
      if (!key || !value || typeof value.timestamp !== "number") return
      getResponseCache.set(key, value)
    })
  } catch {
    // Ignore invalid session cache payloads
  }
}

function persistGetCache() {
  try {
    const now = Date.now()
    const entries = Array.from(getResponseCache.entries())
      .filter(([, value]) => now - value.timestamp < 24 * 60 * 60 * 1000)
      .slice(-300)
    sessionStorage.setItem(GET_CACHE_STORAGE_KEY, JSON.stringify(entries))
  } catch {
    // Ignore storage quota / privacy mode failures
  }
}

loadPersistedGetCache()

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

api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function shouldAttemptTokenRefresh(error) {
  const status = error?.response?.status
  const config = error?.config
  if (status !== 401 || !config || config._retry || config.skipAuthRefresh) {
    return false
  }

  const url = String(config.url || "")
  return !(
    url.includes("/auth/login") ||
    url.includes("/auth/refresh") ||
    url.includes("/auth/logout")
  )
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (!shouldAttemptTokenRefresh(error)) {
      return Promise.reject(error)
    }

    const originalRequest = error.config
    originalRequest._retry = true

    try {
      const newToken = authRefreshHandler ? await authRefreshHandler() : null
      if (newToken) {
        originalRequest.headers = originalRequest.headers || {}
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return api(originalRequest)
      }
    } catch {
      // Fall through to auth failure handling below.
    }

    if (authFailureHandler) {
      authFailureHandler()
    }
    return Promise.reject(error)
  },
)

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
      persistGetCache()
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
