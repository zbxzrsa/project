"use client";
import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Project, ArchitectureGraph } from "@/types";

export default function ArchitecturePage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [sel, setSel] = useState("");
  const [graph, setGraph] = useState<ArchitectureGraph | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [zoom, setZoom] = useState(1);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const t = localStorage.getItem("access_token");
    if (!t) { router.push("/login"); return; }
    fetch("/api/v1/projects",{headers:{Authorization:`Bearer ${t}`}}).then(r=>r.ok&&r.json()).then(d=>{setProjects(d);if(d.length)setSel(d[0].id);}).finally(()=>setLoading(false));
  },[router]);

  useEffect(() => { if(sel) fetch(`/api/v1/projects/${sel}/architecture`,{headers:{Authorization:`Bearer ${localStorage.getItem("access_token")!}}).then(r=>r.ok&&r.json()).then(setGraph); },[sel]);

  const logout = () => { localStorage.clear(); router.push("/login"); };
  
  const getColor = (t:string) => {
    if (t === "file") return "bg-blue-900 border-blue-700";
    if (t === "module") return "bg-green-900 border-green-700";
    if (t === "class") return "bg-purple-900 border-purple-700";
    if (t === "function") return "bg-yellow-900 border-yellow-700";
    return "bg-gray-800 border-gray-700";
  };

  const getBorderColor = (t:string) => {
    if (t === "file") return "hover:border-blue-500";
    if (t === "module") return "hover:border-green-500";
    if (t === "class") return "hover:border-purple-500";
    if (t === "function") return "hover:border-yellow-500";
    return "hover:border-gray-500";
  };

  const filteredNodes = filter === "all" ? graph?.nodes : graph?.nodes.filter(n => n.type === filter) || [];
  
  const handleZoomIn = () => setZoom(z => Math.min(2, z + 0.2));
  const handleZoomOut = () => setZoom(z => Math.max(0.4, z - 0.2));
  const handleReset = () => { setZoom(1); setFilter("all"); setSelectedNode(null); };

  const handleExport = (format: string) => {
    if (!graph) return;
    const data = format === "json" ? JSON.stringify(graph, null, 2) : `Nodes: ${graph.nodeCount}\nEdges: ${graph.edgeCount}`;
    const blob = new Blob([data], { type: format === "json" ? "application/json" : "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `architecture.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) return <div className="min-h-screen bg-[#1b2838] flex items-center justify-center"><div className="text-[#66c0f4] text-xl">Loading...</div></div>;

  const nav = [
    {h:"/dashboard",l:"Dashboard"},
    {h:"/projects",l:"Projects"},
    {h:"/pull-requests",l:"Pull Requests"},
    {h:"/architecture",l:"Architecture"},
    {h:"/analysis-queue",l:"Analysis Queue"},
    {h:"/settings",l:"Settings"},
  ];

  return (
    <div className="min-h-screen bg-[#1b2838]">
      <nav className="bg-[#171a21] border-b border-[#2a475e]">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-8">
              <Link href="/dashboard" className="text-2xl font-bold text-[#66c0f4]">CodeQuality AI</Link>
              <div className="hidden md:flex gap-1">
                {nav.map(n=>(<Link key={n.h} href={n.h} className={`px-4 py-2 rounded text-sm ${n.h==="/architecture"?"bg-[#66c0f4] text-[#171a21]":"text-[#c7d5e0] hover:bg-[#2a475e]"}`}>{n.l}</Link>))}
              </div>
            </div>
            <button onClick={logout} className="text-[#c7d5e0] hover:text-white text-sm">Logout</button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between mb-6">
          <h1 className="text-3xl font-bold text-white">Architecture</h1>
          <select value={sel} onChange={e=>setSel(e.target.value)} className="px-4 py-2 bg-[#0f1319] border border-[#3d5a73] text-white rounded">
            {projects.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>

        <div className="flex gap-2 mb-4">
          <button onClick={handleZoomOut} className="px-3 py-1 bg-[#171a21] border border-[#2a475e] text-white rounded hover:bg-[#2a475e]">-</button>
          <span className="px-3 py-1 text-white">{Math.round(zoom*100)}%</span>
          <button onClick={handleZoomIn} className="px-3 py-1 bg-[#171a21] border border-[#2a475e] text-white rounded hover:bg-[#2a475e]">+</button>
          <button onClick={handleReset} className="px-3 py-1 bg-[#171a21] border border-[#2a475e] text-white rounded hover:bg-[#2a475e] ml-4">Reset</button>
          <select value={filter} onChange={e=>setFilter(e.target.value)} className="ml-4 px-3 py-1 bg-[#0f1319] border border-[#3d5a73] text-white rounded">
            <option value="all">All Types</option>
            <option value="module">Modules</option>
            <option value="class">Classes</option>
            <option value="function">Functions</option>
            <option value="file">Files</option>
          </select>
          <div className="ml-auto flex gap-2">
            <button onClick={()=>handleExport("json")} className="px-3 py-1 bg-[#171a21] border border-[#2a475e] text-white rounded hover:bg-[#2a475e]">Export JSON</button>
            <button onClick={()=>handleExport("txt")} className="px-3 py-1 bg-[#171a21] border border-[#2a475e] text-white rounded hover:bg-[#2a475e]">Export TXT</button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="bg-[#171a21] rounded-lg border border-[#2a475e] p-4">
            <h3 className="text-[#66c0f4] font-semibold mb-4">Modules ({filteredNodes.length})</h3>
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {filteredNodes.map(n=>(
                <div key={n.id} onClick={()=>setSelectedNode(selectedNode===n.id?null:n.id)} 
                     className={`p-3 rounded cursor-pointer ${getColor(n.type)} border ${getBorderColor(n.type)} ${selectedNode===n.id?"ring-2 ring-white":""}`}>
                  <div className="text-white font-medium">{n.name}</div>
                  <div className="text-[#8f98a0] text-xs">{n.type}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="lg:col-span-3 bg-[#171a21] rounded-lg border border-[#2a475e] min-h-[500px] p-6 overflow-auto" ref={containerRef}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-[#66c0f4] font-semibold">
                Graph View {graph && `(${filteredNodes.length} nodes, ${graph.edgeCount} edges)`}
              </h3>
              {selectedNode && <button onClick={()=>setSelectedNode(null)} className="text-[#66c0f4] hover:underline">Clear selection</button>}
            </div>
            {!graph ? <div className="text-[#c7d5e0] text-center py-20">Select a project</div> : filteredNodes.length === 0 ? <div className="text-[#c7d5e0] text-center py-20">No nodes found</div> : (
              <div className="relative" style={{transform:`scale(${zoom})`, transformOrigin:"top left", minWidth:"100%", minHeight:"400px"}}>
                {filteredNodes.map((node, i) => {
                  const x = (i % 5) * 200 + 50;
                  const y = Math.floor(i / 5) * 150 + 50;
                  return (
                    <div key={node.id} 
                         onClick={()=>setSelectedNode(node.id)}
                         className={`absolute p-4 rounded-lg border-2 cursor-pointer transition-all ${getColor(node.type)} ${getBorderColor(node.type)} ${selectedNode===node.id?"ring-2 ring-white":""}`}
                         style={{left:x, top:y}}>
                      <div className="text-white font-medium whitespace-nowrap">{node.name}</div>
                      <div className="text-[#8f98a0] text-xs">{node.type}</div>
                      {node.file_path && <div className="text-[#8f98a0] text-xs mt-1 truncate max-w-[150px]">{node.file_path}</div>}
                    </div>
                  );
                })}
              </div>
            )}
            {filteredNodes.length > 20 && <div className="text-[#8f98a0] text-sm mt-4">Showing first 20 nodes. Use filter to narrow down.</div>}
          </div>
        </div>
      </main>
    </div>
  );
}
