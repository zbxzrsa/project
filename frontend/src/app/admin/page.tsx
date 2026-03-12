"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function AdminPage() {
  const router = useRouter();
  const [stats, setStats] = useState({ totalUsers: 0, totalProjects: 0, totalReviews: 0, activeUsers: 0 });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) { router.push("/login"); return; }
    fetchStats();
  }, [router]);

  const fetchStats = async () => {
    try {
      const res = await fetch("/api/v1/admin/stats", { headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }});
      if (res.ok) setStats(await res.json());
    } catch (error) { console.error("Failed to load stats:", error); }
    finally { setIsLoading(false); }
  };

  const handleLogout = () => { localStorage.clear(); router.push("/login"); };

  const menuItems = [
    { title: "User Management", description: "Manage users, roles", href: "/admin/users" },
    { title: "Tenant Management", description: "Configure tenants", href: "/admin/tenants" },
    { title: "System Settings", description: "Configure settings", href: "/admin/settings" },
    { title: "Audit Logs", description: "View system logs", href: "/admin/audit-logs" },
  ];

  if (isLoading) return <div className="min-h-screen flex items-center justify-center bg-gray-50"><div className="text-gray-600">Loading...</div></div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between h-14">
            <div className="flex items-center gap-6">
              <Link href="/dashboard" className="text-lg font-semibold text-gray-800">CodeQuality AI</Link>
              <div className="flex gap-1">
                <Link href="/dashboard" className="px-3 py-2 text-sm rounded text-gray-600 hover:bg-gray-100">Dashboard</Link>
                <Link href="/projects" className="px-3 py-2 text-sm rounded text-gray-600 hover:bg-gray-100">Projects</Link>
                <Link href="/admin" className="px-3 py-2 text-sm rounded bg-gray-100 text-gray-900">Admin</Link>
              </div>
            </div>
            <button onClick={handleLogout} className="text-sm text-gray-600 hover:text-gray-900">Logout</button>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">Admin Panel</h1>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white border border-gray-200 rounded p-4">
            <div className="text-gray-500 text-sm">Total Users</div>
            <div className="text-2xl font-bold text-gray-900">{stats.totalUsers}</div>
          </div>
          <div className="bg-white border border-gray-200 rounded p-4">
            <div className="text-gray-500 text-sm">Total Projects</div>
            <div className="text-2xl font-bold text-gray-900">{stats.totalProjects}</div>
          </div>
          <div className="bg-white border border-gray-200 rounded p-4">
            <div className="text-gray-500 text-sm">Total Reviews</div>
            <div className="text-2xl font-bold text-gray-900">{stats.totalReviews}</div>
          </div>
          <div className="bg-white border border-gray-200 rounded p-4">
            <div className="text-gray-500 text-sm">Active Users</div>
            <div className="text-2xl font-bold text-gray-900">{stats.activeUsers}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {menuItems.map((item) => (
            <Link key={item.title} href={item.href} className="block bg-white border border-gray-200 rounded p-4 hover:border-blue-400">
              <h3 className="font-medium text-gray-900">{item.title}</h3>
              <p className="text-gray-500 text-sm">{item.description}</p>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
