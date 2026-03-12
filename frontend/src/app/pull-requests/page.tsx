"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Project, AnalysisTask } from "@/types";

export default function PullRequestsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [tasks, setTasks] = useState<AnalysisTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [sel, setSel] = useState("all");

  useEffect(() => {
    const t = localStorage.getItem("access_token");
    if (!t) { router.push("/login"); return; }
    Promise.all([fetch("/api/v1/projects",{h:{Authorization:`Bearer ${t}`}}),fetch("/api/v1/tasks",{h:{Authorization:`Bearer ${t}`}})]).then(([r1,r2])=>{if(r1.ok)setProjects(...[await r1.json()]);if(r2.ok)setTasks(...[(await r2.json())||[]]);}).finally(()=>setLoading(false));
  },[router]);

  const fTasks = sel==="all"?tasks:tasks.filter(t=>t.project_id===sel);
  const logout = () => { localStorage.clear(); router.push("/login"); };
  const getStatusIcon = (s:string) => s==="completed"?"✅":s==="failed"?"❌":s==="processing"?"🔄":"⏳";

  if (loading) return <div className="min-h-screen bg-[#1b2838] flex items-center justify-center"><div className="text-[#66c0f4] text-xl">Loading...</div></div>;

  const nav = [{h:"/dashboard",l:"Dashboard"},{h:"/projects",l:"Projects"},{h:"/pull-requests",l:"Pull Requests"},{h:"/architecture",l:"Architecture"},{h:"/analysis-queue",l:"Analysis Queue"}];

  return (
    <div className="min-h-screen bg-[#1b2838]">
      <nav className="bg-[#171a21] border-b border-[#2a475e]"><div className="max-w-7xl mx-auto px-4"><div className="flex justify-between h-16">
        <div className="flex items-center gap-8"><Link href="/dashboard" className="text-2xl font-bold text-[#66c0f4]">CodeQuality AI</Link>
          <div className="hidden md:flex gap-1">{nav.map(n=>(<Link key={n.h} href={n.h} className={`px-4 py-2 rounded text-sm ${n.h==="/pull-requests"?"bg-[#66c0f4] text-[#171a21]":"text-[#c7d5e0] hover:bg-[#2a475e]"}`}>{n.l}</Link>))}</div>
        </div><button onClick={logout} className="text-[#c7d5e0] hover:text-white text-sm">Logout</button>
      </div></div></nav>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between mb-6"><h1 className="text-3xl font-bold text-white">Pull Requests</h1><select value={sel} onChange={e=>setSel(e.target.value)} className="px-4 py-2 bg-[#0f1319] border border-[#3d5a73] text-white rounded">{projects.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></div>
        <div className="bg-[#171a21] rounded-lg border border-[#2a475e] overflow-hidden">
          <table className="w-full"><thead className="bg-[#0f1319]"><tr><th className="px-4 py-3 text-left text-[#8f98a0] text-sm">Branch</th><th className="px-4 py-3 text-left text-[#8f98a0] text-sm">Project</th><th className="px-4 py-3 text-left text-[#8f98a0] text-sm">Status</th><th className="px-4 py-3 text-left text-[#8f98a0] text-sm">Created</th></tr></thead>
            <tbody className="divide-y divide-[#2a475e]">{fTasks.length===0?<tr><td colSpan={4} className="px-4 py-12 text-center text-[#c7d5e0]">No branches</td></tr>:fTasks.map(t=><tr key={t.id} className="hover:bg-[#2a475e]"><td className="px-4 py-3 text-white">🌿 {t.branch_name}</td><td className="px-4 py-3 text-[#c7d5e0]">{projects.find(p=>p.id===t.project_id)?.name||"Unknown"}</td><td className="px-4 py-3">{getStatusIcon(t.status)} <span className="text-[#c7d5e0]">{t.status}</span></td><td className="px-4 py-3 text-[#8f98a0]">{new Date(t.created_at).toLocaleString()}</td></tr>)}</tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
