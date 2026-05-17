import apiClient from './client';

export interface ResumeUploadResponse {
  resume_id: number;
  file_path: string;
  file_format: string;
  message: string;
}

export interface Resume {
  resume_id: number;
  file_path: string;
  file_format: string;
  extracted_text: string | null;
  upload_date: string;
  candidate_id: number;
  candidate_last_name: string;
  candidate_first_name: string;
  candidate_patronymic: string | null;
}

export const resumesApi = {
  upload: async (file: File, candidateId: number, vacancyId: number): Promise<ResumeUploadResponse> => {
    // FormData для multipart/form-data запроса
    // Порядок соответствует сигнатуре backend: candidate_id, vacancy_id, file
    const formData = new FormData();

    // Числа передаются как строки (требование FormData API)
    formData.append('candidate_id', candidateId.toString());
    formData.append('vacancy_id', vacancyId.toString());

    // Файл передается как Blob
    formData.append('file', file);

    console.log('=== FormData для /resumes/upload ===');
    console.log('candidate_id:', candidateId, '(тип:', typeof candidateId, ')');
    console.log('vacancy_id:', vacancyId, '(тип:', typeof vacancyId, ')');
    console.log('file:', file.name, file.type, file.size, 'bytes');

    // НЕ устанавливаем Content-Type вручную!
    // Axios автоматически установит multipart/form-data с boundary для FormData
    const response = await apiClient.post<ResumeUploadResponse>(
      '/resumes/upload',
      formData,
      {
        headers: {
          // Явно НЕ указываем Content-Type - пусть Axios сам установит правильный
        }
      }
    );
    return response.data;
  },

  getByVacancy: async (vacancyId: number): Promise<Resume[]> => {
    const response = await apiClient.get<Resume[]>(
      `/resumes/?vacancy_id=${vacancyId}`
    );
    return response.data;
  },

  getByCandidate: async (candidateId: number): Promise<Resume[]> => {
    const response = await apiClient.get<Resume[]>(
      `/resumes/?candidate_id=${candidateId}`
    );
    return response.data;
  },

  delete: async (resumeId: number): Promise<void> => {
    await apiClient.delete(`/resumes/${resumeId}`);
  },
};
