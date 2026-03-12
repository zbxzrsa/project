"use client";
import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface GraphNode {
  id: string;
  name: string;
  type: string;
}

export default function ArchitecturePage() {
  const router = useRouter();
  const [projects, setProjects] = useState<{ id: string; name: string }[]>([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [graph, setGraph] = useState<{ nodes: GraphNode[]; edges: any[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [filter, setFilter] = useState("");
  const [zoom, setZoom] = useState(1);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) { router.push("/login"); return; }
    fetchProjects();
  }, [router]);

  useEffect(() => {
    if (selectedProject) fetchGraph();
  }, [selectedProject]);

  const fetchProjects = async () => {
    try {
      const headers = { Authorization: `Bearer ${localStorage.getItem("access_token")}` };
      const res = await fetch("/api/v1/projects", { headers });
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
        if (data.length) setSelectedProject(data[0].id);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const fetchGraph = async () => {
    try {
      const headers = { Authorization: `Bearer ${localStorage.getItem("access_token")}` };
      const res = await fetch(`/api/v1/projects/${selectedProject}/architecture`, { headers });
      if (res.ok) setGraph(await res.json());
    } catch (e) { console.error(e); }
  };

  const analyzeArchitecture = async () => {
    setAnalyzing(true);
    try {
      const headers = { Authorization: `Bearer ${localStorage.getItem("access_token")}` };
      await fetch(`/api/v1/projects/${selectedProject}/analyze`, { headers, method: "POST" });
      await fetchGraph();
    } catch (e) { console.error(e); }
    finally { setAnalyzing(false); }
  };

  const logout = () => { localStorage.clear(); router.push("/login"); };
  
  const getColor = (type: string) => {
    const colors: Record<string, string> = { module: "#3b82f6", class: "#8b5cf6", function: "#10b981", file: "#f59e0b" };
    return colors[type] || "#6b7280";
  };

  const filteredNodes = filter === "all" || !filter ? graph?.nodes || [] : graph?.nodes.filter(n => n.type === filter) || [];
  
  const handleZoomIn = () => setZoom(z => Math.min(2, z + 0.2));
  const handleZoomOut = () => setZoom(z => Math.max(0.4, z - 0.2));
  const handleReset = () => { setZoom(1); setFilter("all"); setSelectedNode(null); };

  const handleExport = (format: string) => {
    window.open(`/api/v1/projects/${selectedProject}/export?format=${format}`, "_blank");
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
                <Link href="/pull-requests" className="px-3 py-2 text-sm rounded text-gray-600 hover:bg-gray-100">Pull Requests</Link>
                <Link href="/architecture" className="px-3 py-2 text-sm rounded bg-gray-100 text-gray-900">Architecture</Link>
              </div>
            </div>
            <button onClick={logout} className="text-sm text-gray-600 hover:text-gray-900">Logout</button>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold text-gray-900">Architecture Analysis</h1>
          <div className="flex gap-2">
            <select value={selectedProject} onChange={e => setSelectedProject(e.target.value)} className="px-3 py-2 border border-gray-300 rounded">
              {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
            <button onClick={analyzeArchitecture} disabled={analyzing} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
              {analyzing ? "Analyzing..." : "Analyze"}
            </button>
          </div>
        </div>

        <div className="flex gap-2 mb-4">
          <button onClick={() => setFilter("all")} className={`px-3 py-1 rounded text-sm ${filter === "all" ? "bg-gray-200" : "bg-white border"}`}>All</button>
          <button onClick={() => setFilter("module")} className={`px-3 py-1 rounded text-sm ${filter === "module" ? "bg-gray-200" : "bg-white border"}`}>Modules</button>
          <button onClick={() => setFilter("class")} className={`px-3 py-1 rounded text-sm ${filter === "class" ? "bg-gray-200" : "bg-white border"}`}>Classes</button>
          <button onClick={() => setFilter("function")} className={`px-3 py-1 rounded text-sm ${filter === "function" ? "bg-gray-200" : "bg-white border"}`}>Functions</button>
          <div className="flex-1"></div>
          <button onClick={handleZoomOut} className="px-3 py-1 border rounded">-</button>
          <button onClick={handleReset} className="px-3 py-1 border rounded">{Math.round(zoom * 100)}%</button>
          <button onClick={handleZoomIn} className="px-3 py-1 border rounded">+</button>
          <button onClick={() => handleExport("svg")} className="px-3 py-1 border rounded">SVG</button>
          <button onClick={() => handleExport("png")} className="px-3 py-1 border rounded">PNG</button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="bg-white border border-gray-200 rounded">
            <div className="px-4 py-3 border-b border-gray-200">
              <h3 className="font-medium text-gray-800">Entities ({filteredNodes.length})</h3>
            </div>
            <div className="max-h-96 overflow-y-auto p-2">
              {filteredNodes.slice(0, 50).map((node) => (
                <div key={node.id} onClick={() => setSelectedNode(node.id)} className={`p-2 rounded cursor-pointer ${selectedNode === node.id ? "bg-blue-50" : "hover:bg-gray-50"}`}>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: getColor(node.type) }}></div>
                    <div className="text-sm text-gray-700">{node.name}</div>
                  </div>
                  <div className="text-xs text-gray-400 ml-5">{node.type}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="lg:col-span-3 bg-white border border-gray-200 rounded min-h-96 p-4">
            {!graph ? (
              <div className="flex items-center justify-center h-full text-gray-500">Select a project and click Analyze</div>
            ) : (
              <div className="flex flex-wrap gap-4 justify-center" style={{ transform: `scale(${zoom})`, transformOrigin: "top center" }}>
                {filteredNodes.slice(0, 40).map((node) => (
                  <div key={node.id} onClick={() => setSelectedNode(node.id)} className={`p-3 rounded border cursor-pointer ${selectedNode === node.id ? "border-blue-500" : "border-gray-200"}`} style={{ backgroundColor: getColor(node.type) + "20", borderLeftColor: getColor(node.type), borderLeftWidth: 3 }}>
                    <div className="font-medium text-gray-900">{node.name}</div>
                    <div className="text-xs text-gray-500">{node.type}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
