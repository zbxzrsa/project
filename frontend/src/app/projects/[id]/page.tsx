"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { projectApi } from "@/lib/projectApi";
import { apiClient } from "@/lib/api";
import { Project, Review } from "@/types";

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
        return "bg-green-100 text-green-800";
      case "failed":
        return "bg-red-100 text-red-800";
      case "processing":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg text-red-600">Project not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/projects" className="text-gray-600 hover:text-gray-900">
                &larr; Projects
              </Link>
              <span className="text-xl font-bold text-gray-900">{project.name}</span>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowReviewModal(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Run Review
              </button>
              <button
                onClick={handleLogout}
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="mb-6 bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-2">Project Details</h2>
            {project.repository_url && (
              <p className="text-gray-600">
                Repository: <span className="text-blue-600">{project.repository_url}</span>
              </p>
            )}
            <p className="text-gray-500 text-sm">
              Created: {new Date(project.created_at).toLocaleDateString()}
            </p>
          </div>

          {currentResult && (
            <div className="mb-6 bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Latest Review Result</h2>
              <div className="mb-4">
                <span className="text-3xl font-bold text-blue-600">{currentResult.score}/100</span>
                <span className="text-gray-500 ml-2">Quality Score</span>
              </div>
              <p className="text-gray-700 mb-4">{currentResult.summary}</p>
              
              {currentResult.issues.length > 0 && (
                <div className="mb-4">
                  <h3 className="font-semibold mb-2">Issues Found ({currentResult.issues.length})</h3>
                  <div className="space-y-2">
                    {currentResult.issues.map((issue, index) => (
                      <div key={index} className={`p-3 rounded border-l-4 ${
                        issue.severity === "critical" ? "border-red-500 bg-red-50" :
                        issue.severity === "high" ? "border-orange-500 bg-orange-50" :
                        issue.severity === "medium" ? "border-yellow-500 bg-yellow-50" :
                        "border-blue-500 bg-blue-50"
                      }`}>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 text-xs rounded ${
                            issue.severity === "critical" ? "bg-red-200" :
                            issue.severity === "high" ? "bg-orange-200" :
                            issue.severity === "medium" ? "bg-yellow-200" :
                            "bg-blue-200"
                          }`}>{issue.severity}</span>
                          <span className="font-medium">{issue.category}</span>
                        </div>
                        <p className="mt-1 text-gray-700">{issue.message}</p>
                        {issue.suggestion && (
                          <p className="mt-1 text-sm text-gray-500">Suggestion: {issue.suggestion}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {currentResult.strengths.length > 0 && (
                <div className="mb-4">
                  <h3 className="font-semibold mb-2 text-green-700">Strengths</h3>
                  <ul className="list-disc list-inside text-gray-700">
                    {currentResult.strengths.map((strength, index) => (
                      <li key={index}>{strength}</li>
                    ))}
                  </ul>
                </div>
              )}

              {currentResult.improvements.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2 text-blue-700">Areas for Improvement</h3>
                  <ul className="list-disc list-inside text-gray-700">
                    {currentResult.improvements.map((improvement, index) => (
                      <li key={index}>{improvement}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div>
            <h2 className="text-xl font-bold mb-4">Review History</h2>
            {reviews.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <p className="text-gray-500 mb-4">No reviews yet</p>
                <button
                  onClick={() => setShowReviewModal(true)}
                  className="text-blue-600 hover:text-blue-700"
                >
                  Run your first review
                </button>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Commit</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {reviews.map((review) => (
                      <tr key={review.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm text-gray-900 font-mono">
                          {review.id.slice(0, 8)}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 font-mono">
                          {review.commit_sha?.slice(0, 8) || "-"}
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 text-xs rounded ${getStatusColor(review.status)}`}>
                            {review.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {new Date(review.created_at).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </main>

      {showReviewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Run Code Review</h2>
            <form onSubmit={handleRunReview}>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Paste your code here
                </label>
                <textarea
                  value={codeToReview}
                  onChange={(e) => setCodeToReview(e.target.value)}
                  className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md font-mono text-sm"
                  placeholder="def hello_world():
    # Your code here
    print('Hello, World!')"
                  required
                />
              </div>
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowReviewModal(false);
                    setCodeToReview("");
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={reviewing || !codeToReview}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {reviewing ? "Analyzing..." : "Run Review"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
