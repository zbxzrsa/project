"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { projectApi } from "@/lib/projectApi";
import { apiClient } from "@/lib/api";
import { Project, Review } from "@/types";
import { 
  ArrowLeft, 
  GitBranch, 
  Clock, 
  Play, 
  LogOut,
  Code2,
  FolderKanban,
  LayoutDashboard,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Loader2,
  ChevronRight,
  Activity,
  Shield,
  TrendingUp,
  Lightbulb,
  ExternalLink
} from "lucide-react";

interface ReviewResult {
  summary: string;
  score: number;
  issues: Array<{
    severity: string;
    category: string;
    message: string;
    line?: number;
    suggestion?: string;
  }>;
  strengths: string[];
  improvements: string[];
}

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [codeToReview, setCodeToReview] = useState("");
  const [reviewing, setReviewing] = useState(false);
  const [currentResult, setCurrentResult] = useState<ReviewResult | null>(null);
  const [selectedReview, setSelectedReview] = useState<Review | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    fetchProjectAndReviews();
  }, [router, projectId]);

  const fetchProjectAndReviews = async () => {
    try {
      const [projectData, reviewsData] = await Promise.all([
        projectApi.getById(projectId),
        apiClient.get(`/reviews/?project_id=${projectId}`),
      ]);
      setProject(projectData);
      setReviews(reviewsData.data);
    } catch (err) {
      setError("Failed to load project");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunReview = async (e: React.FormEvent) => {
    e.preventDefault();
    setReviewing(true);
    setCurrentResult(null);

    try {
      const response = await apiClient.post("/reviews", {
        project_id: projectId,
      });
      
      const analyzeResponse = await apiClient.post(`/reviews/${response.data.id}/analyze`, {
        code: codeToReview,
        language: "python",
      });

      setCurrentResult(analyzeResponse.data.results);
      fetchProjectAndReviews();
    } catch (err) {
      setError("Failed to run review");
    } finally {
      setReviewing(false);
      setShowReviewModal(false);
      setCodeToReview("");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    router.push("/login");
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-50 text-green-600 border-green-200";
      case "failed":
        return "bg-red-50 text-red-600 border-red-200";
      case "processing":
        return "bg-yellow-50 text-yellow-600 border-yellow-200";
      default:
        return "bg-gray-50 text-gray-600 border-gray-200";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "high":
        return <AlertTriangle className="w-5 h-5 text-orange-500" />;
      case "medium":
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default:
        return <Activity className="w-5 h-5 text-blue-500" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-600">Loading project...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-lg text-red-600">Project not found</div>
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
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowReviewModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
              >
                <Play className="w-4 h-4" />
                Run Review
              </button>
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
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-gray-500 mb-6">
          <Link href="/projects" className="hover:text-indigo-600 flex items-center gap-1">
            <ArrowLeft className="w-4 h-4" />
            Projects
          </Link>
          <ChevronRight className="w-4 h-4" />
          <span className="text-gray-900 font-medium">{project.name}</span>
        </nav>

        {/* Project Header */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="p-4 bg-indigo-50 rounded-xl">
                <FolderKanban className="w-8 h-8 text-indigo-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
                {project.repository_url && (
                  <a 
                    href={project.repository_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm text-gray-500 hover:text-indigo-600 mt-1"
                  >
                    <GitBranch className="w-4 h-4" />
                    {project.repository_url}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Created {new Date(project.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Review Results */}
        {currentResult && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-6">Latest Review Result</h2>
            
            {/* Score */}
            <div className="flex items-center gap-6 mb-6 p-4 bg-gray-50 rounded-xl">
              <div className={`text-5xl font-bold ${getScoreColor(currentResult.score)}`}>
                {currentResult.score}
              </div>
              <div>
                <div className="text-sm text-gray-500">Quality Score</div>
                <div className="flex items-center gap-2 mt-1">
                  {currentResult.score >= 80 ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : currentResult.score >= 60 ? (
                    <AlertTriangle className="w-5 h-5 text-yellow-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500" />
                  )}
                  <span className="text-gray-700 font-medium">
                    {currentResult.score >= 80 ? "Excellent" : currentResult.score >= 60 ? "Needs Improvement" : "Critical"}
                  </span>
                </div>
              </div>
            </div>

            <p className="text-gray-700 mb-6">{currentResult.summary}</p>
            
            {/* Issues */}
            {currentResult.issues.length > 0 && (
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Shield className="w-5 h-5 text-red-500" />
                  Issues Found ({currentResult.issues.length})
                </h3>
                <div className="space-y-3">
                  {currentResult.issues.map((issue, index) => (
                    <div key={index} className={`p-4 rounded-xl border ${
                      issue.severity === "critical" ? "border-red-200 bg-red-50" :
                      issue.severity === "high" ? "border-orange-200 bg-orange-50" :
                      issue.severity === "medium" ? "border-yellow-200 bg-yellow-50" :
                      "border-blue-200 bg-blue-50"
                    }`}>
                      <div className="flex items-start gap-3">
                        {getSeverityIcon(issue.severity)}
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                              issue.severity === "critical" ? "bg-red-200 text-red-700" :
                              issue.severity === "high" ? "bg-orange-200 text-orange-700" :
                              issue.severity === "medium" ? "bg-yellow-200 text-yellow-700" :
                              "bg-blue-200 text-blue-700"
                            }`}>{issue.severity}</span>
                            <span className="font-medium text-gray-900">{issue.category}</span>
                          </div>
                          <p className="mt-1 text-gray-700">{issue.message}</p>
                          {issue.suggestion && (
                            <p className="mt-2 text-sm text-gray-500 flex items-start gap-2">
                              <Lightbulb className="w-4 h-4 mt-0.5 text-indigo-500" />
                              {issue.suggestion}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Strengths */}
            {currentResult.strengths.length > 0 && (
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  Strengths
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {currentResult.strengths.map((strength, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                      <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                      <span className="text-gray-700 text-sm">{strength}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Improvements */}
            {currentResult.improvements.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-500" />
                  Areas for Improvement
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {currentResult.improvements.map((improvement, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                      <Lightbulb className="w-4 h-4 text-blue-500 flex-shrink-0" />
                      <span className="text-gray-700 text-sm">{improvement}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Review History */}
        <div className="bg-white rounded-xl border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Review History</h2>
          </div>
          {reviews.length === 0 ? (
            <div className="p-12 text-center">
              <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Activity className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No reviews yet</h3>
              <p className="text-gray-500 mb-6 max-w-md mx-auto">
                Run your first code review to get insights into your code quality
              </p>
              <button
                onClick={() => setShowReviewModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
              >
                <Play className="w-4 h-4" />
                Run First Review
              </button>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {reviews.map((review) => (
                <div 
                  key={review.id} 
                  className="px-6 py-4 hover:bg-gray-50 flex items-center justify-between cursor-pointer"
                  onClick={() => setSelectedReview(review)}
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-lg ${getStatusColor(review.status)}`}>
                      {review.status === "completed" ? (
                        <CheckCircle className="w-5 h-5" />
                      ) : review.status === "failed" ? (
                        <XCircle className="w-5 h-5" />
                      ) : (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 font-mono text-sm">
                        {review.id.slice(0, 8)}
                      </p>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <GitBranch className="w-3 h-3" />
                        {review.commit_sha?.slice(0, 8) || "No commit"}
                        <span className="mx-1">•</span>
                        <Clock className="w-3 h-3" />
                        {new Date(review.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(review.status)}`}>
                      {review.status}
                    </span>
                    {review.score && (
                      <span className={`text-lg font-bold ${getScoreColor(review.score)}`}>
                        {review.score}
                      </span>
                    )}
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Review Modal */}
      {showReviewModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-2xl w-full p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Run Code Review</h2>
              <button
                onClick={() => {
                  setShowReviewModal(false);
                  setCodeToReview("");
                }}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <form onSubmit={handleRunReview}>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Paste your code here
                </label>
                <textarea
                  value={codeToReview}
                  onChange={(e) => setCodeToReview(e.target.value)}
                  className="w-full h-64 px-4 py-3 border border-gray-300 rounded-xl font-mono text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder={`def hello_world():
    # Your code here
    print('Hello, World!')`}
                  required
                />
              </div>
              <div className="mt-6 flex gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowReviewModal(false);
                    setCodeToReview("");
                  }}
                  className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={reviewing || !codeToReview}
                  className="flex-1 px-4 py-3 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2"
                >
                  {reviewing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Run Review
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
