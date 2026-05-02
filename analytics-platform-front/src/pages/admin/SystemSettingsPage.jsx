import { useEffect, useState } from "react";
import {
  Bell,
  Database,
  RotateCcw,
  Save,
  Settings,
  Shield,
} from "lucide-react";
import AppLayout from "../../components/layout/AppLayout";

const defaultSettings = {
  appName: "InsightHub",
  defaultTimezone: "Africa/Tunis",
  sessionTimeoutMinutes: 30,
  strongPasswordPolicy: true,
  lockAfterFailedAttempts: 5,
  emailNotifications: true,
  inAppNotifications: true,
  maintenanceMode: false,
  maintenanceMessage:
    "System maintenance is in progress. Please try again shortly.",
};

export default function SystemSettingsPage() {
  const [settings, setSettings] = useState(defaultSettings);
  const [saveMessage, setSaveMessage] = useState("");

  useEffect(() => {
    const saved = window.localStorage.getItem("system_settings_v1");
    if (!saved) return;

    try {
      const parsed = JSON.parse(saved);
      setSettings((prev) => ({ ...prev, ...parsed }));
    } catch {
      setSettings(defaultSettings);
    }
  }, []);

  const updateSetting = (key, value) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setSaveMessage("");
  };

  const saveSettings = () => {
    window.localStorage.setItem("system_settings_v1", JSON.stringify(settings));
    setSaveMessage("System settings saved.");
  };

  const resetSettings = () => {
    setSettings(defaultSettings);
    window.localStorage.setItem(
      "system_settings_v1",
      JSON.stringify(defaultSettings),
    );
    setSaveMessage("Settings reset to defaults.");
  };

  return (
    <AppLayout pageTitle="System Settings">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">
            System Settings
          </h1>
          <p className="text-sm text-slate-400">
            Manage application and security configuration.
          </p>
        </div>

        {saveMessage && (
          <div className="p-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-sm text-emerald-200">
            {saveMessage}
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          <div className="rounded-xl border border-slate-700 bg-slate-900 p-5 space-y-4">
            <div className="flex items-center gap-2 text-slate-100">
              <Settings size={16} />
              <h2 className="text-base font-semibold">General</h2>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-xs uppercase tracking-wide text-slate-400">
                  Application name
                </label>
                <input
                  value={settings.appName}
                  onChange={(e) => updateSetting("appName", e.target.value)}
                  className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
                />
              </div>
              <div>
                <label className="text-xs uppercase tracking-wide text-slate-400">
                  Default timezone
                </label>
                <input
                  value={settings.defaultTimezone}
                  onChange={(e) =>
                    updateSetting("defaultTimezone", e.target.value)
                  }
                  className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
                />
              </div>
              <div>
                <label className="text-xs uppercase tracking-wide text-slate-400">
                  Session timeout (minutes)
                </label>
                <input
                  type="number"
                  min={5}
                  max={480}
                  value={settings.sessionTimeoutMinutes}
                  onChange={(e) =>
                    updateSetting(
                      "sessionTimeoutMinutes",
                      Number(e.target.value || 30),
                    )
                  }
                  className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
                />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-700 bg-slate-900 p-5 space-y-4">
            <div className="flex items-center gap-2 text-slate-100">
              <Shield size={16} />
              <h2 className="text-base font-semibold">Security</h2>
            </div>
            <div className="space-y-3 text-sm text-slate-200">
              <label className="flex items-center justify-between gap-3">
                <span>Strong password policy</span>
                <input
                  type="checkbox"
                  checked={settings.strongPasswordPolicy}
                  onChange={(e) =>
                    updateSetting("strongPasswordPolicy", e.target.checked)
                  }
                />
              </label>
              <div>
                <label className="text-xs uppercase tracking-wide text-slate-400">
                  Lock account after failed attempts
                </label>
                <input
                  type="number"
                  min={3}
                  max={20}
                  value={settings.lockAfterFailedAttempts}
                  onChange={(e) =>
                    updateSetting(
                      "lockAfterFailedAttempts",
                      Number(e.target.value || 5),
                    )
                  }
                  className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
                />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-700 bg-slate-900 p-5 space-y-4">
            <div className="flex items-center gap-2 text-slate-100">
              <Bell size={16} />
              <h2 className="text-base font-semibold">Notifications</h2>
            </div>
            <div className="space-y-3 text-sm text-slate-200">
              <label className="flex items-center justify-between gap-3">
                <span>Email notifications</span>
                <input
                  type="checkbox"
                  checked={settings.emailNotifications}
                  onChange={(e) =>
                    updateSetting("emailNotifications", e.target.checked)
                  }
                />
              </label>
              <label className="flex items-center justify-between gap-3">
                <span>In-app notifications</span>
                <input
                  type="checkbox"
                  checked={settings.inAppNotifications}
                  onChange={(e) =>
                    updateSetting("inAppNotifications", e.target.checked)
                  }
                />
              </label>
            </div>
          </div>

          <div className="rounded-xl border border-slate-700 bg-slate-900 p-5 space-y-4">
            <div className="flex items-center gap-2 text-slate-100">
              <Database size={16} />
              <h2 className="text-base font-semibold">Maintenance</h2>
            </div>
            <label className="flex items-center justify-between gap-3 text-sm text-slate-200">
              <span>Maintenance mode</span>
              <input
                type="checkbox"
                checked={settings.maintenanceMode}
                onChange={(e) =>
                  updateSetting("maintenanceMode", e.target.checked)
                }
              />
            </label>
            <div>
              <label className="text-xs uppercase tracking-wide text-slate-400">
                Maintenance message
              </label>
              <textarea
                rows={4}
                value={settings.maintenanceMessage}
                onChange={(e) =>
                  updateSetting("maintenanceMessage", e.target.value)
                }
                className="mt-1 w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100"
              />
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={saveSettings}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold"
          >
            <Save size={14} /> Save changes
          </button>
          <button
            onClick={resetSettings}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm"
          >
            <RotateCcw size={14} /> Reset defaults
          </button>
          <p className="text-xs text-slate-400">
            These settings are currently stored locally in the browser.
          </p>
        </div>
      </div>
    </AppLayout>
  );
}
