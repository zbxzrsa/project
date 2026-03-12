"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api";

interface APIKey {
  id: string;
  name: string;
  prefix: string;
  expires_at: string | null;
  last_used_at: string | null;
  is_active: boolean;
  created_at: string;
}

interface CreateAPIKeyRequest {
  name: string;
  expires_days?: number;
}

export default function APIKeysPage() {
  const router = useRouter();
  const [keys, setKeys] = useState<APIKey[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");
  const [newKeyExpiry, setNewKeyExpiry] = useState("");
  const [newKeySecret, setNewKeySecret] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchKeys();
  }, []);

  const fetchKeys = async () => {
    try {
      const response = await apiClient.get("/api-keys");
      setKeys(response.data);
    } catch (err) {
      setError("Failed to load API keys");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    try {
      const data: CreateAPIKeyRequest = {
        name: newKeyName,
      };
      
      if (newKeyExpiry) {
        data.expires_days = parseInt(newKeyExpiry);
      }
      
      const response = await apiClient.post("/api-keys", data);
      setNewKeySecret(response.data.key);
      setShowCreateForm(false);
      setNewKeyName("");
      setNewKeyExpiry("");
      fetchKeys();
    } catch (err) {
      setError("Failed to create API key");
    }
  };

  const handleRevokeKey = async (keyId: string) => {
    if (!confirm("Are you sure you want to revoke this API key?")) return;
    
    try {
      await apiClient.delete(`/api-keys/${keyId}`);
      fetchKeys();
    } catch (err) {
      setError("Failed to revoke API key");
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Never";
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button onClick={() => router.push("/projects")} className="text-gray-500 hover:text-gray-700">
                &larr; Back to Projects
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-gray-900">API Keys</h1>
            <button
              onClick={() => setShowCreateForm(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Create API Key
            </button>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {newKeySecret && (
            <div className="mb-4 bg-green-50 border border-green-200 p-4 rounded">
              <h3 className="font-bold text-green-800 mb-2">API Key Created</h3>
              <p className="text-sm text-green-700 mb-2">
                Make sure to copy your API key now. You won&apos;t be able to see it again!
              </p>
              <div className="bg-white p-3 border border-green-300 rounded font-mono text-sm">
                {newKeySecret}
              </div>
              <button
                onClick={() => setNewKeySecret(null)}
                className="mt-2 text-sm text-green-700 underline"
              >
                I&apos;ve copied my key
              </button>
            </div>
          )}

          {showCreateForm && (
            <div className="mb-6 bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-bold mb-4">Create New API Key</h2>
              <form onSubmit={handleCreateKey}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Key Name
                  </label>
                  <input
                    type="text"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="e.g., Production API"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Expires in (days, optional)
                  </label>
                  <input
                    type="number"
                    value={newKeyExpiry}
                    onChange={(e) => setNewKeyExpiry(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Leave empty for no expiration"
                    min="1"
                    max="365"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Create Key
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {isLoading ? (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          ) : keys.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No API keys found. Create one to get started.
            </div>
          ) : (
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {keys.map((key) => (
                  <li key={key.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">{key.name}</h3>
                        <p className="text-sm text-gray-500">
                          Prefix: <code className="bg-gray-100 px-1 rounded">{key.prefix}...</code>
                        </p>
                        <div className="mt-1 text-sm text-gray-500">
                          <span>Created: {formatDate(key.created_at)}</span>
                          {key.expires_at && (
                            <span className="ml-4">Expires: {formatDate(key.expires_at)}</span>
                          )}
                          <span className="ml-4">Last used: {formatDate(key.last_used_at)}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span
                          className={`px-2 py-1 text-xs rounded-full ${
                            key.is_active
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {key.is_active ? "Active" : "Revoked"}
                        </span>
                        {key.is_active && (
                          <button
                            onClick={() => handleRevokeKey(key.id)}
                            className="px-3 py-1 text-sm text-red-600 hover:text-red-800"
                          >
                            Revoke
                          </button>
                        )}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
