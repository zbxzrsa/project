"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Project, ArchitectureGraph } from "@/types";

export default function ArchitecturePage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [sel, setSel] = useState("");
  const [graph, setGraph] = useState<ArchitectureGraph | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = localStorage.getItem("access_token");
    if (!t) { router.push("/login"); return; }
    fetch("/api/v1/projects",{h:{Authorization:`Bearer ${t}`}}).then(r=>r.ok&&r.json()).then(d=>{setProjects(d);if(d.length)setSel(d[0].id);}).finally(()=>setLoading(false));
  },[router]);

  useEffect(() => { if(sel) fetch(`/api/v1/projects/${sel}/architecture`,{h:{Authorization:`Bearer ${localStorage.getItem("access_token")}`}}).then(r=>r.ok&&r.json()).then(setGraph); },[sel]);

  const logout = () => { localStorage.clear(); router.push("/login"); };
  const getColor = (t:string) => t==="file"?"bg-blue-900":t==="module"?"bg-green-900":t==="class"?"bg-purple-900":"bg-yellow-900";

  if (loading) return <div className="min-h-screen bg-[#1b2838] flex items-center justify-center"><div className="text-[#66c0f4] text-xl">Loading...</div></div>;

  const nav = [{h:"/dashboard",l:"Dashboard"},{h:"/projects",l:"Projects"},{h:"/pull-requests",l:"Pull Requests"},{h:"/architecture",l:"Architecture"},{h:"/analysis-queue",l:"Analysis Queue"}];

  return (
    <div className="min-h-screen bg-[#1b2838]">
      <nav className="bg-[#171a21] border-b border-[#2a475e]"><div className="max-w-7xl mx-auto px-4"><div className="flex justify-between h-16">
        <div className="flex items-center gap-8"><Link href="/dashboard" className="text-2xl font-bold text-[#66c0f4]">CodeQuality AI</Link>
          <div className="hidden md:flex gap-1">{nav.map(n=>(<Link key={n.h} href={n.h} className={`px-4 py-2 rounded text-sm ${n.h==="/architecture"?"bg-[#66c0f4] text-[#171a21]":"text-[#c7d5e0] hover:bg-[#2a475e]"}`}>{n.l}</Link>))}</div>
        </div><button onClick={logout} className="text-[#c7d5e0] hover:text-white text-sm">Logout</button>
      </div></div></nav>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between mb-6"><h1 className="text-3xl font-bold text-white">Architecture</h1><select value={sel} onChange={e=>setSel(e.target.value)} className="px-4 py-2 bg-[#0f1319] border border-[#3d5a73] text-white rounded">{projects.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></div>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="bg-[#171a21] rounded-lg border border-[#2a475e] p-4"><h3 className="text-[#66c0f4] font-semibold mb-4">Modules</h3><div className="space-y-2 max-h-96 overflow-y-auto">{graph?.nodes.filter(n=>n.type==="module"||n.type==="class").map(n=><div key={n.id} className={`p-3 rounded ${getColor(n.type)} border border-[#3d5a73]`}><div className="text-white font-medium">{n.name}</div><div className="text-[#8f98a0] text-xs">{n.type}</div></div>)}</div></div>
          <div className="lg:col-span-3 bg-[#171a21] rounded-lg border border-[#2a475e] min-h-[500px] p-6"><h3 className="text-[#66c0f4] font-semibold mb-4">Graph View {graph&&`(${graph.nodeCount} nodes)`}</h3>{!graph?<div className="text-[#c7d5e0] text-center py-20">Select a project</div>:<div className="flex flex-wrap gap-4 justify-center">{graph.nodes.slice(0,20).map(n=><div key={n.id} className={`p-4 rounded ${getColor(n.type)} border border-[#3d5a73] hover:border-[#66c0f4]`}><div className="text-white font-medium">{n.name}</div><div className="text-[#8f98a0] text-xs">{n.type}</div></div>)}</div>}</div></div>
        </div>
      </main>
    </div>
  );
}
