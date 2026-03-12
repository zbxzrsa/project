"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState({total_projects: 0, pending_reviews: 0, critical_issues: 0, architecture_health: 100});
  const [activities, setActivities] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) { router.push("/login"); return; }
    fetchDashboardData();
  }, [router]);

  const fetchDashboardData = async () => {
    try {
      const headers = { Authorization: `Bearer ${localStorage.getItem("access_token")}` };
      const [statsRes, activitiesRes] = await Promise.all([
        fetch("/api/v1/dashboard", { headers }),
        fetch("/api/v1/audit-logs?limit=10", { headers })
      ]);
      if (statsRes.ok) {
        const data = await statsRes.json();
        setStats(data.stats || {total_projects: 0, pending_reviews: 0, critical_issues: 0, architecture_health: 100});
      }
      if (activitiesRes.ok) setActivities(Array.isArray(await activitiesRes.json()) ? await activitiesRes.json() : []);
    } catch (e) { console.error(e); }
    finally { setIsLoading(false); }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    router.push("/login");
  };

  if (isLoading) return <div className="min-h-screen flex items-center justify-center bg-gray-50"><div className="text-gray-600">Loading...</div></div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between h-14">
            <div className="flex items-center gap-6">
              <Link href="/dashboard" className="text-lg font-semibold text-gray-800">CodeQuality AI</Link>
              <div className="flex gap-1">
                <Link href="/dashboard" className="px-3 py-2 text-sm rounded bg-gray-100 text-gray-900">Dashboard</Link>
                <Link href="/projects" className="px-3 py-2 text-sm rounded text-gray-600 hover:bg-gray-100">Projects</Link>
                <Link href="/pull-requests" className="px-3 py-2 text-sm rounded text-gray-600 hover:bg-gray-100">Pull Requests</Link>
                <Link href="/architecture" className="px-3 py-2 text-sm rounded text-gray-600 hover:bg-gray-100">Architecture</Link>
              </div>
            </div>
            <button onClick={handleLogout} className="text-sm text-gray-600 hover:text-gray-900">Logout</button>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">Dashboard</h1>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white border border-gray-200 rounded p-4">
            <div className="text-gray-500 text-sm">Total Projects</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_projects}</div>
          </div>
          <div className="bg-white border border-gray-200 rounded p-4">
            <div className="text-gray-500 text-sm">Pending Reviews</div>
            <div className="text-2xl font-bold text-gray-900">{stats.pending_reviews}</div>
          </div>
          <div className="bg-white border border-gray-200 rounded p-4">
            <div className="text-gray-500 text-sm">Critical Issues</div>
            <div className="text-2xl font-bold text-red-600">{stats.critical_issues}</div>
          </div>
          <div className="bg-white border border-gray-200 rounded p-4">
            <div className="text-gray-500 text-sm">Architecture Health</div>
            <div className="text-2xl font-bold text-green-600">{stats.architecture_health}%</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white border border-gray-200 rounded">
            <div className="px-4 py-3 border-b border-gray-200">
              <h2 className="font-medium text-gray-800">Recent Activity</h2>
            </div>
            <div className="max-h-64 overflow-y-auto">
              {activities.length === 0 ? (
                <div className="px-4 py-8 text-center text-gray-500">No recent activity</div>
              ) : (
                activities.map((a, i) => (
                  <div key={i} className="px-4 py-3 border-b border-gray-100 hover:bg-gray-50">
                    <div className="text-gray-900 text-sm">{a.action}</div>
                    <div className="text-gray-500 text-xs">{a.description}</div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded">
            <div className="px-4 py-3 border-b border-gray-200">
              <h2 className="font-medium text-gray-800">Quick Actions</h2>
            </div>
            <div className="p-4 space-y-2">
              <Link href="/projects" className="block w-full px-4 py-2 text-center bg-blue-600 text-white rounded hover:bg-blue-700">Add New Project</Link>
              <Link href="/pull-requests" className="block w-full px-4 py-2 text-center border border-gray-300 text-gray-700 rounded hover:bg-gray-50">View Pull Requests</Link>
              <Link href="/architecture" className="block w-full px-4 py-2 text-center border border-gray-300 text-gray-700 rounded hover:bg-gray-50">View Architecture</Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
