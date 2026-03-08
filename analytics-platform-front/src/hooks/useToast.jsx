import { useState, useCallback } from "react"

const TOAST_DURATION = 3000

export const useToast = () => {
  const [toast, setToast] = useState(null)

  const showToast = useCallback((message, type = "info") => {
    setToast({ message, type, id: Date.now() })

    const timer = setTimeout(() => {
      setToast(null)
    }, TOAST_DURATION)

    return () => clearTimeout(timer)
  }, [])

  const Toast = toast ? <ToastComponent toast={toast} onDismiss={() => setToast(null)} /> : null

  return { showToast, Toast }
}

const ToastComponent = ({ toast, onDismiss }) => {
  const baseStyles =
    "fixed top-4 right-4 px-4 py-3 rounded-lg border flex items-center gap-2 animate-slide-in"

  const styles = {
    success: "bg-emerald-500/20 border-emerald-500 text-emerald-300",
    error: "bg-red-500/20 border-red-500 text-red-300",
    info: "bg-indigo-500/20 border-indigo-500 text-indigo-300",
  }

  return (
    <div className={`${baseStyles} ${styles[toast.type] || styles.info}`}>
      <span>{toast.message}</span>
      <button onClick={onDismiss} className="ml-2 font-bold hover:opacity-75">
        ×
      </button>
    </div>
  )
}
