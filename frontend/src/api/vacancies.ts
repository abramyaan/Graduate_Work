import apiClient from './client';
import { Vacancy, VacancyCreate } from '../types';

export const vacanciesApi = {
  getAll: async (): Promise<Vacancy[]> => {
    const response = await apiClient.get<Vacancy[]>('/vacancies');
    return response.data;
  },

  getById: async (id: number): Promise<Vacancy> => {
    const response = await apiClient.get<Vacancy>(`/vacancies/${id}`);
    return response.data;
  },

  getActive: async (): Promise<Vacancy[]> => {
    const response = await apiClient.get<Vacancy[]>('/vacancies?is_active=true');
    return response.data;
  },

  create: async (data: VacancyCreate): Promise<Vacancy> => {
    const response = await apiClient.post<Vacancy>('/vacancies', data);
    return response.data;
  },

  update: async (id: number, data: Partial<VacancyCreate>): Promise<Vacancy> => {
    const response = await apiClient.put<Vacancy>(`/vacancies/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/vacancies/${id}`);
  },
};
