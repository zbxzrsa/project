"use client";
import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Project } from "@/types";

export default function ProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [filtered, setFiltered] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showDel, setShowDel] = useState(false);
  const [projDel, setProjDel] = useState<Project | null>(null);
  const [search, setSearch] = useState("");
  const [cat, setCat] = useState("all");
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const t = localStorage.getItem("access_token");
    if (!t) { router.push("/login"); return; }
    fetchProjects();
  }, [router]);

  useEffect(() => {
    let f = projects;
    if (search) f = f.filter(p => p.name.toLowerCase().includes(search.toLowerCase()) || p.repository_url?.toLowerCase().includes(search.toLowerCase()));
    if (cat !== "all") f = f.filter(p => cat === "has_repo" ? !!p.repository_url : !p.repository_url);
    setFiltered(f);
  }, [projects, search, cat]);

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
  const upload = async (e: React.ChangeEvent<HTMLInputElement>) => { const f = e.target.files?.[0]; if (!f) return; const fd = new FormData(); fd.append("file", f); fd.append("name", f.name.replace(".zip","")); await fetch("/api/v1/projects/upload", { method: "POST", headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }, body: fd }); fetchProjects(); };
  const logout = () => { localStorage.clear(); router.push("/login"); };

  if (loading) return <div className="min-h-screen bg-[#1b2838] flex items-center justify-center"><div className="text-[#66c0f4] text-xl">Loading...</div></div>;

  const nav = [{h:"/dashboard",l:"Dashboard"},{h:"/projects",l:"Projects"},{h:"/pull-requests",l:"Pull Requests"},{h:"/architecture",l:"Architecture"},{h:"/analysis-queue",l:"Analysis Queue"}];

  return (
    <div className="min-h-screen bg-[#1b2838]">
      <nav className="bg-[#171a21] border-b border-[#2a475e]"><div className="max-w-7xl mx-auto px-4"><div className="flex justify-between h-16">
        <div className="flex items-center gap-8"><Link href="/dashboard" className="text-2xl font-bold text-[#66c0f4]">CodeQuality AI</Link>
          <div className="hidden md:flex gap-1">{nav.map(n=>(<Link key={n.h} href={n.h} className={`px-4 py-2 rounded text-sm ${n.h==="/projects"?"bg-[#66c0f4] text-[#171a21]":"text-[#c7d5e0] hover:bg-[#2a475e]"}`}>{n.l}</Link>))}</div>
        </div><button onClick={logout} className="text-[#c7d5e0] hover:text-white text-sm">Logout</button>
      </div></div></nav>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between mb-6"><h1 className="text-3xl font-bold text-white">Projects</h1><button onClick={()=>setShowModal(true)} className="px-4 py-2 bg-[#66c0f4] text-[#171a21] font-bold rounded hover:bg-[#4db8e8]">+ Add Project</button></div>
        <div className="flex gap-4 mb-6"><input type="text" placeholder="Search..." value={search} onChange={e=>setSearch(e.target.value)} className="flex-1 px-4 py-2 bg-[#0f1319] border border-[#3d5a73] text-white rounded"/><select value={cat} onChange={e=>setCat(e.target.value)} className="px-4 py-2 bg-[#0f1319] border border-[#3d5a73] text-white rounded"><option value="all">All</option><option value="has_repo">With Repo</option><option value="no_repo">Without Repo</option></select></div>
        {filtered.length===0?<div className="bg-[#171a21] rounded-lg border border-[#2a475e] p-12 text-center"><p className="text-[#c7d5e0]">No projects yet</p></div>:<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">{filtered.map(p=>(<div key={p.id} className="bg-gradient-to-br from-[#2a475e] to-[#1b2838] rounded-lg border border-[#3d5a73] p-5 hover:border-[#66c0f4] hover:shadow-[0_0_20px_rgba(102,192,244,0.2)]"><Link href={`/projects/${p.id}`} className="block"><h3 className="text-lg font-bold text-white">{p.name}</h3>{p.repository_url&&<p className="text-[#8f98a0] text-sm truncate mt-2">{p.repository_url}</p>}<p className="text-[#8f98a0] text-xs mt-2">Created {new Date(p.created_at).toLocaleDateString()}</p></Link><button onClick={e=>{e.preventDefault();setProjDel(p);setShowDel(true);}} className="mt-3 text-red-400 hover:text-red-300 text-sm">Delete</button></div>))}</div>}
      </main>
      {showModal&&<div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50"><div className="bg-[#171a21] rounded-xl p-6 max-w-md w-full border border-[#2a475e]"><h2 className="text-xl font-bold text-white mb-4">Add Project</h2><button onClick={ghAuth} className="w-full py-3 bg-[#171a21] border border-[#3d5a73] text-white rounded hover:border-[#66c0f4] mb-3">Connect GitHub</button><div className="text-[#8f98a0] text-center text-sm mb-3">or</div><button onClick={()=>fileRef.current?.click()} className="w-full py-3 border border-[#3d5a73] text-[#c7d5e0] rounded hover:border-[#66c0f4]">Upload ZIP</button><input type="file" accept=".zip" ref={fileRef} onChange={upload} className="hidden"/><button onClick={()=>setShowModal(false)} className="mt-4 w-full py-2 border border-[#3d5a73] text-[#c7d5e0] rounded hover:bg-[#2a475e]">Cancel</button></div></div>}
      {showDel&&<div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50"><div className="bg-[#171a21] rounded-xl p-6 max-w-sm border border-[#2a475e]"><h2 className="text-xl font-bold text-white mb-4">Delete Project</h2><p className="text-[#c7d5e0] mb-4">Delete "{projDel?.name}"?</p><div className="flex gap-2"><button onClick={()=>{setShowDel(false);setProjDel(null);}} className="flex-1 py-2 border border-[#3d5a73] text-white rounded">Cancel</button><button onClick={handleDel} className="flex-1 py-2 bg-red-600 text-white rounded hover:bg-red-700">Delete</button></div></div></div>}
    </div>
  );
}
