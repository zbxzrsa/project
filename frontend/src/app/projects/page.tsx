"use client";
import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function ProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<any[]>([]);
  const [filtered, setFiltered] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showDel, setShowDel] = useState(false);
  const [projDel, setProjDel] = useState<any>(null);
  const [search, setSearch] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const t = localStorage.getItem("access_token");
    if (!t) { router.push("/login"); return; }
    fetchProjects();
  }, [router]);

  useEffect(() => {
    let f = projects;
    if (search) f = f.filter(p => p.name.toLowerCase().includes(search.toLowerCase()));
    setFiltered(f);
  }, [projects, search]);

  const fetchProjects = async () => {
    try {
      const r = await fetch("/api/v1/projects", { headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` } });
      if (r.ok) { const d = await r.json(); setProjects(d); setFiltered(d); }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleDel = async () => {
    if (!projDel) return;
    await fetch(`/api/v1/projects/${projDel.id}`, { method: "DELETE", headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` } });
    setShowDel(false); setProjDel(null); fetchProjects();
  };

  const ghAuth = () => { window.location.href = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/oauth/github`; };
  const logout = () => { localStorage.clear(); router.push("/login"); };

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
                <Link href="/projects" className="px-3 py-2 text-sm rounded bg-gray-100 text-gray-900">Projects</Link>
                <Link href="/pull-requests" className="px-3 py-2 text-sm rounded text-gray-600 hover:bg-gray-100">Pull Requests</Link>
                <Link href="/architecture" className="px-3 py-2 text-sm rounded text-gray-600 hover:bg-gray-100">Architecture</Link>
              </div>
            </div>
            <button onClick={logout} className="text-sm text-gray-600 hover:text-gray-900">Logout</button>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold text-gray-900">Projects</h1>
          <button onClick={() => setShowModal(true)} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Add Project</button>
        </div>

        <div className="flex gap-4 mb-6">
          <input type="text" placeholder="Search projects..." value={search} onChange={e => setSearch(e.target.value)} className="flex-1 px-4 py-2 border border-gray-300 rounded" />
        </div>

        {filtered.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded p-12 text-center text-gray-500">No projects yet</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map(p => (
              <div key={p.id} className="bg-white border border-gray-200 rounded p-4">
                <Link href={`/projects/${p.id}`} className="block">
                  <h3 className="font-medium text-gray-900">{p.name}</h3>
                  {p.repository_url && <p className="text-gray-500 text-sm truncate mt-1">{p.repository_url}</p>}
                  <p className="text-gray-400 text-xs mt-2">Created {new Date(p.created_at).toLocaleDateString()}</p>
                </Link>
                <button onClick={e => { e.preventDefault(); setProjDel(p); setShowDel(true); }} className="mt-2 text-red-600 text-sm hover:underline">Delete</button>
              </div>
            ))}
          </div>
        )}
      </main>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-white rounded p-6 max-w-md w-full">
            <h2 className="text-lg font-semibold mb-4">Add Project</h2>
            <button onClick={ghAuth} className="w-full py-3 bg-gray-900 text-white rounded mb-3">Connect GitHub</button>
            <div className="text-center text-gray-500 text-sm mb-3">or</div>
            <button onClick={() => setShowModal(false)} className="w-full py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50">Cancel</button>
          </div>
        </div>
      )}

      {showDel && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-white rounded p-6 max-w-sm">
            <h2 className="text-lg font-semibold mb-4">Delete Project</h2>
            <p className="text-gray-600 mb-4">Delete "{projDel?.name}"?</p>
            <div className="flex gap-2">
              <button onClick={() => { setShowDel(false); setProjDel(null); }} className="flex-1 py-2 border border-gray-300 rounded text-gray-700">Cancel</button>
              <button onClick={handleDel} className="flex-1 py-2 bg-red-600 text-white rounded hover:bg-red-700">Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
