import apiClient from './client';

export interface ResumeUploadResponse {
  resume_id: number;
  file_path: string;
  file_format: string;
  message: string;
}

export const resumesApi = {
  upload: async (file: File, candidateId: number): Promise<ResumeUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('candidate_id', candidateId.toString());

    const response = await apiClient.post<ResumeUploadResponse>(
      '/resumes/upload',
      formData
    );
    return response.data;
  },
};
