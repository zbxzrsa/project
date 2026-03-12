"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Project, AnalysisTask } from "@/types";

export default function AnalysisQueuePage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<AnalysisTask[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState({paused:false,w:0,p:0,c:0,f:0});
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    const h = { Authorization: `Bearer ${localStorage.getItem("access_token")}` };
    const [tR, pR, qR] = await Promise.all([fetch("/api/v1/tasks",{h}),fetch("/api/v1/projects",{h}),fetch("/api/v1/queue/status",{h})]);
    if(tR.ok) setTasks(...[(await tR.json())||[]]);
    if(pR.ok) setProjects(...[await pR.json()]);
    if(qR.ok) setStats(...[await qR.json()]);
    setLoading(false);
  };

  useEffect(() => {
    const t = localStorage.getItem("access_token");
    if (!t) { router.push("/login"); return; }
    fetchData();
    const int = setInterval(fetchData,5000);
    return ()=>clearInterval(int);
  },[router]);

  const pause = async () => { await fetch("/api/v1/queue/pause",{method:"POST",h:{Authorization:`Bearer ${localStorage.getItem("access_token")}`}}); fetchData(); };
  const resume = async () => { await fetch("/api/v1/queue/resume",{method:"POST",h:{Authorization:`Bearer ${localStorage.getItem("access_token")}`}}); fetchData(); };
  const retry = async (id:string) => { await fetch(`/api/v1/tasks/${id}/retry`,{method:"POST",h:{Authorization:`Bearer ${localStorage.getItem("access_token")}`}}); fetchData(); };
  const logout = () => { localStorage.clear(); router.push("/login"); };
  const getIcon = (s:string) => s==="completed"?"✅":s==="failed"?"❌":s==="processing"?"🔄":s==="queued"?"⏳":"⏸";

  if (loading) return <div className="min-h-screen bg-[#1b2838] flex items-center justify-center"><div className="text-[#66c0f4] text-xl">Loading...</div></div>;

  const nav = [{h:"/dashboard",l:"Dashboard"},{h:"/projects",l:"Projects"},{h:"/pull-requests",l:"Pull Requests"},{h:"/architecture",l:"Architecture"},{h:"/analysis-queue",l:"Analysis Queue"}];

  return (
    <div className="min-h-screen bg-[#1b2838]">
      <nav className="bg-[#171a21] border-b border-[#2a475e]"><div className="max-w-7xl mx-auto px-4"><div className="flex justify-between h-16">
        <div className="flex items-center gap-8"><Link href="/dashboard" className="text-2xl font-bold text-[#66c0f4]">CodeQuality AI</Link>
          <div className="hidden md:flex gap-1">{nav.map(n=>(<Link key={n.h} href={n.h} className={`px-4 py-2 rounded text-sm ${n.h==="/analysis-queue"?"bg-[#66c0f4] text-[#171a21]":"text-[#c7d5e0] hover:bg-[#2a475e]"}`}>{n.l}</Link>))}</div>
        </div><button onClick={logout} className="text-[#c7d5e0] hover:text-white text-sm">Logout</button>
      </div></div></nav>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-6">Analysis Queue</h1>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">{[{l:"Status",v:stats.paused?"⏸ Paused":"▶ Running",c:stats.paused?"text-yellow-400":"text-green-400"},{l:"Waiting",v:stats.w},{l:"Processing",v:stats.p,c:"text-blue-400"},{l:"Completed",v:stats.c,c:"text-green-400"},{l:"Failed",v:stats.f,c:"text-red-400"}].map((s,i)=><div key={i} className="bg-[#171a21] rounded-lg border border-[#2a475e] p-4"><div className="text-[#8f98a0] text-sm">{s.l}</div><div className={`text-2xl font-bold ${s.c||"text-white"}`}>{s.v}</div></div>)}</div>
        <div className="flex gap-2 mb-6">{stats.paused?<button onClick={resume} className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">▶ Resume</button>:<button onClick={pause} className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700">⏸ Pause</button>}</div>
        <div className="bg-[#171a21] rounded-lg border border-[#2a475e] overflow-hidden"><table className="w-full"><thead className="bg-[#0f1319]"><tr><th className="px-4 py-3 text-left text-[#8f98a0]">Task</th><th className="px-4 py-3 text-left text-[#8f98a0]">Project</th><th className="px-4 py-3 text-left text-[#8f98a0]">Status</th><th className="px-4 py-3 text-left text-[#8f98a0]">Progress</th><th className="px-4 py-3 text-left text-[#8f98a0]">Actions</th></tr></thead><tbody className="divide-y divide-[#2a475e]">{tasks.length===0?<tr><td colSpan={5} className="px-4 py-12 text-center text-[#c7d5e0]">No tasks</td></tr>:tasks.map(t=><tr key={t.id} className="hover:bg-[#2a475e]"><td className="px-4 py-3 text-white">{t.branch_name}</td><td className="px-4 py-3 text-[#c7d5e0]">{projects.find(p=>p.id===t.project_id)?.name}</td><td className="px-4 py-3">{getIcon(t.status)} {t.status}</td><td className="px-4 py-3"><div className="w-24 bg-[#0f1319] rounded h-2"><div className="bg-[#66c0f4] h-2 rounded" style={{width:`${t.progress}%`}}></div></div></td><td className="px-4 py-3">{t.status==="failed"&&<button onClick={()=>retry(t.id)} className="text-blue-400 hover:text-blue-300">Retry</button>}</td></tr>)}</tbody></table></div>
      </main>
    </div>
  );
}
