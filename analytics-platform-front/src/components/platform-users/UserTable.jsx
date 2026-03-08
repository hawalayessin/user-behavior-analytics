import PropTypes from "prop-types"
import { Pencil, Ban, CheckCircle, Trash2 } from "lucide-react"
import { useAuth } from "../../context/AuthContext"

const UserTable = ({
  users,
  loading,
  onEdit,
  onToggleStatus,
  onDelete,
  page,
  total,
  limit,
  onPageChange,
}) => {
  const { role: currentRole, access_token } = useAuth()
  const currentUserId = localStorage.getItem("user_id")

  if (loading) {
    return (
      <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-800/50 border-b border-slate-800">
            <tr>
              <th className="text-left px-6 py-4 text-xs uppercase text-slate-500 tracking-widest font-semibold">
                Utilisateur
              </th>
              <th className="text-left px-6 py-4 text-xs uppercase text-slate-500 tracking-widest font-semibold">
                Contact
              </th>
              <th className="text-left px-6 py-4 text-xs uppercase text-slate-500 tracking-widest font-semibold">
                Rôle
              </th>
              <th className="text-left px-6 py-4 text-xs uppercase text-slate-500 tracking-widest font-semibold">
                Statut
              </th>
              <th className="text-left px-6 py-4 text-xs uppercase text-slate-500 tracking-widest font-semibold">
                Dernière Connexion
              </th>
              <th className="text-center px-6 py-4 text-xs uppercase text-slate-500 tracking-widest font-semibold">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {[1, 2, 3, 4, 5].map((i) => (
              <tr key={i} className="border-b border-slate-800">
                <td colSpan="6" className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-slate-700 animate-pulse"></div>
                    <div className="flex-1">
                      <div className="h-4 bg-slate-700 rounded animate-pulse mb-2"></div>
                      <div className="h-3 bg-slate-700 rounded animate-pulse w-2/3"></div>
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  if (users.length === 0) {
    return (
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-12 text-center">
        <p className="text-slate-400 mb-2">No users found</p>
        <p className="text-sm text-slate-500">Try adjusting your search or filters</p>
      </div>
    )
  }

  const totalPages = Math.ceil(total / limit)
  const startIndex = (page - 1) * limit + 1
  const endIndex = Math.min(page * limit, total)

  return (
    <div className="space-y-4">
      <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-800/50 border-b border-slate-800">
            <tr>
              <th className="text-left px-6 py-4 text-xs uppercase text-slate-500 tracking-widest font-semibold">
                Utilisateur
              </th>
              <th className="text-left px-6 py-4 text-xs uppercase text-slate-500 tracking-widest font-semibold">
                Contact
              </th>
              <th className="text-left px-6 py-4 text-xs uppercase text-slate-500 tracking-widest font-semibold">
                Rôle
              </th>
              <th className="text-left px-6 py-4 text-xs uppercase text-slate-500 tracking-widest font-semibold">
                Statut
              </th>
              <th className="text-left px-6 py-4 text-xs uppercase text-slate-500 tracking-widest font-semibold">
                Dernière Connexion
              </th>
              <th className="text-center px-6 py-4 text-xs uppercase text-slate-500 tracking-widest font-semibold">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => {
              const isOwnAccount = user.id === currentUserId
              const initials = user.full_name
                ? user.full_name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .toUpperCase()
                : "?"

              return (
                <tr key={user.id} className="border-b border-slate-800 hover:bg-slate-800/40 transition">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-indigo-600 flex items-center justify-center text-sm font-bold text-white">
                        {initials}
                      </div>
                      <span className="text-sm font-semibold text-slate-100">
                        {user.full_name || "—"}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-slate-400">{user.email}</span>
                  </td>
                  <td className="px-6 py-4">
                    <RoleBadge role={user.role} />
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge isActive={user.is_active} />
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-slate-400">
                      {formatLastLogin(user.last_login_at)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-center gap-2">
                      <button
                        onClick={() => onEdit(user)}
                        className="p-1.5 text-slate-400 hover:text-indigo-400 transition"
                        title="Edit user"
                      >
                        <Pencil size={16} />
                      </button>
                      <button
                        onClick={() => onToggleStatus(user)}
                        disabled={isOwnAccount}
                        className={`p-1.5 transition ${
                          isOwnAccount
                            ? "text-slate-600 cursor-not-allowed opacity-50"
                            : user.is_active
                              ? "text-slate-400 hover:text-red-400"
                              : "text-slate-400 hover:text-emerald-400"
                        }`}
                        title={isOwnAccount ? "Cannot modify your own account" : "Toggle status"}
                      >
                        {user.is_active ? <Ban size={16} /> : <CheckCircle size={16} />}
                      </button>
                      <button
                        onClick={() => onDelete(user)}
                        disabled={isOwnAccount}
                        className={`p-1.5 transition ${
                          isOwnAccount
                            ? "text-slate-600 cursor-not-allowed opacity-50"
                            : "text-slate-400 hover:text-red-500"
                        }`}
                        title={isOwnAccount ? "Cannot delete your own account" : "Delete user"}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between text-sm text-slate-500">
        <span>
          Showing {startIndex}–{endIndex} of {total} users
        </span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => onPageChange(Math.max(1, page - 1))}
            disabled={page === 1}
            className="px-3 py-1 rounded hover:bg-slate-800 transition disabled:opacity-40 disabled:cursor-not-allowed text-slate-400"
          >
            ← Prev
          </button>
          {Array.from({ length: totalPages }, (_, i) => i + 1)
            .filter((p) => Math.abs(p - page) <= 1 || p === 1 || p === totalPages)
            .map((p, idx, arr) => {
              if (idx > 0 && arr[idx - 1] !== p - 1) {
                return (
                  <span key={`dots-${p}`} className="px-1 text-slate-500">
                    ...
                  </span>
                )
              }
              return (
                <button
                  key={p}
                  onClick={() => onPageChange(p)}
                  className={`px-3 py-1 rounded transition ${
                    page === p
                      ? "bg-indigo-600 text-white"
                      : "text-slate-400 hover:bg-slate-800"
                  }`}
                >
                  {p}
                </button>
              )
            })}
          <button
            onClick={() => onPageChange(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
            className="px-3 py-1 rounded hover:bg-slate-800 transition disabled:opacity-40 disabled:cursor-not-allowed text-slate-400"
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  )
}

const RoleBadge = ({ role }) => {
  const styles = {
    admin: "bg-indigo-500/20 text-indigo-400 border-indigo-500/30",
    analyst: "bg-slate-700 text-slate-300 border-slate-600",
    viewer: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold uppercase border ${
        styles[role] || styles.viewer
      }`}
    >
      {role}
    </span>
  )
}

const StatusBadge = ({ isActive }) => {
  if (isActive) {
    return <span className="text-sm text-emerald-400 flex items-center gap-1.5">● ACTIVE</span>
  }
  return <span className="text-sm text-slate-500 flex items-center gap-1.5">● INACTIVE</span>
}

const formatLastLogin = (datetime) => {
  if (!datetime) return <span className="italic text-slate-500">Never</span>

  const date = new Date(datetime)
  const now = new Date()
  const seconds = Math.floor((now - date) / 1000)

  if (seconds < 60) return "Just now"
  if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`
  if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`

  return date.toLocaleDateString("fr-FR", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

UserTable.propTypes = {
  users: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      email: PropTypes.string.isRequired,
      full_name: PropTypes.string,
      role: PropTypes.oneOf(["admin", "analyst", "viewer"]).isRequired,
      is_active: PropTypes.bool.isRequired,
      last_login_at: PropTypes.string,
    })
  ).isRequired,
  loading: PropTypes.bool.isRequired,
  onEdit: PropTypes.func.isRequired,
  onToggleStatus: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  page: PropTypes.number.isRequired,
  total: PropTypes.number.isRequired,
  limit: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
}

export default UserTable
