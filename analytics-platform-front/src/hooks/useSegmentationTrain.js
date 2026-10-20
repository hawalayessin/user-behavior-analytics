import { useCallback, useRef, useState } from "react"
import api from "../services/api"

export function useSegmentationTrain() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [job, setJob] = useState(null)
  const pollRef = useRef(null)

  const train = useCallback(async () => {
    setLoading(true)
    setError(null)
    setJob(null)
    try {
      const startRes = await api.post("/analytics/segmentation/train/start")
      const jobId = startRes?.data?.job_id
      if (!jobId) throw new Error("Unable to start training job")

      return await new Promise((resolve, reject) => {
        pollRef.current = setInterval(async () => {
          try {
            const statusRes = await api.get(`/analytics/segmentation/train/${jobId}/status`)
            const current = statusRes?.data ?? null
            setJob(current)

            if (!current) return
            if (current.status === "success") {
              clearInterval(pollRef.current)
              pollRef.current = null
              resolve(current.summary ?? null)
            } else if (current.status === "failed") {
              clearInterval(pollRef.current)
              pollRef.current = null
              const msg = current.error || "Training failed"
              setError(msg)
              reject(new Error(msg))
            }
          } catch (pollErr) {
            clearInterval(pollRef.current)
            pollRef.current = null
            const msg = pollErr?.response?.data?.detail ?? pollErr.message ?? "Training poll failed"
            setError(msg)
            reject(pollErr)
          }
        }, 1500)
      })
    } catch (err) {
      setError(err?.response?.data?.detail ?? err.message ?? "Error training segmentation model")
      throw err
    } finally {
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
      setLoading(false)
    }
  }, [])

  return { train, loading, error, job }
}