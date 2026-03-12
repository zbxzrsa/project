"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AnalysisTask, Project } from "@/types";
import { 
  LayoutDashboard, 
  FolderKanban, 
  GitBranch,
  Clock,
  LogOut,
  Code2,
  Play,
  Pause,
  RotateCcw,
  Trash2,
  Loader2,
  CheckCircle,
  XCircle,
  AlertCircle
} from "lucide-react";

export default function AnalysisQueuePage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<AnalysisTask[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [queueStatus, setQueueStatus] = useState({
    paused: false,
    waiting: 0,
    processing: 0,
    completed_today: 0,
    failed_today: 0,
  });

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    fetchData();
    
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [router]);

  const fetchData = async () => {
    try {
      const headers = {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      };

      const [tasksRes, projectsRes, queueRes] = await Promise.all([
        fetch("/api/v1/tasks", { headers }),
        fetch("/api/v1/projects", { headers }),
        fetch("/api/v1/queue/status", { headers }),
      ]);

      if (tasksRes.ok) {
        const data = await tasksRes.json();
        setTasks(Array.isArray(data) ? data : []);
      }

      if (projectsRes.ok) {
        const data = await projectsRes.json();
        setProjects(data);
      }

      if (queueRes.ok) {
        const data = await queueRes.json();
        setQueueStatus(data);
      }
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePauseQueue = async () => {
    try {
      await fetch("/api/v1/queue/pause", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      fetchData();
    } catch (error) {
      console.error("Failed to pause queue:", error);
    }
  };

  const handleResumeQueue = async () => {
    try {
      await fetch("/api/v1/queue/resume", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      fetchData();
    } catch (error) {
      console.error("Failed to resume queue:", error);
    }
  };

  const handleRetryTask = async (taskId: string) => {
    try {
      await fetch(`/api/v1/tasks/${taskId}/retry`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      fetchData();
    } catch (error) {
      console.error("Failed to retry task:", error);
    }
  };

  const handleCancelTask = async (taskId: string) => {
    try {
      await fetch(`/api/v1/tasks/${taskId}/cancel`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      fetchData();
    } catch (error) {
      console.error("Failed to cancel task:", error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "processing":
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case "queued":
        return <Clock className="w-5 h-5 text-yellow-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800";
      case "failed":
        return "bg-red-100 text-red-800";
      case "processing":
        return "bg-blue-100 text-blue-800";
      case "queued":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    router.push("/login");
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-600">Loading queue...</p>
        </div>
      </div>
    );
  }

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
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
                >
                  <Code2 className="w-4 h-4" />
                  Architecture
                </Link>
                <Link
                  href="/analysis-queue"
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg"
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
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Analysis Queue</h1>
          <p className="mt-1 text-sm text-gray-500">
            Monitor and manage analysis tasks
          </p>
        </div>

        {/* Queue Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Queue Status</div>
            <div className="flex items-center gap-2 mt-2">
              {queueStatus.paused ? (
                <>
                  <Pause className="w-5 h-5 text-yellow-500" />
                  <span className="font-semibold text-yellow-600">Paused</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 text-green-500" />
                  <span className="font-semibold text-green-600">Running</span>
                </>
              )}
            </div>
          </div>
          
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Waiting</div>
            <div className="text-2xl font-semibold text-gray-900 mt-2">
              {queueStatus.waiting}
            </div>
          </div>
          
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Processing</div>
            <div className="text-2xl font-semibold text-blue-600 mt-2">
              {queueStatus.processing}
            </div>
          </div>
          
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Completed Today</div>
            <div className="text-2xl font-semibold text-green-600 mt-2">
              {queueStatus.completed_today}
            </div>
          </div>
          
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="text-sm text-gray-500">Failed Today</div>
            <div className="text-2xl font-semibold text-red-600 mt-2">
              {queueStatus.failed_today}
            </div>
          </div>
        </div>

        {/* Queue Controls */}
        <div className="flex gap-2 mb-6">
          {queueStatus.paused ? (
            <button
              onClick={handleResumeQueue}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Play className="w-4 h-4" />
              Resume Queue
            </button>
          ) : (
            <button
              onClick={handlePauseQueue}
              className="flex items-center gap-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
            >
              <Pause className="w-4 h-4" />
              Pause Queue
            </button>
          )}
        </div>

        {/* Tasks Table */}
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Task
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Project
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Progress
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tasks.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    No tasks in queue
                  </td>
                </tr>
              ) : (
                tasks.map((task) => {
                  const project = projects.find(p => p.id === task.project_id);
                  return (
                    <tr key={task.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {task.branch_name}
                        </div>
                        <div className="text-xs text-gray-500">
                          Stage: {task.stage}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-500">
                          {project?.name || "Unknown"}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(task.status)}
                          <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(task.status)}`}>
                            {task.status}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="w-full max-w-[150px]">
                          <div className="flex justify-between text-xs text-gray-500 mb-1">
                            <span>{task.progress}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-indigo-600 h-2 rounded-full transition-all"
                              style={{ width: `${task.progress}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(task.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="flex justify-end gap-2">
                          {task.status === "failed" && (
                            <button
                              onClick={() => handleRetryTask(task.id)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                              title="Retry"
                            >
                              <RotateCcw className="w-4 h-4" />
                            </button>
                          )}
                          {(task.status === "pending" || task.status === "queued") && (
                            <button
                              onClick={() => handleCancelTask(task.id)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                              title="Cancel"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
