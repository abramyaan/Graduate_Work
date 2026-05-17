import apiClient from './client';

export interface DashboardStats {
  total_vacancies: number;
  active_vacancies: number;
  total_candidates: number;
  total_resumes: number;
  total_evaluations: number;
  avg_score: number;
  high_score_count: number;
  medium_score_count: number;
  low_score_count: number;
}

export interface VacancyStatsItem {
  vacancy_id: number;
  title: string;
  resume_count: number;
  avg_score: number;
  top_candidate: string | null;
}

export interface RecentEvaluationItem {
  result_id: number;
  candidate_name: string;
  vacancy_title: string;
  overall_score: number;
  recommendation: string;
  analysis_date: string;
}

export const statisticsApi = {
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get<DashboardStats>('/statistics/dashboard');
    return response.data;
  },

  getTopVacancies: async (limit: number = 5): Promise<VacancyStatsItem[]> => {
    const response = await apiClient.get<VacancyStatsItem[]>(
      `/statistics/vacancies/top?limit=${limit}`
    );
    return response.data;
  },

  getRecentEvaluations: async (limit: number = 10): Promise<RecentEvaluationItem[]> => {
    const response = await apiClient.get<RecentEvaluationItem[]>(
      `/statistics/evaluations/recent?limit=${limit}`
    );
    return response.data;
  },
};
