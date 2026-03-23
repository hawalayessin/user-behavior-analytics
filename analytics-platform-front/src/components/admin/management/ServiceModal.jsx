import { useEffect, useMemo, useState } from "react"
import PropTypes from "prop-types"
import { X } from "lucide-react"
import { getApiErrorMessage } from "../../../utils/apiError"

export default function ServiceModal({ open, mode, initialValue, onClose, onSave }) {
  const [name, setName] = useState("")
  const [billingType, setBillingType] = useState("daily")
  const [price, setPrice] = useState("")
  const [errors, setErrors] = useState({})
  const [formError, setFormError] = useState("")
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!open) return
    setName(initialValue?.name ?? "")
    setBillingType(initialValue?.billing_type ?? "daily")
    setPrice(initialValue?.price != null ? String(initialValue.price) : "")
    setErrors({})
    setFormError("")
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

  const title = mode === "edit" ? "Edit Service" : "Add New Service"

  const payload = useMemo(() => {
    return {
      name: name.trim(),
      billing_type: billingType,
      price: Number(price),
    }
  }, [name, billingType, price])

  const validate = () => {
    const e = {}
    if (!payload.name) e.name = "Service name is required."
    if (payload.name.length > 100) e.name = "Max 100 characters."
    if (!["daily", "weekly"].includes(payload.billing_type)) e.billing_type = "Invalid billing type."
    if (!Number.isFinite(payload.price) || payload.price <= 0) e.price = "Price must be > 0."
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const submit = async () => {
    if (!validate()) return
    setSaving(true)
    setFormError("")
    try {
      await onSave(payload)
      onClose()
    } catch (err) {
      setFormError(getApiErrorMessage(err, "Save failed"))
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
            <p className="text-sm text-slate-400 mt-1">Fill service details and save.</p>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-slate-800 rounded transition text-slate-400 hover:text-slate-200"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>

        {formError && (
          <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <p className="text-sm text-red-300">{formError}</p>
          </div>
        )}

        <div className="mt-5 space-y-4">
          <div>
            <label className="block text-sm text-slate-300 font-medium mb-1">Service Name *</label>
            <input
              value={name}
              onChange={(e) => { setName(e.target.value); if (formError) setFormError("") }}
              className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-100 focus:outline-none focus:border-violet-500"
              placeholder="e.g. Tawer"
            />
            {errors.name && <p className="text-xs text-red-300 mt-1">{errors.name}</p>}
          </div>

          <div>
            <label className="block text-sm text-slate-300 font-medium mb-1">Billing Type *</label>
            <div className="flex items-center gap-4">
              {[
                { v: "daily", label: "Daily" },
                { v: "weekly", label: "Weekly" },
              ].map((opt) => (
                <label key={opt.v} className="flex items-center gap-2 text-sm text-slate-200">
                  <input
                    type="radio"
                    name="billing"
                    value={opt.v}
                    checked={billingType === opt.v}
                    onChange={() => { setBillingType(opt.v); if (formError) setFormError("") }}
                  />
                  {opt.label}
                </label>
              ))}
            </div>
            {errors.billing_type && <p className="text-xs text-red-300 mt-1">{errors.billing_type}</p>}
          </div>

          <div>
            <label className="block text-sm text-slate-300 font-medium mb-1">Price (DT) *</label>
            <input
              value={price}
              onChange={(e) => { setPrice(e.target.value); if (formError) setFormError("") }}
              className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-100 focus:outline-none focus:border-violet-500"
              placeholder="e.g. 1.5"
              inputMode="decimal"
            />
            {errors.price && <p className="text-xs text-red-300 mt-1">{errors.price}</p>}
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
            {saving ? "Saving..." : "Save Service"}
          </button>
        </div>
      </div>
    </div>
  )
}

ServiceModal.propTypes = {
  open: PropTypes.bool.isRequired,
  mode: PropTypes.oneOf(["add", "edit"]).isRequired,
  initialValue: PropTypes.object,
  onClose: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired,
}
