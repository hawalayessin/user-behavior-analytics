import React, { useState, useEffect, useCallback } from "react"
import PropTypes from "prop-types"
import { UserPlus } from "lucide-react"
import api from "../../services/api"
import { useAuth } from "../../context/AuthContext"
import { useToast } from "../../hooks/useToast"
import AppLayout from "../../components/layout/AppLayout"
import UserTable from "../../components/platform-users/UserTable"
import UserFilters from "../../components/platform-users/UserFilters"
import UserKPICards from "../../components/platform-users/UserKPICards"
import CreateUserModal from "../../components/platform-users/CreateUserModal"
import EditUserModal from "../../components/platform-users/EditUserModal"
import ConfirmDeleteModal from "../../components/platform-users/ConfirmDeleteModal"

const DEBOUNCE_DELAY = 400
const PAGE_LIMIT = 20

export default function PlatformUsersPage() {
  const { role: currentRole } = useAuth()
  const { showToast, Toast } = useToast()

  // ── Table state ────────────────────────────────────────────
  const [users, setUsers]               = useState([])
  const [total, setTotal]               = useState(0)
  const [loading, setLoading]           = useState(false)
  const [search, setSearch]             = useState("")
  const [roleFilter, setRoleFilter]     = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [page, setPage]                 = useState(1)

  // ── Modal state ────────────────────────────────────────────
  const [selectedUser, setSelectedUser]       = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal]     = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  // ── KPI state ──────────────────────────────────────────────
  const [statsData, setStatsData] = useState({
    total: 0,
    administrators: 0,
    activeNow: 0,
    inactiveAccounts: 0,
  })

  // ── Fetch table data ───────────────────────────────────────
  const fetchUsers = useCallback(async (skip, limit, searchQuery, role, activeStatus) => {
    setLoading(true)
    try {
      const params = { skip, limit }
      if (searchQuery)          params.search    = searchQuery
      if (role !== "all")       params.role      = role
      if (activeStatus !== "all") params.is_active = activeStatus === "active"

      const res = await api.get("/platform-users/", { params })
      setUsers(res.data.items ?? [])
      setTotal(res.data.total ?? 0)
    } catch (err) {
      console.error("fetchUsers error:", err)
      showToast("Failed to load users", "error")
    } finally {
      setLoading(false)
    }
  }, [showToast])

  // ── Fetch KPI stats (no filters) ───────────────────────────
  const fetchStats = useCallback(async () => {
    try {
      const res = await api.get("/platform-users/", {
        params: { skip: 0, limit: 500 },
      })
      const items = res.data.items ?? []
      setStatsData({
        total:            res.data.total ?? items.length,
        administrators:   items.filter((u) => u.role === "admin").length,
        activeNow:        items.filter((u) => u.is_active === true).length,
        inactiveAccounts: items.filter((u) => u.is_active === false).length,
      })
    } catch (err) {
      console.error("fetchStats error:", err)
    }
  }, [])

  // ── Debounced table fetch ──────────────────────────────────
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchUsers((page - 1) * PAGE_LIMIT, PAGE_LIMIT, search, roleFilter, statusFilter)
    }, DEBOUNCE_DELAY)
    return () => clearTimeout(timer)
  }, [search, roleFilter, statusFilter, page, fetchUsers])

  // ── Stats on mount ─────────────────────────────────────────
  useEffect(() => {
    fetchStats()
  }, [fetchStats])

  // ── Refresh both table + stats ─────────────────────────────
  const refreshAll = useCallback(async (targetPage = page) => {
    await Promise.all([
      fetchUsers((targetPage - 1) * PAGE_LIMIT, PAGE_LIMIT, search, roleFilter, statusFilter),
      fetchStats(),
    ])
  }, [fetchUsers, fetchStats, page, search, roleFilter, statusFilter])

  // ── Filter handlers ────────────────────────────────────────
  const handleSearchChange = (value) => { setSearch(value); setPage(1) }
  const handleRoleFilter   = (role)  => { setRoleFilter(role); setPage(1) }
  const handleStatusFilter = (s)     => { setStatusFilter(s); setPage(1) }
  const handlePageChange   = (p)     => setPage(p)

  // ── Modal open handlers ────────────────────────────────────
  const handleCreateClick = ()     => setShowCreateModal(true)
  const handleEditClick   = (user) => { setSelectedUser(user); setShowEditModal(true) }
  const handleDeleteClick = (user) => { setSelectedUser(user); setShowDeleteModal(true) }

  // ── Status toggle ──────────────────────────────────────────
  const handleToggleStatus = async (user) => {
    try {
      await api.patch(`/platform-users/${user.id}/status`, {
        is_active: !user.is_active,
      })
      showToast(`User ${!user.is_active ? "activated" : "deactivated"}`, "success")
      refreshAll()
    } catch (err) {
      console.error("Toggle status error:", err)
      showToast("Failed to update user status", "error")
    }
  }

  // ── Modal success handlers ─────────────────────────────────
  const handleCreateSuccess = () => {
    setShowCreateModal(false)
    setPage(1)
    refreshAll(1)
    showToast("User created successfully", "success")
  }

  const handleEditSuccess = () => {
    setShowEditModal(false)
    setSelectedUser(null)
    refreshAll()
    showToast("User updated successfully", "success")
  }

  const handleDeleteSuccess = () => {
    setShowDeleteModal(false)
    setSelectedUser(null)
    setPage(1)
    refreshAll(1)
    showToast("User deleted successfully", "success")
  }

  // ── Render ─────────────────────────────────────────────────
  return (
    <AppLayout pageTitle="Platform Users" hasNotifications={false} showExportButton={false}>
      <div className="max-w-full">

        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-100 mb-1">Platform Users</h1>
            <p className="text-slate-400">Manage dashboard access and roles</p>
          </div>
          {currentRole === "admin" && (
            <button
              onClick={handleCreateClick}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition"
            >
              <UserPlus size={18} />
              Create Account
            </button>
          )}
        </div>

        {/* KPI Cards */}
        <UserKPICards
          total={statsData.total}
          administrators={statsData.administrators}
          activeNow={statsData.activeNow}
          inactiveAccounts={statsData.inactiveAccounts}
        />

        {/* Filters */}
        <div className="mt-8">
          <UserFilters
            search={search}
            onSearchChange={handleSearchChange}
            roleFilter={roleFilter}
            onRoleFilter={handleRoleFilter}
            statusFilter={statusFilter}
            onStatusFilter={handleStatusFilter}
          />
        </div>

        {/* Table */}
        <div className="mt-6 mb-8">
          <UserTable
            users={users}
            loading={loading}
            onEdit={handleEditClick}
            onToggleStatus={handleToggleStatus}
            onDelete={handleDeleteClick}
            page={page}
            total={total}
            limit={PAGE_LIMIT}
            onPageChange={handlePageChange}
          />
        </div>

        {/* Modals */}
        {showCreateModal && (
          <CreateUserModal
            onClose={() => setShowCreateModal(false)}
            onSuccess={handleCreateSuccess}
          />
        )}

        {showEditModal && selectedUser && (
          <EditUserModal
            user={selectedUser}
            onClose={() => { setShowEditModal(false); setSelectedUser(null) }}
            onSuccess={handleEditSuccess}
          />
        )}

        {showDeleteModal && selectedUser && (
          <ConfirmDeleteModal
            user={selectedUser}
            onClose={() => { setShowDeleteModal(false); setSelectedUser(null) }}
            onSuccess={handleDeleteSuccess}
          />
        )}
      </div>

      {Toast}
    </AppLayout>
  )
}

PlatformUsersPage.propTypes = {}