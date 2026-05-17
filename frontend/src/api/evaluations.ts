import apiClient from './client';
import { EvaluationResult, DetailedEvaluation } from '../types';

export interface EvaluateResultItem {
  result_id: number;
  resume_id: number;
  candidate_name: string;
  overall_score: number;
  recommendation: string;
}

export interface EvaluateResponse {
  message: string;
  count: number;
  results: EvaluateResultItem[];
}

export interface EvaluateRequest {
  vacancy_id: number;
  resume_ids?: number[];
}

export const evaluationsApi = {
  getByVacancy: async (vacancyId: number): Promise<EvaluationResult[]> => {
    const response = await apiClient.get<EvaluationResult[]>(
      `/results/?vacancy_id=${vacancyId}`
    );
    return response.data;
  },

  getById: async (id: number): Promise<DetailedEvaluation> => {
    const response = await apiClient.get<DetailedEvaluation>(`/results/${id}`);
    return response.data;
  },

  runEvaluation: async (vacancyId: number): Promise<{ message: string; count: number }> => {
    const response = await apiClient.post<{ message: string; count: number }>(
      `/results/evaluate`,
      { vacancy_id: vacancyId }
    );
    return response.data;
  },

  evaluate: async (request: EvaluateRequest): Promise<EvaluateResponse> => {
    // Увеличенный timeout для первого запроса (загрузка ML модели может занять до 60 секунд)
    const response = await apiClient.post<EvaluateResponse>(
      `/results/evaluate`,
      request,
      {
        timeout: 120000, // 2 минуты
      }
    );
    return response.data;
  },

  exportResults: async (
    vacancyId: number,
    format: 'pdf' | 'excel'
  ): Promise<Blob> => {
    const response = await apiClient.get(
      `/results/export/${vacancyId}?format=${format}`,
      {
        responseType: 'blob',
      }
    );
    return response.data;
  },
};
