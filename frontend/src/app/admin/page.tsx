"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api";
import { User, FeatureFlag } from "@/types";

export default function AdminPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [featureFlags, setFeatureFlags] = useState<FeatureFlag[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"users" | "flags">("users");
  const [showFlagModal, setShowFlagModal] = useState(false);
  const [newFlagName, setNewFlagName] = useState("");
  const [newFlagEnabled, setNewFlagEnabled] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    fetchData();
  }, [router]);

  const fetchData = async () => {
    try {
      const userResponse = await apiClient.get("/users/");
      const flagsResponse = await apiClient.get("/feature-flags/");
      setUsers(userResponse.data);
      setFeatureFlags(flagsResponse.data);
    } catch (err) {
      setError("Failed to load admin data");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateFlag = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post("/feature-flags/", {
        name: newFlagName,
        enabled: newFlagEnabled,
        rules: {},
      });
      setShowFlagModal(false);
      setNewFlagName("");
      setNewFlagEnabled(false);
      fetchData();
    } catch (err) {
      setError("Failed to create feature flag");
    }
  };

  const handleToggleFlag = async (flag: FeatureFlag) => {
    try {
      await apiClient.patch(`/feature-flags/${flag.id}`, {
        enabled: !flag.enabled,
      });
      fetchData();
    } catch (err) {
      setError("Failed to update feature flag");
    }
  };

  const handleDeleteFlag = async (flagId: string) => {
    if (!confirm("Are you sure you want to delete this feature flag?")) return;
    try {
      await apiClient.delete(`/feature-flags/${flagId}`);
      fetchData();
    } catch (err) {
      setError("Failed to delete feature flag");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    router.push("/login");
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
            <div className="flex items-center space-x-4">
              <Link href="/projects" className="text-gray-600 hover:text-gray-900">
                &larr; Projects
              </Link>
              <span className="text-xl font-bold text-gray-900">Admin</span>
            </div>
            <div className="flex items-center space-x-4">
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

          <div className="mb-6">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8">
                <button
                  onClick={() => setActiveTab("users")}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === "users"
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700"
                  }`}
                >
                  Users
                </button>
                <button
                  onClick={() => setActiveTab("flags")}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === "flags"
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700"
                  }`}
                >
                  Feature Flags
                </button>
              </nav>
            </div>
          </div>

          {activeTab === "users" && (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-900">{user.email}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{user.full_name || "-"}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{user.role}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs rounded ${
                          user.is_active === "true" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                        }`}>
                          {user.is_active === "true" ? "Active" : "Inactive"}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === "flags" && (
            <div>
              <div className="flex justify-end mb-4">
                <button
                  onClick={() => setShowFlagModal(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Create Feature Flag
                </button>
              </div>

              {featureFlags.length === 0 ? (
                <div className="bg-white rounded-lg shadow p-8 text-center">
                  <p className="text-gray-500 mb-4">No feature flags yet</p>
                  <button
                    onClick={() => setShowFlagModal(true)}
                    className="text-blue-600 hover:text-blue-700"
                  >
                    Create your first feature flag
                  </button>
                </div>
              ) : (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {featureFlags.map((flag) => (
                        <tr key={flag.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 text-sm font-medium text-gray-900">{flag.name}</td>
                          <td className="px-6 py-4">
                            <button
                              onClick={() => handleToggleFlag(flag)}
                              className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                                flag.enabled ? "bg-blue-600" : "bg-gray-200"
                              }`}
                            >
                              <span
                                className={`inline-block h-4 w-4 transform rounded-full bg-white ${
                                  flag.enabled ? "translate-x-6" : "translate-x-1"
                                }`}
                              />
                            </button>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500">
                            {new Date(flag.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <button
                              onClick={() => handleDeleteFlag(flag.id)}
                              className="text-red-600 hover:text-red-700"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {showFlagModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Create Feature Flag</h2>
            <form onSubmit={handleCreateFlag}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Flag Name
                  </label>
                  <input
                    type="text"
                    value={newFlagName}
                    onChange={(e) => setNewFlagName(e.target.value)}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="e.g., new_dashboard"
                    required
                  />
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="enabled"
                    checked={newFlagEnabled}
                    onChange={(e) => setNewFlagEnabled(e.target.checked)}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                  />
                  <label htmlFor="enabled" className="ml-2 block text-sm text-gray-700">
                    Enabled by default
                  </label>
                </div>
              </div>
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowFlagModal(false);
                    setNewFlagName("");
                    setNewFlagEnabled(false);
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
