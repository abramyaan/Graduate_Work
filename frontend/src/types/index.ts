// Типы для API

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  role: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'Admin' | 'Recruiter' | 'Operator';
  full_name: string;
  is_active: boolean;
}

export interface Vacancy {
  id: number;
  title: string;
  description: string;
  required_skills: string[];
  experience_years: number;
  created_at: string;
  status: 'active' | 'closed' | 'draft';
  department?: string;
}

export interface Candidate {
  id: number;
  full_name: string;
  email: string;
  phone: string;
  resume_file_path: string;
  uploaded_at: string;
}

export interface EvaluationResult {
  id: number;
  candidate_id: number;
  candidate: Candidate;
  vacancy_id: number;
  vacancy: Vacancy;
  overall_score: number;
  skills_score: number;
  experience_score: number;
  structure_score: number;
  ats_score: number;
  recommendation: string;
  evaluated_at: string;
  evaluated_by_user_id: number;
}

export interface CategoryScore {
  category_name: string;
  score: number;
  weight: number;
  weighted_score: number;
}

export interface DetailedEvaluation {
  id: number;
  candidate: Candidate;
  vacancy: Vacancy;
  overall_score: number;
  category_scores: CategoryScore[];
  recommendation: string;
  evaluated_at: string;
  evaluator_name: string;
  resume_url?: string;
}

export interface DashboardStats {
  total_vacancies: number;
  active_vacancies: number;
  total_evaluations: number;
  pending_reviews: number;
}

export interface ExportRequest {
  vacancy_id: number;
  format: 'pdf' | 'excel';
  include_details: boolean;
}
