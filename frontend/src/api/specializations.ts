import apiClient from './client';
import { Specialization } from '../types';

export const specializationsApi = {
  getAll: async (): Promise<Specialization[]> => {
    const response = await apiClient.get<Specialization[]>('/specializations');
    return response.data;
  },
};
