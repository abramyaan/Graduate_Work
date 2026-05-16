/**
 * Константы приложения
 */

export const SCORE_THRESHOLDS = {
  HIGH: 75,
  MEDIUM: 50,
  LOW: 0,
} as const;

export const RECOMMENDATIONS = {
  INVITE: 'Пригласить немедленно',
  POSTPONE: 'Отложить',
  REJECT: 'Отклонить',
} as const;

export const ROLES = {
  ADMIN: 'Admin',
  RECRUITER: 'Recruiter',
  OPERATOR: 'Operator',
} as const;

export const CATEGORY_WEIGHTS = {
  SKILLS: 0.4,
  EXPERIENCE: 0.3,
  STRUCTURE: 0.2,
  ATS: 0.1,
} as const;

export const EXPORT_FORMATS = {
  PDF: 'pdf',
  EXCEL: 'excel',
} as const;

export const VACANCY_STATUS = {
  ACTIVE: 'active',
  CLOSED: 'closed',
  DRAFT: 'draft',
} as const;
