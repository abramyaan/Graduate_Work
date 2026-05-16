import apiClient from './client';
import { Candidate, CandidateCreate } from '../types';

export const candidatesApi = {
  create: async (data: CandidateCreate): Promise<Candidate> => {
    const response = await apiClient.post<Candidate>('/candidates', data);
    return response.data;
  },

  getById: async (id: number): Promise<Candidate> => {
    const response = await apiClient.get<Candidate>(`/candidates/${id}`);
    return response.data;
  },
};
