import React, { useCallback, useEffect, useMemo, useState } from "react";
import AppLayout from "../components/layout/AppLayout";
import NotePanel from "../components/notes/NotePanel";
import NotesList from "../components/notes/NotesList";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../hooks/useToast";

export default function NotesPage() {
  const { role } = useAuth();
  const { showToast, Toast } = useToast();

  const [notes, setNotes] = useState([]);
  const [services, setServices] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(false);

  const [panelOpen, setPanelOpen] = useState(false);
  const [editingNote, setEditingNote] = useState(null);

  const [filters, setFilters] = useState({
    service_id: "",
    metric: "",
    period_start: "",
    period_end: "",
    analyst_id: "",
  });

  const analystOptions = useMemo(() => {
    const map = new Map();
    notes.forEach((note) => {
      if (!note.analyst_id) return;
      if (!map.has(note.analyst_id)) {
        map.set(note.analyst_id, note.analyst_name || "Unknown");
      }
    });
    return Array.from(map.entries()).map(([id, name]) => ({ id, name }));
  }, [notes]);

  const fetchServices = useCallback(async () => {
    try {
      const res = await api.get("/services");
      setServices(res.data || []);
    } catch {
      showToast("Failed to load services", "error");
    }
  }, [showToast]);

  const fetchCampaigns = useCallback(async () => {
    try {
      const res = await api.get("/analytics/campaigns/list", {
        params: { page: 1, limit: 200 },
      });
      setCampaigns(res.data?.campaigns || []);
    } catch {
      setCampaigns([]);
    }
  }, []);

  const fetchNotes = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.service_id) params.service_id = filters.service_id;
      if (filters.metric) params.metric = filters.metric;
      if (filters.period_start) params.period_start = filters.period_start;
      if (filters.period_end) params.period_end = filters.period_end;
      if (role === "admin" && filters.analyst_id) {
        params.analyst_id = filters.analyst_id;
      }

      const res = await api.get("/notes", { params });
      setNotes(res.data || []);
    } catch (err) {
      showToast("Failed to load notes", "error");
    } finally {
      setLoading(false);
    }
  }, [filters, role, showToast]);

  useEffect(() => {
    fetchServices();
    fetchCampaigns();
  }, [fetchServices, fetchCampaigns]);

  useEffect(() => {
    fetchNotes();
  }, [fetchNotes]);

  const handleSubmit = async (payload) => {
    try {
      if (editingNote) {
        await api.put(`/notes/${editingNote.id}`, payload);
        showToast("Note updated", "success");
      } else {
        await api.post("/notes", payload);
        showToast("Note created", "success");
      }
      setPanelOpen(false);
      setEditingNote(null);
      fetchNotes();
    } catch (err) {
      showToast(err.response?.data?.detail || "Failed to save note", "error");
    }
  };

  const handleDelete = async (note) => {
    try {
      await api.delete(`/notes/${note.id}`);
      showToast("Note deleted", "success");
      fetchNotes();
    } catch (err) {
      showToast(err.response?.data?.detail || "Failed to delete note", "error");
    }
  };

  return (
    <AppLayout pageTitle="Analyst Notes">
      <div className="space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-3xl font-bold text-slate-100 mb-2">
              Analyst Notes
            </h1>
            <p className="text-sm text-slate-400">
              Capture analytical context for reports and dashboards.
            </p>
          </div>
          <button
            onClick={() => {
              setEditingNote(null);
              setPanelOpen(true);
            }}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold"
          >
            📝 Add Note
          </button>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4 grid grid-cols-1 md:grid-cols-4 gap-3">
          <select
            value={filters.service_id}
            onChange={(e) =>
              setFilters((prev) => ({ ...prev, service_id: e.target.value }))
            }
            className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
          >
            <option value="">All services</option>
            {services.map((service) => (
              <option key={service.id} value={service.id}>
                {service.name}
              </option>
            ))}
          </select>

          <select
            value={filters.metric}
            onChange={(e) =>
              setFilters((prev) => ({ ...prev, metric: e.target.value }))
            }
            className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
          >
            <option value="">All metrics</option>
            <option value="DAU">DAU</option>
            <option value="MAU">MAU</option>
            <option value="WAU">WAU</option>
            <option value="Churn">Churn</option>
            <option value="MRR">MRR</option>
            <option value="Conversion Rate">Conversion Rate</option>
          </select>

          <input
            type="date"
            value={filters.period_start}
            onChange={(e) =>
              setFilters((prev) => ({ ...prev, period_start: e.target.value }))
            }
            className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
          />
          <input
            type="date"
            value={filters.period_end}
            onChange={(e) =>
              setFilters((prev) => ({ ...prev, period_end: e.target.value }))
            }
            className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
          />
        </div>

        {loading ? (
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6 text-slate-400">
            Loading notes...
          </div>
        ) : (
          <NotesList
            notes={notes}
            role={role}
            onEdit={(note) => {
              setEditingNote(note);
              setPanelOpen(true);
            }}
            onDelete={handleDelete}
            analystFilter={filters.analyst_id}
            analystOptions={analystOptions}
            onAnalystFilter={(value) =>
              setFilters((prev) => ({ ...prev, analyst_id: value }))
            }
          />
        )}
      </div>

      <NotePanel
        open={panelOpen}
        onClose={() => setPanelOpen(false)}
        onSubmit={handleSubmit}
        services={services}
        campaigns={campaigns}
        initialNote={editingNote}
      />

      {Toast}
    </AppLayout>
  );
}
