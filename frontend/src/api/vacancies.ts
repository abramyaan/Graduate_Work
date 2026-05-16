import apiClient from './client';
import { Vacancy } from '../types';

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
    const response = await apiClient.get<Vacancy[]>('/vacancies?status=active');
    return response.data;
  },
};
