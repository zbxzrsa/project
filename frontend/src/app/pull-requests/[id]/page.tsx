"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { AnalysisTask, Branch, Project, ReviewIssue } from "@/types";

interface TaskDetail extends AnalysisTask {
  results?: {
    summary?: string;
    score?: number;
    issues?: ReviewIssue[];
    strengths?: string[];
    improvements?: string[];
  };
}

export default function PullRequestDetailPage() {
  const params = useParams();
  const router = useRouter();
  const taskId = params.id as string;
  
  const [task, setTask] = useState<TaskDetail | null>(null);
  const [branch, setBranch] = useState<Branch | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"issues" | "improvements" | "architecture">("issues");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) { router.push("/login"); return; }
    fetchData();
  }, [taskId, router]);

  const fetchData = async () => {
    try {
      const headers = { Authorization: `Bearer ${localStorage.getItem("access_token")}` };
      
      const taskRes = await fetch(`/api/v1/tasks/${taskId}`, { headers });
      if (taskRes.ok) {
        const taskData = await taskRes.json();
        setTask(taskData);
        
        if (taskData.branch_id) {
          const branchRes = await fetch(`/api/v1/branches/${taskData.branch_id}`, { headers });
          if (branchRes.ok) setBranch(await branchRes.json());
        }
        
        const projectRes = await fetch(`/api/v1/projects/${taskData.project_id}`, { headers });
        if (projectRes.ok) setProject(await projectRes.json());
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const logout = () => { localStorage.clear(); router.push("/login"); };
  
  const getSeverityColor = (s: string) => {
    switch (s) {
      case "critical": return "bg-red-900 text-red-400 border-red-700";
      case "high": return "bg-orange-900 text-orange-400 border-orange-700";
      case "medium": return "bg-yellow-900 text-yellow-400 border-yellow-700";
      case "low": return "bg-blue-900 text-blue-400 border-blue-700";
      default: return "bg-gray-800 text-gray-400 border-gray-700";
    }
  };

  if (loading) return <div className="min-h-screen bg-[#1b2838] flex items-center justify-center"><div className="text-[#66c0f4] text-xl">Loading...</div></div>;

  const results = task?.results as TaskDetail["results"] | undefined;
  const issues = results?.issues || [];
  const strengths = results?.strengths || [];
  const improvements = results?.improvements || [];

  const nav = [
    {h:"/dashboard",l:"Dashboard"},
    {h:"/projects",l:"Projects"},
    {h:"/pull-requests",l:"Pull Requests"},
    {h:"/architecture",l:"Architecture"},
    {h:"/analysis-queue",l:"Analysis Queue"}
  ];

  return (
    <div className="min-h-screen bg-[#1b2838]">
      <nav className="bg-[#171a21] border-b border-[#2a475e]">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-8">
              <Link href="/dashboard" className="text-2xl font-bold text-[#66c0f4]">CodeQuality AI</Link>
              <div className="hidden md:flex gap-1">
                {nav.map(n=>(<Link key={n.h} href={n.h} className={`px-4 py-2 rounded text-sm ${n.h==="/pull-requests"?"bg-[#66c0f4] text-[#171a21]":"text-[#c7d5e0] hover:bg-[#2a475e]"}`}>{n.l}</Link>))}
              </div>
            </div>
            <button onClick={logout} className="text-[#c7d5e0] hover:text-white text-sm">Logout</button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-6">
          <Link href="/pull-requests" className="text-[#66c0f4] hover:underline">← Back to Pull Requests</Link>
        </div>

        <div className="bg-[#171a21] rounded-lg border border-[#2a475e] p-6 mb-6">
          <h1 className="text-2xl font-bold text-white mb-2">🌿 {task?.branch_name || "Unknown Branch"}</h1>
          <p className="text-[#8f98a0]">{project?.name || "Unknown Project"}</p>
          
          <div className="flex gap-4 mt-4">
            <div className="px-3 py-1 rounded bg-[#2a475e] text-[#c7d5e0]">{task?.status}</div>
            {task?.commit_sha && <div className="px-3 py-1 rounded bg-[#2a475e] text-[#c7d5e0] font-mono">{task.commit_sha.slice(0,7)}</div>}
            {results?.score !== undefined && (
              <div className={`px-3 py-1 rounded font-bold ${results.score >= 80 ? "bg-green-900 text-green-400" : results.score >= 60 ? "bg-yellow-900 text-yellow-400" : "bg-red-900 text-red-400"}`}>
                Score: {results.score}
              </div>
            )}
          </div>
        </div>

        <div className="flex gap-2 mb-6">
          {(["issues", "improvements", "architecture"] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded text-sm ${activeTab === tab ? "bg-[#66c0f4] text-[#171a21]" : "bg-[#171a21] text-[#c7d5e0] border border-[#2a475e]"}`}
            >
              {tab === "issues" ? `Issues (${issues.length})` : tab === "improvements" ? "Improvements" : "Architecture"}
            </button>
          ))}
        </div>

        {activeTab === "issues" && (
          <div className="bg-[#171a21] rounded-lg border border-[#2a475e] overflow-hidden">
            {issues.length === 0 ? (
              <div className="p-12 text-center text-[#c7d5e0]">No issues found</div>
            ) : (
              <div className="divide-y divide-[#2a475e]">
                {issues.map((issue, i) => (
                  <div key={i} className="p-4 hover:bg-[#2a475e]">
                    <div className="flex items-start gap-3">
                      <span className={`px-2 py-1 rounded text-xs uppercase ${getSeverityColor(issue.severity)}`}>{issue.severity}</span>
                      <div className="flex-1">
                        <h3 className="text-white font-medium">{issue.title}</h3>
                        <p className="text-[#8f98a0] text-sm mt-1">{issue.description}</p>
                        {issue.file_path && <p className="text-[#66c0f4] text-xs mt-2 font-mono">{issue.file_path}{issue.line_number ? `:${issue.line_number}` : ""}</p>}
                        {issue.suggestion && <p className="text-green-400 text-sm mt-2">💡 {issue.suggestion}</p>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "improvements" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-[#171a21] rounded-lg border border-[#2a475e] p-6">
              <h3 className="text-[#66c0f4] font-semibold mb-4">Strengths ✅</h3>
              {strengths.length === 0 ? (
                <p className="text-[#8f98a0]">No strengths recorded</p>
              ) : (
                <ul className="space-y-2">
                  {strengths.map((s, i) => <li key={i} className="text-[#c7d5e0]">• {s}</li>)}
                </ul>
              )}
            </div>
            <div className="bg-[#171a21] rounded-lg border border-[#2a475e] p-6">
              <h3 className="text-[#66c0f4] font-semibold mb-4">Suggested Improvements 💡</h3>
              {improvements.length === 0 ? (
                <p className="text-[#8f98a0]">No improvements suggested</p>
              ) : (
                <ul className="space-y-2">
                  {improvements.map((imp, i) => <li key={i} className="text-[#c7d5e0]">• {imp}</li>)}
                </ul>
              )}
            </div>
          </div>
        )}

        {activeTab === "architecture" && (
          <div className="bg-[#171a21] rounded-lg border border-[#2a475e] p-6">
            <h3 className="text-[#66c0f4] font-semibold mb-4">Architecture Graph</h3>
            <Link href={`/architecture?project=${task?.project_id}`} className="text-[#c7d5e0] hover:underline">
              View full architecture graph →
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}
