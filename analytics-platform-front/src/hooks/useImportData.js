import { useCallback, useEffect, useState } from "react"
import api from "../services/api"

export default function useImportData() {
  const [loading, setLoading] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])

  const refreshHistory = useCallback(async () => {
    setHistoryLoading(true)
    try {
      const res = await api.get("/admin/import/history")
      setHistory(res.data?.history ?? [])
    } catch (e) {
      setHistory([])
    } finally {
      setHistoryLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshHistory()
  }, [refreshHistory])

  const stageCsv = useCallback(async ({ file, table, mode }) => {
    setLoading(true)
    setError(null)
    try {
      const form = new FormData()
      form.append("file", file)
      const params = new URLSearchParams()
      params.set("table", table)
      params.set("mode", mode)
      const res = await api.post(`/admin/import/csv?${params.toString()}`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      await refreshHistory()
      return res.data
    } catch (e) {
      const detail = e?.response?.data?.detail ?? e?.response?.data ?? e?.message ?? "Import failed"
      setError(detail)
      await refreshHistory()
      throw e
    } finally {
      setLoading(false)
    }
  }, [refreshHistory])

  const confirmCsv = useCallback(async ({ importId, table, mode, force }) => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      params.set("import_id", importId)
      params.set("table", table)
      params.set("mode", mode)
      params.set("force", String(!!force))
      const res = await api.post(`/admin/import/csv/confirm?${params.toString()}`)
      await refreshHistory()
      return res.data
    } catch (e) {
      const detail = e?.response?.data?.detail ?? e?.response?.data ?? e?.message ?? "Confirm failed"
      setError(detail)
      await refreshHistory()
      throw e
    } finally {
      setLoading(false)
    }
  }, [refreshHistory])

  const importDatabaseSql = useCallback(async ({ file, mode }) => {
    setLoading(true)
    setError(null)
    try {
      const form = new FormData()
      form.append("file", file)
      const params = new URLSearchParams()
      params.set("mode", mode)
      const res = await api.post(`/admin/import/database?${params.toString()}`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      await refreshHistory()
      return res.data
    } catch (e) {
      const detail = e?.response?.data?.detail ?? e?.response?.data ?? e?.message ?? "SQL import failed"
      setError(detail)
      await refreshHistory()
      throw e
    } finally {
      setLoading(false)
    }
  }, [refreshHistory])

  const downloadTemplate = useCallback(async (table) => {
    const res = await api.get(`/admin/import/template/${table}`, { responseType: "blob" })
    const blob = new Blob([res.data], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${table}_template.csv`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }, [])

  return {
    loading,
    historyLoading,
    error,
    history,
    refreshHistory,
    stageCsv,
    confirmCsv,
    importDatabaseSql,
    downloadTemplate,
  }
}

