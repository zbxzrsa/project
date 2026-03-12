import { apiClient } from "@/lib/api";
import { Project } from "@/types";

export const projectApi = {
  getAll: async (): Promise<Project[]> => {
    const response = await apiClient.get("/projects/");
    return response.data;
  },

  getById: async (id: string): Promise<Project> => {
    const response = await apiClient.get(`/projects/${id}`);
    return response.data;
  },

  create: async (data: { name: string; repository_url?: string }): Promise<Project> => {
    const response = await apiClient.post("/projects/", data);
    return response.data;
  },

  update: async (id: string, data: { name?: string; repository_url?: string }): Promise<Project> => {
    const response = await apiClient.put(`/projects/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/projects/${id}`);
  },
};
