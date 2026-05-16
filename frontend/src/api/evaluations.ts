import apiClient from './client';
import { EvaluationResult, DetailedEvaluation } from '../types';

export const evaluationsApi = {
  getByVacancy: async (vacancyId: number): Promise<EvaluationResult[]> => {
    const response = await apiClient.get<EvaluationResult[]>(
      `/evaluations/vacancy/${vacancyId}`
    );
    return response.data;
  },

  getById: async (id: number): Promise<DetailedEvaluation> => {
    const response = await apiClient.get<DetailedEvaluation>(`/evaluations/${id}`);
    return response.data;
  },

  runEvaluation: async (vacancyId: number): Promise<{ message: string; count: number }> => {
    const response = await apiClient.post<{ message: string; count: number }>(
      `/evaluations/run/${vacancyId}`
    );
    return response.data;
  },

  exportResults: async (
    vacancyId: number,
    format: 'pdf' | 'excel'
  ): Promise<Blob> => {
    const response = await apiClient.get(
      `/evaluations/export/${vacancyId}?format=${format}`,
      {
        responseType: 'blob',
      }
    );
    return response.data;
  },
};
