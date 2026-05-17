import apiClient from './client';
import { Candidate, CandidateCreate } from '../types';

export const candidatesApi = {
  getAll: async (): Promise<Candidate[]> => {
    const response = await apiClient.get<Candidate[]>('/candidates');
    return response.data;
  },

  create: async (data: CandidateCreate): Promise<Candidate> => {
    const response = await apiClient.post<Candidate>('/candidates', data);
    return response.data;
  },

  getById: async (id: number): Promise<Candidate> => {
    const response = await apiClient.get<Candidate>(`/candidates/${id}`);
    return response.data;
  },

  update: async (id: number, data: Partial<CandidateCreate>): Promise<Candidate> => {
    const response = await apiClient.put<Candidate>(`/candidates/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/candidates/${id}`);
  },
};
