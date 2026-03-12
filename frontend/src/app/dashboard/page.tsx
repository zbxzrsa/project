"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { DashboardStats, Activity } from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats>({total_projects: 0, pending_reviews: 0, critical_issues: 0, architecture_health: 100});
  const [activities, setActivities] = useState<Activity[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) { router.push("/login"); return; }
    fetchDashboardData();
  }, [router]);

  const fetchDashboardData = async () => {
    try {
      const headers = { Authorization: `Bearer ${localStorage.getItem("access_token")}` };
      const [statsRes, activitiesRes] = await Promise.all([fetch("/api/v1/dashboard", { headers }), fetch("/api/v1/audit-logs?limit=10", { headers })]);
      if (statsRes.ok) setStats(await statsRes.json());
      if (activitiesRes.ok) setActivities(Array.isArray(await activitiesRes.json()) ? await activitiesRes.json() : []);
    } catch (e) { console.error(e); }
    finally { setIsLoading(false); }
  };

  const handleLogout = () => { localStorage.removeItem("access_token"); localStorage.removeItem("refresh_token"); router.push("/login"); };
  if (isLoading) return <div className="min-h-screen bg-[#1b2838] flex items-center justify-center"><div className="text-[#66c0f4] text-xl">Loading...</div></div>;

  const nav = [{h:"/dashboard",l:"Dashboard"},{h:"/projects",l:"Projects"},{h:"/pull-requests",l:"Pull Requests"},{h:"/architecture",l:"Architecture"},{h:"/analysis-queue",l:"Analysis Queue"}];
  const statsData = [{l:"Total Projects",v:stats.total_projects,i:"📁",c:"from-blue-900 to-blue-950"},{l:"Pending Reviews",v:stats.pending_reviews,i:"⏳",c:"from-yellow-900 to-yellow-950"},{l:"Critical Issues",v:stats.critical_issues,i:"⚠️",c:"from-red-900 to-red-950"},{l:"Architecture Health",v:`${stats.architecture_health}%`,i:"💚",c:"from-green-900 to-green-950"}];
  const actions = [{h:"/projects",l:"+ Add New Project",p:true},{h:"/pull-requests",l:"View All Branches",p:false},{h:"/architecture",l:"View Architecture",p:false},{h:"/analysis-queue",l:"Manage Analysis Queue",p:false}];

  return (
    <div className="min-h-screen bg-[#1b2838]">
      <nav className="bg-[#171a21] border-b border-[#2a475e]">
        <div className="max-w-7xl mx-auto px-4"><div className="flex justify-between h-16">
          <div className="flex items-center gap-8"><Link href="/dashboard" className="text-2xl font-bold text-[#66c0f4] hover:text-[#4db8e8]">CodeQuality AI</Link>
            <div className="hidden md:flex gap-1">{nav.map(n=>(<Link key={n.h} href={n.h} className={`px-4 py-2 rounded text-sm font-medium transition-all ${n.h==="/dashboard"?"bg-[#66c0f4] text-[#171a21]":"text-[#c7d5e0] hover:bg-[#2a475e]"}`}>{n.l}</Link>))}</div>
          </div><button onClick={handleLogout} className="text-[#c7d5e0] hover:text-white text-sm">Logout</button>
        </div></div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-8">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {statsData.map((s,i)=>(<div key={i} className={`bg-gradient-to-br ${s.c} rounded-lg p-5 border border-[#3d5a73] hover:border-[#66c0f4] hover:shadow-[0_0_20px_rgba(102,192,244,0.2)]`}><div className="flex items-center justify-between mb-2"><span className="text-3xl">{s.i}</span><span className="text-4xl font-bold text-white">{s.v}</span></div><div className="text-[#c7d5e0] text-sm">{s.l}</div></div>))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-[#171a21] rounded-lg border border-[#2a475e] overflow-hidden"><div className="px-6 py-4 border-b border-[#2a475e] bg-[#0f1319]"><h2 className="text-lg font-semibold text-[#66c0f4]">Recent Activity</h2></div><div className="max-h-80 overflow-y-auto">{activities.length===0?<div className="px-6 py-12 text-center text-[#c7d5e0]">No recent activity</div>:activities.map((a,i)=>(<div key={i} className="px-6 py-4 border-b border-[#2a475e] hover:bg-[#2a475e]"><div className="flex items-center gap-3"><span className="text-xl">{a.type==="review"?"🔍":a.type==="project"?"📁":"⚙️"}</span><div><p className="text-white font-medium">{a.action}</p><p className="text-[#8f98a0] text-sm">{a.description}</p></div></div></div>))}</div></div>
          <div className="bg-[#171a21] rounded-lg border border-[#2a475e] overflow-hidden"><div className="px-6 py-4 border-b border-[#2a475e] bg-[#0f1319]"><h2 className="text-lg font-semibold text-[#66c0f4]">Quick Actions</h2></div><div className="p-6 space-y-3">{actions.map((a,i)=>(<Link key={i} href={a.h} className={`block w-full text-center px-4 py-3 rounded transition-all ${a.p?"bg-[#66c0f4] text-[#171a21] font-bold hover:bg-[#4db8e8] hover:shadow-[0_0_15px_rgba(102,192,244,0.4)]":"border border-[#3d5a73] text-[#c7d5e0] hover:border-[#66c0f4] hover:text-[#66c0f4]"}`}>{a.l}</Link>))}</div></div>
        </div>
      </main>
    </div>
  );
}
