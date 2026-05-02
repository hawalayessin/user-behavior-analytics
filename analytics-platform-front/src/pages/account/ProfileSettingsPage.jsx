import React, { useEffect, useMemo, useRef, useState } from "react";
import AppLayout from "../../components/layout/AppLayout";
import api from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { useToast } from "../../hooks/useToast";

const DEFAULT_PREFS = {
  emailNotifications: true,
};

export default function ProfileSettingsPage() {
  const { updateProfile } = useAuth();
  const { showToast, Toast } = useToast();

  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState({
    full_name: "",
    email: "",
    avatar_url: null,
  });
  const [fullName, setFullName] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [prefs, setPrefs] = useState(DEFAULT_PREFS);
  const [saving, setSaving] = useState(false);
  const [avatarUploading, setAvatarUploading] = useState(false);
  const fileInputRef = useRef(null);
  const [avatarPreviewUrl, setAvatarPreviewUrl] = useState(null);

  useEffect(() => {
    const stored = window.localStorage.getItem("profile_settings_v1");
    if (stored) {
      try {
        setPrefs({ ...DEFAULT_PREFS, ...JSON.parse(stored) });
      } catch {
        setPrefs(DEFAULT_PREFS);
      }
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    const fetchProfile = async () => {
      try {
        const response = await api.get("/auth/me");
        if (!isMounted) return;
        setProfile(response.data);
        setFullName(response.data.full_name || "");
      } catch (err) {
        showToast("Failed to load profile", "error");
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchProfile();
    return () => {
      isMounted = false;
    };
  }, [showToast]);

  const initials = useMemo(() => {
    if (!fullName && !profile.full_name) return "?";
    return (fullName || profile.full_name)
      .split(" ")
      .map((part) => part[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  }, [fullName, profile.full_name]);

  const username = useMemo(() => {
    if (!profile.email) return "user";
    return profile.email.split("@")[0];
  }, [profile.email]);

  const apiBase = import.meta.env.VITE_API_URL || "/api";
  const avatarUrl = profile.avatar_url
    ? profile.avatar_url.startsWith("http")
      ? profile.avatar_url
      : `${apiBase}${profile.avatar_url}`
    : null;
  const displayAvatarUrl = avatarPreviewUrl || avatarUrl;

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);

    if (newPassword || confirmPassword || currentPassword) {
      if (!currentPassword) {
        showToast("Current password is required", "error");
        setSaving(false);
        return;
      }
      if (!newPassword || newPassword.length < 8) {
        showToast("New password must be at least 8 characters", "error");
        setSaving(false);
        return;
      }
      if (newPassword !== confirmPassword) {
        showToast("Passwords do not match", "error");
        setSaving(false);
        return;
      }
    }

    try {
      const payload = {
        full_name: fullName.trim() || null,
      };

      if (newPassword) {
        payload.current_password = currentPassword;
        payload.new_password = newPassword;
      }

      const response = await api.patch("/auth/profile", payload);
      setProfile(response.data);
      updateProfile(response.data.full_name || "");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      showToast("Profile updated", "success");
    } catch (err) {
      showToast(
        err.response?.data?.detail || "Failed to update profile",
        "error",
      );
    } finally {
      setSaving(false);
    }
  };

  const handleDiscard = () => {
    setFullName(profile.full_name || "");
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    showToast("Changes discarded", "info");
  };

  const handlePrefChange = (key, value) => {
    const next = { ...prefs, [key]: value };
    setPrefs(next);
    window.localStorage.setItem("profile_settings_v1", JSON.stringify(next));
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleAvatarChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const objectUrl = URL.createObjectURL(file);
    setAvatarPreviewUrl(objectUrl);

    const formData = new FormData();
    formData.append("file", file);

    setAvatarUploading(true);
    try {
      const response = await api.post("/auth/profile/avatar", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setProfile(response.data);
      setAvatarPreviewUrl(null);
      showToast("Photo updated", "success");
    } catch (err) {
      setAvatarPreviewUrl(null);
      showToast(
        err.response?.data?.detail || "Failed to upload photo",
        "error",
      );
    } finally {
      URL.revokeObjectURL(objectUrl);
      setAvatarUploading(false);
      event.target.value = "";
    }
  };

  const handleAvatarRemove = async () => {
    setAvatarUploading(true);
    try {
      const response = await api.delete("/auth/profile/avatar");
      setProfile(response.data);
      setAvatarPreviewUrl(null);
      showToast("Photo removed", "success");
    } catch (err) {
      setAvatarPreviewUrl(null);
      showToast(
        err.response?.data?.detail || "Failed to remove photo",
        "error",
      );
    } finally {
      setAvatarUploading(false);
    }
  };

  return (
    <AppLayout pageTitle="Profile Settings" hasNotifications={false}>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">
            Profile Settings
          </h1>
          <p className="text-sm text-slate-400">
            Manage your identity and security preferences.
          </p>
        </div>

        {loading ? (
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
            Loading profile...
          </div>
        ) : (
          <form onSubmit={handleSave} className="space-y-6">
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
              <div className="flex items-start justify-between gap-6 flex-wrap">
                <div>
                  <h2 className="text-lg font-semibold text-slate-100">
                    Public Profile
                  </h2>
                  <p className="text-sm text-slate-400">
                    Information visible to your team.
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-indigo-600 flex items-center justify-center text-lg font-bold text-white overflow-hidden">
                    {displayAvatarUrl ? (
                      <img
                        src={displayAvatarUrl}
                        alt="Profile avatar"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      initials
                    )}
                  </div>
                  <div className="space-x-2">
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/png,image/jpeg,image/jpg,image/webp,image/gif"
                      onChange={handleAvatarChange}
                      className="hidden"
                    />
                    <button
                      type="button"
                      onClick={handleUploadClick}
                      disabled={avatarUploading}
                      className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold"
                    >
                      {avatarUploading ? "Updating..." : "Update Photo"}
                    </button>
                    <button
                      type="button"
                      onClick={handleAvatarRemove}
                      disabled={avatarUploading || !displayAvatarUrl}
                      className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300 text-sm font-semibold"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs uppercase tracking-wide text-slate-400">
                    Username
                  </label>
                  <input
                    value={username}
                    readOnly
                    className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-400"
                  />
                </div>
                <div>
                  <label className="text-xs uppercase tracking-wide text-slate-400">
                    Full Name
                  </label>
                  <input
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
                  />
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900 p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-slate-100">
                  Account Security
                </h2>
                <p className="text-sm text-slate-400">
                  Manage your login and password.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs uppercase tracking-wide text-slate-400">
                    Work Email
                  </label>
                  <input
                    value={profile.email || ""}
                    readOnly
                    className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-400"
                  />
                </div>
                <div>
                  <label className="text-xs uppercase tracking-wide text-slate-400">
                    Phone Number
                  </label>
                  <input
                    placeholder="+216"
                    className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
                  />
                </div>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950 p-4 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-200">
                    Change Password
                  </h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div>
                    <label className="text-xs uppercase tracking-wide text-slate-400">
                      Current Password
                    </label>
                    <input
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
                    />
                  </div>
                  <div>
                    <label className="text-xs uppercase tracking-wide text-slate-400">
                      New Password
                    </label>
                    <input
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
                    />
                  </div>
                  <div>
                    <label className="text-xs uppercase tracking-wide text-slate-400">
                      Confirm Password
                    </label>
                    <input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
              <div>
                <h2 className="text-lg font-semibold text-slate-100">
                  System Preferences
                </h2>
                <p className="text-sm text-slate-400">
                  Manage how you receive updates.
                </p>
              </div>

              <div className="mt-4 flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-200">
                    Email Notifications
                  </p>
                  <p className="text-xs text-slate-400">
                    Receive weekly summaries and alerts.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={prefs.emailNotifications}
                  onChange={(e) =>
                    handlePrefChange("emailNotifications", e.target.checked)
                  }
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={handleDiscard}
                className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300 text-sm font-semibold"
              >
                Discard Changes
              </button>
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white text-sm font-semibold"
              >
                {saving ? "Saving..." : "Save Profile Settings"}
              </button>
            </div>
          </form>
        )}
      </div>

      {Toast}
    </AppLayout>
  );
}
