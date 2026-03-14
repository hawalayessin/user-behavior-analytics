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
  const { userId: currentUserId } = useAuth()

  /* ───────────────── LOADING ───────────────── */
  if (loading) {
    return (
      <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-800/50 border-b border-slate-800">
            <tr>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase">Utilisateur</th>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase">Contact</th>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase">Rôle</th>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase">Statut</th>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase">Dernière Connexion</th>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase">Campaign</th>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            {[1,2,3,4,5].map((i)=>(
              <tr key={i} className="border-b border-slate-800">
                <td colSpan="7" className="px-6 py-4">
                  <div className="h-4 bg-slate-700 rounded animate-pulse w-2/3"></div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  /* ───────────────── EMPTY ───────────────── */
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
  const endIndex   = Math.min(page * limit, total)

  /* ───────────────── TABLE ───────────────── */
  return (
    <div className="space-y-4">
      <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
        <table className="w-full">

          {/* HEADER */}
          <thead className="bg-slate-800/50 border-b border-slate-800">
            <tr>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase">Utilisateur</th>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase">Contact</th>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase">Rôle</th>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase">Statut</th>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase">Dernière Connexion</th>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase">Campaign</th>
              <th className="px-6 py-4 text-xs text-slate-500 uppercase text-center">Actions</th>
            </tr>
          </thead>

          {/* BODY */}
          <tbody>
            {users.map((user) => {

              const isOwnAccount = user.id === currentUserId
              const initials = user.full_name
                ? user.full_name.split(" ").map((n)=>n[0]).join("").toUpperCase()
                : "?"

              return (
                <tr key={user.id} className="border-b border-slate-800 hover:bg-slate-800/40">

                  {/* USER */}
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

                  {/* CONTACT */}
                  <td className="px-6 py-4 text-sm text-slate-400">
                    {user.email}
                  </td>

                  {/* ROLE */}
                  <td className="px-6 py-4">
                    <RoleBadge role={user.role} />
                  </td>

                  {/* STATUS */}
                  <td className="px-6 py-4">
                    <StatusBadge isActive={user.is_active} />
                  </td>

                  {/* LAST LOGIN */}
                  <td className="px-6 py-4 text-sm text-slate-400">
                    {formatLastLogin(user.last_login_at)}
                  </td>

                  {/* ✅ CAMPAIGN */}
                  <td className="px-6 py-4 text-xs">
                    {user.campaign_name ? (
                      <span className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/30 text-[10px] max-w-[120px] truncate inline-block">
                        {user.campaign_name}
                      </span>
                    ) : (
                      <span className="text-slate-500">—</span>
                    )}
                  </td>

                  {/* ACTIONS */}
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-center gap-2">

                      <button onClick={()=>onEdit(user)}
                        className="p-1.5 text-slate-400 hover:text-indigo-400">
                        <Pencil size={16}/>
                      </button>

                      <button onClick={()=>onToggleStatus(user)}
                        disabled={isOwnAccount}
                        className={`p-1.5 ${
                          isOwnAccount
                            ? "text-slate-600 cursor-not-allowed"
                            : user.is_active
                              ? "hover:text-red-400"
                              : "hover:text-emerald-400"
                        }`}>
                        {user.is_active ? <Ban size={16}/> : <CheckCircle size={16}/>}
                      </button>

                      <button onClick={()=>onDelete(user)}
                        disabled={isOwnAccount}
                        className={`p-1.5 ${
                          isOwnAccount
                            ? "text-slate-600 cursor-not-allowed"
                            : "hover:text-red-500"
                        }`}>
                        <Trash2 size={16}/>
                      </button>

                    </div>
                  </td>

                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* PAGINATION */}
      <div className="flex items-center justify-between text-sm text-slate-500">
        <span>
          Showing {startIndex}–{endIndex} of {total} users
        </span>

        <div className="flex gap-1">
          <button onClick={()=>onPageChange(Math.max(1,page-1))}
            disabled={page===1}
            className="px-3 py-1 rounded hover:bg-slate-800 disabled:opacity-40">
            ← Prev
          </button>

          <button onClick={()=>onPageChange(Math.min(totalPages,page+1))}
            disabled={page===totalPages}
            className="px-3 py-1 rounded hover:bg-slate-800 disabled:opacity-40">
            Next →
          </button>
        </div>
      </div>
    </div>
  )
}

/* ───────────────── BADGES ───────────────── */

const RoleBadge = ({ role }) => {
  const styles = {
    admin:   "bg-indigo-500/20 text-indigo-400 border-indigo-500/30",
    analyst: "bg-slate-700 text-slate-300 border-slate-600",
    viewer:  "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  }

  return (
    <span className={`px-2 py-0.5 rounded text-xs border ${styles[role] || styles.viewer}`}>
      {role}
    </span>
  )
}

const StatusBadge = ({ isActive }) => (
  isActive
    ? <span className="text-sm text-emerald-400">● ACTIVE</span>
    : <span className="text-sm text-slate-500">● INACTIVE</span>
)

const formatLastLogin = (datetime) => {
  if (!datetime) return "Never"
  return new Date(datetime).toLocaleDateString("fr-FR")
}

UserTable.propTypes = {
  users: PropTypes.array.isRequired,
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