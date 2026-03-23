import { useMemo, useState } from "react"
import { AlertCircle, Plus, Search, RotateCcw } from "lucide-react"

import AppLayout from "../../components/layout/AppLayout"
import { useToast } from "../../hooks/useToast"
import { useManagement } from "../../hooks/useManagement"
import { getApiErrorMessage } from "../../utils/apiError"

import ServiceTable from "../../components/admin/management/ServiceTable"
import CampaignTable from "../../components/admin/management/CampaignTable"
import ServiceModal from "../../components/admin/management/ServiceModal"
import CampaignModal from "../../components/admin/management/CampaignModal"
import DeleteConfirmModal from "../../components/admin/management/DeleteConfirmModal"

function TabButton({ active, icon, label, count, onClick }) {
  const Icon = icon
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-3 py-2 text-sm font-semibold border-b-2 transition ${
        active ? "border-violet-500 text-white" : "border-transparent text-slate-400 hover:text-slate-200"
      }`}
    >
      <Icon size={16} />
      {label}
      <span className="ml-1 text-xs px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-200">
        {count}
      </span>
    </button>
  )
}

export default function ManagementPage() {
  const { showToast, Toast } = useToast()
  const {
    services,
    campaigns,
    loading,
    error,
    refetch,
    createService,
    updateService,
    deleteService,
    createCampaign,
    updateCampaign,
    deleteCampaign,
  } = useManagement()

  const [tab, setTab] = useState("services") // services | campaigns
  const [search, setSearch] = useState("")

  const [serviceModalOpen, setServiceModalOpen] = useState(false)
  const [serviceModalMode, setServiceModalMode] = useState("add")
  const [serviceEditing, setServiceEditing] = useState(null)

  const [campaignModalOpen, setCampaignModalOpen] = useState(false)
  const [campaignModalMode, setCampaignModalMode] = useState("add")
  const [campaignEditing, setCampaignEditing] = useState(null)

  const [deleteOpen, setDeleteOpen] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [deleteContext, setDeleteContext] = useState(null) // { type, item }

  const filteredServices = useMemo(() => {
    const s = search.trim().toLowerCase()
    if (!s) return services
    return (services ?? []).filter((r) => (r.name ?? "").toLowerCase().includes(s))
  }, [services, search])

  const filteredCampaigns = useMemo(() => {
    const s = search.trim().toLowerCase()
    if (!s) return campaigns
    return (campaigns ?? []).filter((r) =>
      `${r.name ?? ""} ${r.service_name ?? ""}`.toLowerCase().includes(s)
    )
  }, [campaigns, search])

  const openAddService = () => {
    setServiceModalMode("add")
    setServiceEditing(null)
    setServiceModalOpen(true)
  }
  const openEditService = (row) => {
    setServiceModalMode("edit")
    setServiceEditing(row)
    setServiceModalOpen(true)
  }

  const openAddCampaign = () => {
    setCampaignModalMode("add")
    setCampaignEditing(null)
    setCampaignModalOpen(true)
  }
  const openEditCampaign = (row) => {
    setCampaignModalMode("edit")
    setCampaignEditing(row)
    setCampaignModalOpen(true)
  }

  const confirmDelete = (type, item) => {
    setDeleteContext({ type, item })
    setDeleteOpen(true)
  }

  const doDelete = async () => {
    if (!deleteContext) return
    setDeleteLoading(true)
    try {
      if (deleteContext.type === "service") {
        await deleteService(deleteContext.item.id)
        showToast("Service deleted successfully", "success")
      } else {
        await deleteCampaign(deleteContext.item.id)
        showToast("Campaign deleted successfully", "success")
      }
      setDeleteOpen(false)
      setDeleteContext(null)
    } catch (err) {
      showToast(getApiErrorMessage(err, "Delete failed"), "error")
    } finally {
      setDeleteLoading(false)
    }
  }

  const headerSubtitle = "Manage services and campaigns"

  return (
    <AppLayout pageTitle="Management">
      <div className="space-y-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-100 mb-2">Management</h1>
            <p className="text-sm text-slate-400">{headerSubtitle}</p>
          </div>
          <button
            onClick={refetch}
            className="flex items-center gap-2 px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-lg transition"
          >
            <RotateCcw size={14} />
            Refresh
          </button>
        </div>

        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-5">
          {/* Tabs */}
          <div className="flex items-center justify-between gap-4 border-b border-slate-700/50 pb-2">
            <div className="flex items-center gap-4">
              <TabButton
                active={tab === "services"}
                icon={() => <span>🏢</span>}
                label="Services"
                count={services.length}
                onClick={() => { setTab("services"); setSearch("") }}
              />
              <TabButton
                active={tab === "campaigns"}
                icon={() => <span>📣</span>}
                label="Campaigns"
                count={campaigns.length}
                onClick={() => { setTab("campaigns"); setSearch("") }}
              />
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
              <p className="flex-1 text-sm text-red-200">{error}</p>
              <button
                onClick={refetch}
                className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
              >
                <RotateCcw size={14} /> Retry
              </button>
            </div>
          )}

          {/* Toolbar */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex-1 min-w-[220px] relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search..."
                className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-100 focus:outline-none focus:border-violet-500"
              />
            </div>

            {tab === "services" ? (
              <button
                onClick={openAddService}
                className="flex items-center gap-2 px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold rounded-lg transition"
              >
                <Plus size={16} /> Add Service
              </button>
            ) : (
              <button
                onClick={openAddCampaign}
                className="flex items-center gap-2 px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold rounded-lg transition"
              >
                <Plus size={16} /> Add Campaign
              </button>
            )}
          </div>

          {/* Content */}
          {loading ? (
            <div className="space-y-3">
              <div className="h-10 bg-slate-800 animate-pulse rounded-lg border border-slate-700" />
              <div className="h-64 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
            </div>
          ) : tab === "services" ? (
            <ServiceTable
              rows={filteredServices}
              onEdit={openEditService}
              onDelete={(row) => confirmDelete("service", row)}
            />
          ) : (
            <CampaignTable
              rows={filteredCampaigns}
              onEdit={openEditCampaign}
              onDelete={(row) => confirmDelete("campaign", row)}
            />
          )}
        </div>

        {/* Modals */}
        <ServiceModal
          open={serviceModalOpen}
          mode={serviceModalMode}
          initialValue={serviceEditing}
          onClose={() => setServiceModalOpen(false)}
          onSave={async (payload) => {
            try {
              if (serviceModalMode === "add") {
                await createService(payload)
                showToast("Service created successfully", "success")
              } else {
                await updateService(serviceEditing.id, payload)
                showToast("Service updated successfully", "success")
              }
            } catch (err) {
              showToast(getApiErrorMessage(err, "Save failed"), "error")
              // Let the modal display the error without throwing
            }
          }}
        />

        <CampaignModal
          open={campaignModalOpen}
          mode={campaignModalMode}
          initialValue={campaignEditing}
          services={services}
          onClose={() => setCampaignModalOpen(false)}
          onSave={async (payload) => {
            try {
              if (campaignModalMode === "add") {
                await createCampaign(payload)
                showToast("Campaign created successfully", "success")
              } else {
                await updateCampaign(campaignEditing.id, payload)
                showToast("Campaign updated successfully", "success")
              }
            } catch (err) {
              showToast(getApiErrorMessage(err, "Save failed"), "error")
              // Let the modal display the error without throwing
            }
          }}
        />

        <DeleteConfirmModal
          open={deleteOpen}
          title="Confirm deletion"
          message={
            deleteContext
              ? `Are you sure you want to delete ${deleteContext.item.name}? This action cannot be undone.`
              : ""
          }
          onCancel={() => { setDeleteOpen(false); setDeleteContext(null) }}
          onConfirm={doDelete}
          loading={deleteLoading}
        />

        {Toast}
      </div>
    </AppLayout>
  )
}
