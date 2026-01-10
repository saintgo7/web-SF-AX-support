export type EvaluationStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';

export interface Evaluation {
  id: string;
  application_id: string;
  evaluator_id: string;
  status: EvaluationStatus;
  score?: number;
  max_score: number;
  feedback?: string;
  evaluated_at?: string;
  created_at: string;
  updated_at: string;
}

export type QuestionType = 'SINGLE' | 'MULTIPLE' | 'SHORT' | 'LONG';
export type Difficulty = 'EASY' | 'MEDIUM' | 'HARD';
export type Specialty =
  | 'SMART_FACTORY'
  | 'PRODUCTION_MANAGEMENT'
  | 'QUALITY_MANAGEMENT'
  | 'SAFETY_MANAGEMENT'
  | 'ENERGY_MANAGEMENT'
  | 'LOGISTICS'
  | 'MAINTENANCE'
  | 'OTHER';

export interface QuestionCategory {
  id: string;
  name: string;
  description?: string;
  weight: number;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Question {
  id: string;
  category_id: string;
  q_type: QuestionType;
  content: string;
  options?: Record<string, string>;
  correct_answer?: { value: string | string[] };
  scoring_rubric?: Record<string, string>;
  max_score: number;
  difficulty: Difficulty;
  target_specialties?: Specialty[];
  explanation?: string;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Legacy simple question type for backwards compatibility
export interface SimpleQuestion {
  id: string;
  content: string;
  category: string;
  max_score: number;
  order: number;
}

export interface QuestionListResponse {
  items: Question[];
  total: number;
  skip: number;
  limit: number;
}

export interface Answer {
  question_id: string;
  response: string;
  score?: number;
  evaluator_note?: string;
}

export interface EvaluationSession {
  evaluation_id: string;
  questions: Question[];
  answers: Answer[];
  started_at: string;
  completed_at?: string;
}
