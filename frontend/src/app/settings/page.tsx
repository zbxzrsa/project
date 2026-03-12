"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface Settings {
  analysis: {
    auto_review_on_pr: boolean;
    max_files_per_review: number;
    max_file_size_kb: number;
    severity_threshold: string;
    include_security_checks: boolean;
    include_style_checks: boolean;
    include_performance_checks: boolean;
  };
  compliance: {
    enabled_standards: string[];
    auto_check_on_review: boolean;
  };
  notifications: {
    email_on_critical_issues: boolean;
    email_on_completion: boolean;
    webhook_url: string | null;
  };
}

export default function SettingsPage() {
  const router = useRouter();
  const [settings, setSettings] = useState<Settings | null>(null);
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
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(settings),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) { console.error(e); }
    finally { setSaving(false); }
  };

  const logout = () => { localStorage.clear(); router.push("/login"); };
  if (loading) return <div className="min-h-screen bg-[#1b2838] flex items-center justify-center"><div className="text-[#66c0f4]">Loading...</div></div>;

  const nav = [
    {h:"/dashboard",l:"Dashboard"},
    {h:"/projects",l:"Projects"},
    {h:"/pull-requests",l:"Pull Requests"},
    {h:"/architecture",l:"Architecture"},
    {h:"/analysis-queue",l:"Queue"},
    {h:"/admin",l:"Admin"},
  ];

  return (
    <div className="min-h-screen bg-[#1b2838]">
      <nav className="bg-[#171a21] border-b border-[#2a475e]">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-8">
              <Link href="/dashboard" className="text-2xl font-bold text-[#66c0f4]">CodeQuality AI</Link>
              <div className="hidden md:flex gap-1">
                {nav.map(n=>(<Link key={n.h} href={n.h} className={`px-4 py-2 rounded text-sm ${n.h==="/settings"?"bg-[#66c0f4] text-[#171a21]":"text-[#c7d5e0] hover:bg-[#2a475e]"}`}>{n.l}</Link>))}
              </div>
            </div>
            <button onClick={logout} className="text-[#c7d5e0] hover:text-white text-sm">Logout</button>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-8">System Settings</h1>

        {saved && <div className="mb-4 bg-green-900/50 border border-green-700 text-green-400 px-4 py-2 rounded">Settings saved successfully!</div>}

        {settings && (
          <div className="space-y-6">
            <div className="bg-[#171a21] rounded-lg border border-[#2a475e] p-6">
              <h2 className="text-xl font-semibold text-[#66c0f4] mb-4">Analysis Settings</h2>
              <div className="space-y-4">
                <label className="flex items-center gap-3">
                  <input type="checkbox" checked={settings.analysis.auto_review_on_pr} onChange={e=>setSettings({...settings, analysis:{...settings.analysis, auto_review_on_pr:e.target.checked}})} className="w-5 h-5" />
                  <span className="text-[#c7d5e0]">Auto-review on PR</span>
                </label>
                <label className="flex items-center gap-3">
                  <input type="checkbox" checked={settings.analysis.include_security_checks} onChange={e=>setSettings({...settings, analysis:{...settings.analysis, include_security_checks:e.target.checked}})} className="w-5 h-5" />
                  <span className="text-[#c7d5e0]">Include security checks</span>
                </label>
                <label className="flex items-center gap-3">
                  <input type="checkbox" checked={settings.analysis.include_style_checks} onChange={e=>setSettings({...settings, analysis:{...settings.analysis, include_style_checks:e.target.checked}})} className="w-5 h-5" />
                  <span className="text-[#c7d5e0]">Include style checks</span>
                </label>
                <div>
                  <label className="text-[#8f98a0] text-sm">Max files per review</label>
                  <input type="number" value={settings.analysis.max_files_per_review} onChange={e=>setSettings({...settings, analysis:{...settings.analysis, max_files_per_review:parseInt(e.target.value)}})} className="ml-4 px-3 py-1 bg-[#0f1319] border border-[#3d5a73] text-white rounded" />
                </div>
              </div>
            </div>

            <div className="bg-[#171a21] rounded-lg border border-[#2a475e] p-6">
              <h2 className="text-xl font-semibold text-[#66c0f4] mb-4">Compliance Standards</h2>
              <div className="space-y-2">
                {["iso_25010", "iso_23396", "google_style"].map(std => (
                  <label key={std} className="flex items-center gap-3">
                    <input type="checkbox" checked={settings.compliance.enabled_standards.includes(std)} onChange={e=>{
                      const standards = e.target.checked ? [...settings.compliance.enabled_standards, std] : settings.compliance.enabled_standards.filter(s=>s!==std);
                      setSettings({...settings, compliance:{...settings.compliance, enabled_standards:standards}});
                    }} className="w-5 h-5" />
                    <span className="text-[#c7d5e0]">{std.toUpperCase()}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="bg-[#171a21] rounded-lg border border-[#2a475e] p-6">
              <h2 className="text-xl font-semibold text-[#66c0f4] mb-4">Notifications</h2>
              <div className="space-y-4">
                <label className="flex items-center gap-3">
                  <input type="checkbox" checked={settings.notifications.email_on_critical_issues} onChange={e=>setSettings({...settings, notifications:{...settings.notifications, email_on_critical_issues:e.target.checked}})} className="w-5 h-5" />
                  <span className="text-[#c7d5e0]">Email on critical issues</span>
                </label>
                <label className="flex items-center gap-3">
                  <input type="checkbox" checked={settings.notifications.email_on_completion} onChange={e=>setSettings({...settings, notifications:{...settings.notifications, email_on_completion:e.target.checked}})} className="w-5 h-5" />
                  <span className="text-[#c7d5e0]">Email on completion</span>
                </label>
              </div>
            </div>

            <button onClick={handleSave} disabled={saving} className="w-full py-3 bg-[#66c0f4] text-[#171a21] font-bold rounded hover:bg-[#4db8e8] disabled:opacity-50">
              {saving ? "Saving..." : "Save Settings"}
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
