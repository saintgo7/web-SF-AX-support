/**
 * Score types for grading and evaluation scoring system.
 */

/**
 * Category score summary with breakdown.
 */
export interface CategoryScoreSummary {
  category_id: string;
  category_name: string;
  score: number;
  max_score: number;
  percentage: number;
  graded_count: number;
  total_count: number;
}

/**
 * Expert score base fields.
 */
export interface ExpertScoreBase {
  total_score: number;
  max_possible_score: number;
  average_percentage: number;
  graded_count: number;
  total_count: number;
}

/**
 * Expert score response from API.
 */
export interface ExpertScoreResponse extends ExpertScoreBase {
  id: string;
  expert_id: string;
  category_scores: CategoryScoreSummary[];
  rank: number | null;
  percentile: number | null;
  last_calculated_at: string;
}

/**
 * Grading progress for an expert.
 */
export interface GradingProgress {
  total_answers: number;
  graded_answers: number;
  pending_answers: number;
  progress_percentage: number;
  draft_count: number;
  submitted_count: number;
  graded_count: number;
  reviewed_count: number;
}

/**
 * Overall grading statistics for dashboard.
 */
export interface GradingStatistics {
  // Expert stats
  total_experts: number;
  experts_with_submissions: number;
  fully_graded_experts: number;

  // Answer stats
  total_answers: number;
  graded_answers: number;
  pending_answers: number;

  // Score distribution
  average_score: number;
  highest_score: number;
  lowest_score: number;

  // Today's activity
  graded_today: number;

  // Category breakdown
  category_stats: CategoryStats[];
}

/**
 * Category statistics for dashboard.
 */
export interface CategoryStats {
  category_id: string;
  category_name: string;
  total_questions: number;
  total_answers: number;
  graded_answers: number;
  average_score: number;
}

/**
 * AI grade request.
 */
export interface AIGradeRequest {
  answer_id: string;
}

/**
 * AI grade response with suggestion and reasoning.
 */
export interface AIGradeResponse {
  answer_id: string;
  question_id: string;
  suggested_score: number;
  max_score: number;
  confidence: number;
  reasoning: string;
  matched_keywords: string[];
  rubric_coverage: number;
}

/**
 * Score recalculation request.
 */
export interface ScoreRecalculateRequest {
  expert_id: string;
}

/**
 * Score recalculation response.
 */
export interface ScoreRecalculateResponse {
  expert_id: string;
  previous_score: number;
  new_score: number;
  previous_percentage: number;
  new_percentage: number;
  recalculated_at: string;
}

/**
 * Batch grading request.
 */
export interface BatchGradeRequest {
  answer_ids: string[];
}

/**
 * Batch grading response.
 */
export interface BatchGradeResponse {
  graded_count: number;
  failed_count: number;
  results: Array<{
    answer_id: string;
    success: boolean;
    score?: number;
    error?: string;
  }>;
}
