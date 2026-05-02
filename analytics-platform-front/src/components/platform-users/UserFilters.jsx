import React from "react"
import PropTypes from "prop-types"
import { Search } from "lucide-react"

export default function UserFilters({
  search,
  onSearchChange,
  onClearSearch,
  roleFilter,
  onRoleFilter,
  statusFilter,
  onStatusFilter,
}) {
  return (
    <div className="flex flex-col lg:flex-row lg:items-center gap-4 bg-slate-900/50 p-4 rounded-lg border border-slate-800">
      {/* Search Input */}
      <div className="flex-1 relative group">
        <Search
          size={18}
          className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500 group-focus-within:text-violet-400 transition-colors"
        />
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search by name or email..."
          className="w-full h-10 pl-10 pr-10 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/40 focus:border-violet-500 transition"
        />
        {search && (
          <button
            type="button"
            onClick={onClearSearch}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-2 py-1 text-xs rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition"
          >
            Clear
          </button>
        )}
      </div>

      {/* Role Filter Tabs */}
      <div className="flex items-center gap-1 bg-slate-800/50 p-1 rounded-lg">
        {["all", "admin", "analyst", "viewer"].map((role) => (
          <button
            key={role}
            onClick={() => onRoleFilter(role)}
            className={`px-3 py-1.5 rounded transition ${
              roleFilter === role
                ? "bg-violet-600 text-white"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {role === "all" ? "All" : role.charAt(0).toUpperCase() + role.slice(1)}
          </button>
        ))}
      </div>

      {/* Status Dropdown */}
      <select
        value={statusFilter}
        onChange={(e) => onStatusFilter(e.target.value)}
        className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/40 focus:border-violet-500 transition"
      >
        <option value="all">All Status</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>
    </div>
  )
}

UserFilters.propTypes = {
  search: PropTypes.string.isRequired,
  onSearchChange: PropTypes.func.isRequired,
  onClearSearch: PropTypes.func.isRequired,
  roleFilter: PropTypes.string.isRequired,
  onRoleFilter: PropTypes.func.isRequired,
  statusFilter: PropTypes.string.isRequired,
  onStatusFilter: PropTypes.func.isRequired,
}
