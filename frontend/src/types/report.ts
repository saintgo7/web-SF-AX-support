// 보고서 유형
export type ReportType = 'CONSULTING' | 'EVALUATION' | 'SUMMARY';

// 보고서 상태
export type ReportStatus = 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REJECTED';

// 보고서 기본 정보
export interface Report {
  id: string;
  title: string;
  report_type: ReportType;
  consultant_id?: string;
  consultant_name?: string;
  company_id?: string;
  company_name?: string;
  status: ReportStatus;
  created_at: string;
  updated_at: string;
  submitted_at?: string;
  approved_at?: string;
  author_id: string;
  author: string;
}

// 컨설팅 보고서 섹션
export interface ConsultingReportContent {
  // 1. 기본 정보
  consulting_period: string;
  consulting_area: string;

  // 2. 현황 분석
  current_status: string;
  problem_analysis: string;

  // 3. 개선 방안
  improvement_plan: string;
  expected_effect: string;

  // 4. 실행 계획
  action_plan: string;
  timeline: string;

  // 5. 종합 의견
  overall_opinion: string;
}

// 평가 보고서 섹션
export interface EvaluationReportContent {
  // 1. 평가 개요
  evaluation_period: string;
  evaluation_criteria: string;

  // 2. 역량 평가
  technical_competency: string;
  consulting_competency: string;
  communication_competency: string;

  // 3. 성과 평가
  performance_summary: string;
  achievement_rate: string;

  // 4. 종합 의견
  strengths: string;
  improvements: string;
  overall_rating: string;
  overall_opinion: string;
}

// 요약 보고서 섹션
export interface SummaryReportContent {
  // 1. 기간 및 범위
  report_period: string;
  report_scope: string;

  // 2. 활동 요약
  total_consultings: string;
  completed_consultings: string;
  key_achievements: string;

  // 3. 성과 분석
  performance_analysis: string;
  statistics_summary: string;

  // 4. 이슈 및 개선사항
  issues: string;
  improvements: string;

  // 5. 향후 계획
  future_plan: string;
}

// 보고서 상세 (전체 내용 포함)
export interface ReportDetail extends Report {
  content: ConsultingReportContent | EvaluationReportContent | SummaryReportContent;
  attachments?: ReportAttachment[];
  comments?: ReportComment[];
}

// 첨부파일
export interface ReportAttachment {
  id: string;
  filename: string;
  file_size: number;
  file_type: string;
  uploaded_at: string;
}

// 코멘트/피드백
export interface ReportComment {
  id: string;
  author: string;
  content: string;
  created_at: string;
}

// 보고서 생성 요청
export interface CreateReportRequest {
  title: string;
  report_type: ReportType;
  consultant_id?: string;
  company_id?: string;
}

// 보고서 업데이트 요청
export interface UpdateReportRequest {
  title?: string;
  content?: ConsultingReportContent | EvaluationReportContent | SummaryReportContent;
  status?: ReportStatus;
}

// 유형별 라벨
export const REPORT_TYPE_LABELS: Record<ReportType, string> = {
  CONSULTING: '컨설팅 보고서',
  EVALUATION: '평가 보고서',
  SUMMARY: '요약 보고서',
};

// 상태별 라벨
export const REPORT_STATUS_LABELS: Record<ReportStatus, string> = {
  DRAFT: '작성중',
  SUBMITTED: '제출됨',
  APPROVED: '승인됨',
  REJECTED: '반려됨',
};
