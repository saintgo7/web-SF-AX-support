/**
 * Matching types for expert-demand matching system.
 *
 * Aligned with backend schemas: src/app/schemas/matching.py
 */

// Matching status enum (aligned with backend MatchingStatus)
export type MatchingStatus =
  | 'PROPOSED'
  | 'ACCEPTED'
  | 'REJECTED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CANCELLED';

// Matching type enum
export type MatchingType = 'AUTO' | 'MANUAL';

// Base matching interface
export interface Matching {
  id: string;
  expert_id: string;
  demand_id: string;
  matching_type: MatchingType;
  status: MatchingStatus;
  match_score: number | null;
  score_breakdown: Record<string, unknown> | null;
  matching_reason: string | null;
  expert_response: string | null;
  expert_responded_at: string | null;
  company_feedback: string | null;
  company_rating: number | null;
  matched_by: string | null;
  project_start_date: string | null;
  project_end_date: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Matching with additional details
export interface MatchingWithDetails extends Matching {
  expert_name?: string;
  expert_specialties?: string[];
  demand_title?: string;
  company_name?: string;
}

// Matching list response
export interface MatchingList {
  items: Matching[];
  total: number;
  page: number;
  page_size: number;
}

// Matching summary statistics
export interface MatchingSummary {
  total: number;
  proposed: number;
  accepted: number;
  rejected: number;
  in_progress: number;
  completed: number;
}

// Create matching request
export interface MatchingCreate {
  expert_id: string;
  demand_id: string;
  matching_type?: MatchingType;
  matching_reason?: string;
  match_score?: number;
}

// Update matching request
export interface MatchingUpdate {
  status?: MatchingStatus;
  matching_reason?: string;
  expert_response?: string;
  company_feedback?: string;
  company_rating?: number;
  project_start_date?: string;
  project_end_date?: string;
}

// Expert response to matching proposal
export interface MatchingExpertResponse {
  accept: boolean;
  response_message?: string;
}

// Company feedback for completed matching
export interface MatchingCompanyFeedback {
  rating: number; // 1-5
  feedback?: string;
}

// Auto-match request
export interface AutoMatchRequest {
  demand_id: string;
  max_candidates?: number;
  min_score?: number;
}

// Basic match candidate (for auto-match)
export interface MatchCandidate {
  expert_id: string;
  expert_name: string;
  match_score: number;
  score_breakdown: Record<string, {
    score: number;
    max: number;
    description: string;
  }>;
  specialties: string[] | null;
  qualification_status: string;
}

// Auto-match response
export interface AutoMatchResponse {
  demand_id: string;
  candidates: MatchCandidate[];
  total_candidates: number;
}

// ==============================================================================
// Sprint 6: Enhanced Matching Types (Intelligent Recommendations)
// ==============================================================================

// Detailed score breakdown for intelligent matching
export interface MatchScoreBreakdown {
  specialty: number;      // 40% weight
  qualification: number;  // 15% weight
  career: number;         // 15% weight
  evaluation: number;     // 20% weight
  availability: number;   // 10% weight
}

// Recommended candidate with intelligent scoring
export interface RecommendedCandidate {
  expert_id: string;
  expert_name: string;
  total_score: number;
  score_breakdown: MatchScoreBreakdown;
  recommendation_reasons: string[];
  specialties: string[] | null;
  qualification_status: string;
}

// Recommend request
export interface RecommendRequest {
  demand_id: string;
  top_n?: number;     // default: 10, max: 50
  min_score?: number; // default: 50.0
}

// Recommend response
export interface RecommendResponse {
  demand_id: string;
  demand_title: string | null;
  candidates: RecommendedCandidate[];
  total_candidates: number;
  algorithm_version: string;
}

// Recommendation level type
export type RecommendationLevel =
  | 'HIGHLY_RECOMMENDED'
  | 'RECOMMENDED'
  | 'POSSIBLE'
  | 'NOT_RECOMMENDED';

// Compatibility check response
export interface CompatibilityCheckResponse {
  expert_id: string;
  demand_id: string;
  total_score: number;
  score_breakdown: MatchScoreBreakdown;
  recommendation: RecommendationLevel;
  recommendation_text: string;
  reasons: string[];
  details: Record<string, unknown>;
}

// Matching analytics
export interface MatchingAnalytics {
  status_distribution: Record<MatchingStatus, number>;
  success_rate: number;
  average_match_score: number;
  total_active_matchings: number;
  total_completed: number;
  top_matched_experts: Array<{
    expert_id: string;
    match_count: number;
  }>;
}

// Helper: Get recommendation color based on level
export function getRecommendationColor(level: RecommendationLevel): string {
  switch (level) {
    case 'HIGHLY_RECOMMENDED':
      return 'green';
    case 'RECOMMENDED':
      return 'blue';
    case 'POSSIBLE':
      return 'yellow';
    case 'NOT_RECOMMENDED':
      return 'red';
    default:
      return 'gray';
  }
}

// Helper: Get matching status label in Korean
export function getMatchingStatusLabel(status: MatchingStatus): string {
  const labels: Record<MatchingStatus, string> = {
    PROPOSED: '제안됨',
    ACCEPTED: '수락됨',
    REJECTED: '거절됨',
    IN_PROGRESS: '진행중',
    COMPLETED: '완료',
    CANCELLED: '취소됨',
  };
  return labels[status] || status;
}

// Helper: Get matching status color
export function getMatchingStatusColor(status: MatchingStatus): string {
  const colors: Record<MatchingStatus, string> = {
    PROPOSED: 'blue',
    ACCEPTED: 'green',
    REJECTED: 'red',
    IN_PROGRESS: 'yellow',
    COMPLETED: 'green',
    CANCELLED: 'gray',
  };
  return colors[status] || 'gray';
}
