import React, { useState } from "react"
import PropTypes from "prop-types"
import { AlertTriangle, X } from "lucide-react"
import api from "../../services/api"
import { getApiErrorMessage } from "../../utils/apiError"

export default function ConfirmDeleteModal({ user, onClose, onSuccess }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleDelete = async () => {
    setLoading(true)
    try {
      await api.delete(`/platform-users/${user.id}`)
      onSuccess()
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to delete user"))
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 rounded-xl border border-slate-800 w-full max-w-md p-6 shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex-1" />
          <button
            onClick={onClose}
            className="p-1 hover:bg-slate-800 rounded transition text-slate-400 hover:text-slate-200"
          >
            <X size={20} />
          </button>
        </div>

        {/* Warning Icon */}
        <div className="flex justify-center mb-4">
          <AlertTriangle size={48} className="text-red-400" />
        </div>

        {/* Content */}
        <div className="text-center mb-6">
          <h2 className="text-lg font-bold text-slate-100 mb-2">Delete User Account</h2>
          <p className="text-slate-400 text-sm mb-4">
            This action is permanent and cannot be undone.
          </p>

          {/* User Info */}
          <div className="bg-slate-800/50 rounded-lg p-3 mb-4 text-left">
            <p className="text-sm font-semibold text-slate-200">{user.full_name}</p>
            <p className="text-sm text-slate-400">{user.email}</p>
          </div>

          {/* Error */}
          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg mb-4">
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}
        </div>

        {/* Buttons */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="flex-1 px-4 py-2 border border-slate-700 rounded-lg text-slate-300 font-semibold hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleDelete}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition"
          >
            {loading ? "Deleting..." : "Delete"}
          </button>
        </div>
      </div>
    </div>
  )
}

ConfirmDeleteModal.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.string.isRequired,
    email: PropTypes.string.isRequired,
    full_name: PropTypes.string,
  }).isRequired,
  onClose: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
}
