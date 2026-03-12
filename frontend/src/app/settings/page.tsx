"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function SettingsPage() {
  const router = useRouter();
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) { router.push("/login"); return; }
    fetchSettings();
  }, [router]);

  const fetchSettings = async () => {
    try {
      const res = await fetch("/api/v1/settings", {
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
      });
      if (res.ok) setSettings(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleSave = async () => {
    if (!settings) return;
    setSaving(true);
    try {
      await fetch("/api/v1/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("access_token")}` },
        body: JSON.stringify(settings),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) { console.error(e); }
    finally { setSaving(false); }
  };

  const logout = () => { localStorage.clear(); router.push("/login"); };

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-gray-50"><div className="text-gray-600">Loading...</div></div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex justify-between h-14">
            <div className="flex items-center gap-6">
              <Link href="/dashboard" className="text-lg font-semibold text-gray-800">CodeQuality AI</Link>
              <div className="flex gap-1">
                <Link href="/dashboard" className="px-3 py-2 text-sm rounded text-gray-600 hover:bg-gray-100">Dashboard</Link>
                <Link href="/projects" className="px-3 py-2 text-sm rounded text-gray-600 hover:bg-gray-100">Projects</Link>
                <Link href="/settings" className="px-3 py-2 text-sm rounded bg-gray-100 text-gray-900">Settings</Link>
              </div>
            </div>
            <button onClick={logout} className="text-sm text-gray-600 hover:text-gray-900">Logout</button>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">System Settings</h1>

        {saved && <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-2 rounded">Settings saved!</div>}

        {settings && (
          <div className="space-y-6">
            <div className="bg-white border border-gray-200 rounded p-6">
              <h2 className="font-medium text-gray-800 mb-4">Analysis Settings</h2>
              <div className="space-y-3">
                <label className="flex items-center gap-3">
                  <input type="checkbox" checked={settings.analysis?.auto_review_on_pr || false} onChange={e => setSettings({...settings, analysis: {...settings.analysis, auto_review_on_pr: e.target.checked}})} className="w-4 h-4" />
                  <span className="text-gray-700">Auto-review on PR</span>
                </label>
                <label className="flex items-center gap-3">
                  <input type="checkbox" checked={settings.analysis?.include_security_checks || false} onChange={e => setSettings({...settings, analysis: {...settings.analysis, include_security_checks: e.target.checked}})} className="w-4 h-4" />
                  <span className="text-gray-700">Include security checks</span>
                </label>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded p-6">
              <h2 className="font-medium text-gray-800 mb-4">Compliance Standards</h2>
              <div className="space-y-2">
                {["iso_25010", "iso_23396", "google_style"].map(std => (
                  <label key={std} className="flex items-center gap-3">
                    <input type="checkbox" checked={settings.compliance?.enabled_standards?.includes(std) || false} onChange={e => {
                      const standards = e.target.checked ? [...(settings.compliance?.enabled_standards || []), std] : (settings.compliance?.enabled_standards || []).filter(s => s !== std);
                      setSettings({...settings, compliance: {...settings.compliance, enabled_standards: standards}});
                    }} className="w-4 h-4" />
                    <span className="text-gray-700">{std.toUpperCase()}</span>
                  </label>
                ))}
              </div>
            </div>

            <button onClick={handleSave} disabled={saving} className="w-full py-3 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
              {saving ? "Saving..." : "Save Settings"}
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
