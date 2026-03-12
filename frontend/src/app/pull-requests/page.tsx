"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function PullRequestsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<{id: string; name: string}[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [sel, setSel] = useState("all");

  useEffect(() => {
    const t = localStorage.getItem("access_token");
    if (!t) { router.push("/login"); return; }
    Promise.all([
      fetch("/api/v1/projects",{headers:{Authorization:`Bearer ${t}`}}),
      fetch("/api/v1/tasks",{headers:{Authorization:`Bearer ${t}`}})
    ]).then(([r1,r2])=>{
      if(r1.ok) r1.json().then(d=>setProjects(d||[]));
      if(r2.ok) r2.json().then(d=>setTasks(d||[]));
    }).finally(()=>setLoading(false));
  },[router]);

  const fTasks = sel === "all" ? tasks : tasks.filter(t => t.project_id === sel);
  const logout = () => { localStorage.clear(); router.push("/login"); };
  const getStatusBadge = (s: string) => {
    if (s === "completed") return <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Completed</span>;
    if (s === "failed") return <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">Failed</span>;
    if (s === "processing") return <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">Processing</span>;
    return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-xs">{s}</span>;
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-gray-50"><div className="text-gray-600">Loading...</div></div>;

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
                <Link href="/pull-requests" className="px-3 py-2 text-sm rounded bg-gray-100 text-gray-900">Pull Requests</Link>
                <Link href="/architecture" className="px-3 py-2 text-sm rounded text-gray-600 hover:bg-gray-100">Architecture</Link>
              </div>
            </div>
            <button onClick={logout} className="text-sm text-gray-600 hover:text-gray-900">Logout</button>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold text-gray-900">Pull Requests</h1>
          <select value={sel} onChange={e => setSel(e.target.value)} className="px-3 py-2 border border-gray-300 rounded">
            <option value="all">All Projects</option>
            {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>

        <div className="bg-white border border-gray-200 rounded">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Branch</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Project</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {fTasks.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-12 text-center text-gray-500">No branches</td>
                </tr>
              ) : (
                fTasks.map(t => (
                  <tr key={t.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-900">{t.branch_name}</td>
                    <td className="px-4 py-3 text-gray-600">{projects.find(p => p.id === t.project_id)?.name || "Unknown"}</td>
                    <td className="px-4 py-3">{getStatusBadge(t.status)}</td>
                    <td className="px-4 py-3 text-gray-500 text-sm">{new Date(t.created_at).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
