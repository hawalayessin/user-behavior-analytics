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
    "fixed top-6 left-1/2 z-[80] flex w-[calc(100vw-2rem)] max-w-md -translate-x-1/2 items-center justify-between gap-3 rounded-lg border px-4 py-3 text-sm shadow-xl backdrop-blur"

  const styles = {
    success: "bg-emerald-500/20 border-emerald-500 text-emerald-300",
    error: "bg-red-500/20 border-red-500 text-red-300",
    info: "bg-indigo-500/20 border-indigo-500 text-indigo-300",
  }

  return (
    <div className={`${baseStyles} ${styles[toast.type] || styles.info}`}>
      <span>{toast.message}</span>
      <button
        type="button"
        onClick={onDismiss}
        className="ml-2 font-bold hover:opacity-75"
        aria-label="Dismiss notification"
      >
        &times;
      </button>
    </div>
  )
}
