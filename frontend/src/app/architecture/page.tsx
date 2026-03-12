"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Project, ArchitectureGraph, ArchitectureNode } from "@/types";
import { 
  LayoutDashboard, 
  FolderKanban, 
  GitBranch,
  Clock,
  LogOut,
  Code2,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Layers
} from "lucide-react";

export default function ArchitecturePage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<string>("");
  const [graphData, setGraphData] = useState<ArchitectureGraph | null>(null);
  const [selectedModule, setSelectedModule] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    fetchProjects();
  }, [router]);

  const fetchProjects = async () => {
    try {
      const response = await fetch("/api/v1/projects", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setProjects(data);
        if (data.length > 0) {
          setSelectedProject(data[0].id);
        }
      }
    } catch (error) {
      console.error("Failed to fetch projects:", error);
    }
  };

  const fetchArchitecture = async (projectId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/projects/${projectId}/architecture`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setGraphData(data);
      }
    } catch (error) {
      console.error("Failed to fetch architecture:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (selectedProject) {
      fetchArchitecture(selectedProject);
    }
  }, [selectedProject]);

  const getNodeColor = (type: string) => {
    switch (type) {
      case "file":
        return "fill-blue-200 stroke-blue-500";
      case "module":
        return "fill-green-200 stroke-green-500";
      case "class":
        return "fill-purple-200 stroke-purple-500";
      case "function":
        return "fill-yellow-200 stroke-yellow-500";
      default:
        return "fill-gray-200 stroke-gray-500";
    }
  };

  const filteredNodes = selectedModule
    ? graphData?.nodes.filter(n => n.name === selectedModule || n.file_path.includes(selectedModule))
    : graphData?.nodes;

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    router.push("/login");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-8">
              <Link href="/dashboard" className="flex items-center gap-2">
                <div className="p-1.5 bg-indigo-600 rounded-lg">
                  <Code2 className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-gray-900">CodeQuality AI</span>
              </Link>
              <div className="hidden md:flex items-center gap-6">
                <Link
                  href="/dashboard"
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  Dashboard
                </Link>
                <Link
                  href="/projects"
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
                >
                  <FolderKanban className="w-4 h-4" />
                  Projects
                </Link>
                <Link
                  href="/pull-requests"
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
                >
                  <GitBranch className="w-4 h-4" />
                  Pull Requests
                </Link>
                <Link
                  href="/architecture"
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg"
                >
                  <Code2 className="w-4 h-4" />
                  Architecture
                </Link>
                <Link
                  href="/analysis-queue"
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
                >
                  <Clock className="w-4 h-4" />
                  Analysis Queue
                </Link>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Architecture</h1>
            <p className="mt-1 text-sm text-gray-500">
              Visualize project architecture and module dependencies
            </p>
          </div>
          <div className="flex items-center gap-4">
            <select
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
              className="px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Select Project</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Module List Sidebar */}
          <div className="lg:col-span-1 bg-white rounded-xl border border-gray-200 p-4">
            <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Layers className="w-4 h-4" />
              Modules
            </h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {graphData?.nodes.filter(n => n.type === "module" || n.type === "class").map((node) => (
                <button
                  key={node.id}
                  onClick={() => setSelectedModule(selectedModule === node.name ? "" : node.name)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                    selectedModule === node.name
                      ? "bg-indigo-100 text-indigo-700"
                      : "hover:bg-gray-100 text-gray-700"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${
                      node.branches?.length > 1 ? "bg-orange-400" : "bg-green-400"
                    }`} />
                    <span className="truncate">{node.name}</span>
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {node.type} • {node.branches?.length || 1} branch(es)
                  </div>
                </button>
              ))}
              {!graphData && (
                <p className="text-sm text-gray-500 text-center py-4">
                  Select a project to view architecture
                </p>
              )}
            </div>
          </div>

          {/* Architecture Graph */}
          <div className="lg:col-span-3 bg-white rounded-xl border border-gray-200">
            {/* Toolbar */}
            <div className="border-b border-gray-200 px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
                  className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  <ZoomOut className="w-4 h-4" />
                </button>
                <span className="text-sm text-gray-500">{Math.round(zoom * 100)}%</span>
                <button
                  onClick={() => setZoom(Math.min(2, zoom + 0.1))}
                  className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  <ZoomIn className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setZoom(1)}
                  className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  <Maximize2 className="w-4 h-4" />
                </button>
              </div>
              {graphData && (
                <div className="text-sm text-gray-500">
                  {graphData.nodeCount} nodes • {graphData.edgeCount} edges
                </div>
              )}
            </div>

            {/* Graph Canvas */}
            <div className="p-4 min-h-[600px] flex items-center justify-center">
              {isLoading ? (
                <div className="flex flex-col items-center gap-4">
                  <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                  <p className="text-gray-600">Loading architecture...</p>
                </div>
              ) : graphData ? (
                <div 
                  className="w-full overflow-auto"
                  style={{ transform: `scale(${zoom})`, transformOrigin: "center" }}
                >
                  {filteredNodes && filteredNodes.length > 0 ? (
                    <div className="flex flex-wrap gap-4 justify-center">
                      {filteredNodes.map((node) => (
                        <div
                          key={node.id}
                          className={`p-4 rounded-lg border-2 ${getNodeColor(node.type)} ${
                            selectedModule === node.name ? "ring-2 ring-indigo-500" : ""
                          }`}
                          onClick={() => setSelectedModule(selectedModule === node.name ? "" : node.name)}
                        >
                          <div className="font-medium text-sm">{node.name}</div>
                          <div className="text-xs text-gray-500 mt-1">{node.type}</div>
                          {node.file_path && (
                            <div className="text-xs text-gray-400 mt-1 truncate max-w-[200px]">
                              {node.file_path}
                            </div>
                          )}
                          {node.branches && node.branches.length > 1 && (
                            <div className="flex gap-1 mt-2">
                              {node.branches.slice(0, 3).map((branch, i) => (
                                <span
                                  key={i}
                                  className="px-2 py-0.5 text-xs bg-orange-100 text-orange-700 rounded"
                                >
                                  {branch}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">No architecture data available</p>
                  )}
                </div>
              ) : (
                <div className="text-center">
                  <Code2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Select a project to view its architecture</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
