"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface DashboardStats {
  totalProjects: number;
  totalReviews: number;
  avgScore: number;
  criticalIssues: number;
}

interface RecentReview {
  id: string;
  projectName: string;
  score: number;
  status: string;
  createdAt: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats>({
    totalProjects: 0,
    totalReviews: 0,
    avgScore: 0,
    criticalIssues: 0,
  });
  const [recentReviews, setRecentReviews] = useState<RecentReview[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    fetchDashboardData();
  }, [router]);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch("/api/v1/dashboard", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data.stats);
        setRecentReviews(data.recent_reviews);
      }
    } catch (error) {
      console.error("Failed to load dashboard:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    router.push("/login");
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <Link href="/dashboard" className="text-xl font-bold text-gray-900">
                AI Code Quality
              </Link>
              <div className="hidden md:flex space-x-4">
                <Link
                  href="/dashboard"
                  className="text-gray-900 hover:text-gray-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Dashboard
                </Link>
                <Link
                  href="/projects"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Projects
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/projects"
                className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
              >
                New Review
              </Link>
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
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-500">Total Projects</div>
              <div className="mt-2 text-3xl font-semibold text-gray-900">
                {stats.totalProjects}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-500">Total Reviews</div>
              <div className="mt-2 text-3xl font-semibold text-gray-900">
                {stats.totalReviews}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-500">Average Score</div>
              <div className={`mt-2 text-3xl font-semibold ${getScoreColor(stats.avgScore)}`}>
                {stats.avgScore}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-500">Critical Issues</div>
              <div className="mt-2 text-3xl font-semibold text-red-600">
                {stats.criticalIssues}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Recent Reviews</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {recentReviews.length === 0 ? (
                <div className="px-6 py-12 text-center text-gray-500">
                  No reviews yet.{" "}
                  <Link href="/projects" className="text-blue-600 hover:text-blue-700">
                    Start your first review
                  </Link>
                </div>
              ) : (
                recentReviews.map((review) => (
                  <div
                    key={review.id}
                    className="px-6 py-4 hover:bg-gray-50 flex items-center justify-between"
                  >
                    <div>
                      <div className="font-medium text-gray-900">{review.projectName}</div>
                      <div className="text-sm text-gray-500">
                        {new Date(review.createdAt).toLocaleString()}
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium ${
                          review.status === "completed"
                            ? "bg-green-100 text-green-800"
                            : "bg-yellow-100 text-yellow-800"
                        }`}
                      >
                        {review.status}
                      </span>
                      <span className={`text-lg font-semibold ${getScoreColor(review.score)}`}>
                        {review.score}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
