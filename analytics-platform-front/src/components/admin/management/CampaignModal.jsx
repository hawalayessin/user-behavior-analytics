import { useEffect, useMemo, useState } from "react"
import PropTypes from "prop-types"
import { X } from "lucide-react"

export default function CampaignModal({ open, mode, initialValue, services, onClose, onSave }) {
  const [name, setName] = useState("")
  const [serviceId, setServiceId] = useState("")
  const [sendDate, setSendDate] = useState("")
  const [targetSize, setTargetSize] = useState("")
  const [errors, setErrors] = useState({})
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!open) return
    setName(initialValue?.name ?? "")
    setServiceId(initialValue?.service_id ?? "")
    setSendDate(initialValue?.send_date ?? "")
    setTargetSize(initialValue?.target_size != null ? String(initialValue.target_size) : "")
    setErrors({})
    setSaving(false)
  }, [open, initialValue])

  useEffect(() => {
    if (!open) return
    const onKeyDown = (e) => {
      if (e.key === "Escape") onClose()
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [open, onClose])

  const title = mode === "edit" ? "Edit Campaign" : "Add New Campaign"

  const payload = useMemo(() => {
    return {
      name: name.trim(),
      service_id: serviceId,
      send_date: sendDate ? new Date(sendDate).toISOString() : null,
      target_size: Number(targetSize),
    }
  }, [name, serviceId, sendDate, targetSize])

  const validate = () => {
    const e = {}
    if (!payload.name) e.name = "Campaign name is required."
    if (payload.name.length > 255) e.name = "Max 255 characters."
    if (mode === "add" && !payload.service_id) e.service_id = "Service is required."
    if (!sendDate) e.send_date = "Send date is required."
    if (!Number.isFinite(payload.target_size) || payload.target_size <= 0) e.target_size = "Target size must be > 0."
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const submit = async () => {
    if (!validate()) return
    setSaving(true)
    try {
      const out = { name: payload.name, send_date: payload.send_date, target_size: payload.target_size }
      if (mode === "add") out.service_id = payload.service_id
      await onSave(out)
      onClose()
    } finally {
      setSaving(false)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-700 rounded-2xl p-6 shadow-xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-slate-100">{title}</h3>
            <p className="text-sm text-slate-400 mt-1">Fill campaign details and save.</p>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-slate-800 rounded transition text-slate-400 hover:text-slate-200"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>

        <div className="mt-5 space-y-4">
          <div>
            <label className="block text-sm text-slate-300 font-medium mb-1">Campaign Name *</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-100 focus:outline-none focus:border-violet-500"
              placeholder="e.g. Acquisition Tawer - Nov 2025"
            />
            {errors.name && <p className="text-xs text-red-300 mt-1">{errors.name}</p>}
          </div>

          <div>
            <label className="block text-sm text-slate-300 font-medium mb-1">Service *</label>
            <select
              value={serviceId}
              onChange={(e) => setServiceId(e.target.value)}
              disabled={mode === "edit"}
              className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-100 focus:outline-none focus:border-violet-500 disabled:opacity-60"
            >
              <option value="">Select a service</option>
              {(services ?? []).map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
            {errors.service_id && <p className="text-xs text-red-300 mt-1">{errors.service_id}</p>}
            {mode === "edit" && (
              <p className="text-xs text-slate-500 mt-1">Service cannot be changed after creation.</p>
            )}
          </div>

          <div>
            <label className="block text-sm text-slate-300 font-medium mb-1">Send Date *</label>
            <input
              type="date"
              value={sendDate}
              onChange={(e) => setSendDate(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-100 focus:outline-none focus:border-violet-500"
            />
            {errors.send_date && <p className="text-xs text-red-300 mt-1">{errors.send_date}</p>}
          </div>

          <div>
            <label className="block text-sm text-slate-300 font-medium mb-1">Target Size *</label>
            <input
              value={targetSize}
              onChange={(e) => setTargetSize(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-100 focus:outline-none focus:border-violet-500"
              placeholder="SMS recipients"
              inputMode="numeric"
            />
            {errors.target_size && <p className="text-xs text-red-300 mt-1">{errors.target_size}</p>}
          </div>
        </div>

        <div className="mt-6 flex gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="flex-1 px-4 py-2 border border-slate-700 rounded-lg text-slate-300 font-semibold hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={submit}
            disabled={saving}
            className="flex-1 px-4 py-2 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition"
          >
            {saving ? "Saving..." : "Save Campaign"}
          </button>
        </div>
      </div>
    </div>
  )
}

CampaignModal.propTypes = {
  open: PropTypes.bool.isRequired,
  mode: PropTypes.oneOf(["add", "edit"]).isRequired,
  initialValue: PropTypes.object,
  services: PropTypes.array,
  onClose: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired,
}

