'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { Card, Badge, Button, Input, Select, Textarea } from '@/components/ui';
import {
  ReportDetail,
  ReportType,
  ReportStatus,
  ConsultingReportContent,
  EvaluationReportContent,
  SummaryReportContent,
  REPORT_TYPE_LABELS,
  REPORT_STATUS_LABELS,
} from '@/types/report';
import ReportPrintLayout from '@/components/report/ReportPrintLayout';
import { generatePDF, generateReportFilename } from '@/lib/utils/pdf';

// Mock 데이터 - 실제로는 API에서 가져옴
const mockReportDetails: Record<string, ReportDetail> = {
  '1': {
    id: '1',
    title: '(주)스마트제조 AX 컨설팅 보고서',
    report_type: 'CONSULTING',
    consultant_id: '1',
    consultant_name: '김철수',
    company_id: '1',
    company_name: '(주)스마트제조',
    status: 'SUBMITTED',
    created_at: '2026-01-10',
    updated_at: '2026-01-10',
    author_id: '1',
    author: '홍길동',
    content: {
      consulting_period: '2026.01.10 ~ 2026.01.20',
      consulting_area: 'AI/ML 기반 품질 예측 시스템',
      current_status: '현재 품질 검사는 수작업으로 진행되고 있으며, 불량률이 약 3.5%로 업계 평균 대비 높은 수준입니다.',
      problem_analysis: '1. 실시간 품질 모니터링 부재\n2. 데이터 기반 의사결정 체계 미흡\n3. 설비 노후화로 인한 품질 편차 발생',
      improvement_plan: '1. IoT 센서 기반 실시간 데이터 수집 체계 구축\n2. ML 모델을 활용한 품질 예측 시스템 도입\n3. 대시보드 기반 품질 모니터링 시스템 구축',
      expected_effect: '불량률 50% 감소 (3.5% → 1.75%)\n연간 비용 절감 예상: 약 2억원',
      action_plan: '1단계: 데이터 수집 인프라 구축 (2주)\n2단계: ML 모델 개발 및 테스트 (4주)\n3단계: 시스템 통합 및 교육 (2주)',
      timeline: '총 8주 소요 예정',
      overall_opinion: '스마트제조 도입을 통해 품질 경쟁력을 확보할 수 있을 것으로 판단됩니다. 경영진의 적극적인 지원과 현장 인력의 참여가 성공의 핵심 요소입니다.',
    } as ConsultingReportContent,
  },
  '3': {
    id: '3',
    title: '김철수 컨설턴트 평가 보고서',
    report_type: 'EVALUATION',
    consultant_id: '1',
    consultant_name: '김철수',
    status: 'DRAFT',
    created_at: '2026-01-11',
    updated_at: '2026-01-11',
    author_id: '1',
    author: '홍길동',
    content: {
      evaluation_period: '2025.07 ~ 2026.01',
      evaluation_criteria: 'AX 컨설턴트 역량 평가 기준 v2.0',
      technical_competency: '',
      consulting_competency: '',
      communication_competency: '',
      performance_summary: '',
      achievement_rate: '',
      strengths: '',
      improvements: '',
      overall_rating: '',
      overall_opinion: '',
    } as EvaluationReportContent,
  },
  '4': {
    id: '4',
    title: '2026년 1월 컨설팅 현황 요약',
    report_type: 'SUMMARY',
    status: 'DRAFT',
    created_at: '2026-01-11',
    updated_at: '2026-01-11',
    author_id: '1',
    author: '홍길동',
    content: {
      report_period: '2026년 1월',
      report_scope: '전체 AX 컨설팅 활동',
      total_consultings: '',
      completed_consultings: '',
      key_achievements: '',
      performance_analysis: '',
      statistics_summary: '',
      issues: '',
      improvements: '',
      future_plan: '',
    } as SummaryReportContent,
  },
};

export default function ReportDetailPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const reportId = params.id as string;
  const action = searchParams.get('action');

  const [report, setReport] = useState<ReportDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [activeTab, setActiveTab] = useState<'edit' | 'preview'>('edit');
  const printRef = useRef<HTMLDivElement>(null);

  // 보고서 데이터 로드
  useEffect(() => {
    const loadReport = async () => {
      setIsLoading(true);
      // TODO: 실제 API 호출로 변경
      await new Promise((resolve) => setTimeout(resolve, 500));
      const data = mockReportDetails[reportId];
      if (data) {
        setReport(data);
      }
      setIsLoading(false);
    };
    loadReport();
  }, [reportId]);

  // PDF 다운로드 핸들러
  const handleDownloadPDF = useCallback(async () => {
    if (!report || !printRef.current) return;

    setIsGeneratingPDF(true);
    try {
      const filename = generateReportFilename(report.title, report.created_at);
      await generatePDF(printRef.current, { filename });
    } catch (error) {
      console.error('PDF 생성 오류:', error);
      alert('PDF 생성 중 오류가 발생했습니다.');
    } finally {
      setIsGeneratingPDF(false);
    }
  }, [report]);

  // URL 파라미터로 PDF 다운로드가 요청된 경우 자동 실행
  useEffect(() => {
    if (action === 'pdf' && report?.status === 'APPROVED' && printRef.current && !isGeneratingPDF) {
      // 약간의 딜레이 후 PDF 생성 (DOM 렌더링 대기)
      const timer = setTimeout(() => {
        handleDownloadPDF();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [action, report, isGeneratingPDF, handleDownloadPDF]);

  const isEditable = report?.status === 'DRAFT';

  const handleContentChange = (field: string, value: string) => {
    if (!report || !isEditable) return;
    setReport({
      ...report,
      content: {
        ...report.content,
        [field]: value,
      },
    });
  };

  const handleTitleChange = (value: string) => {
    if (!report || !isEditable) return;
    setReport({ ...report, title: value });
  };

  const handleSave = async () => {
    if (!report) return;
    setIsSaving(true);
    // TODO: 실제 API 호출
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsSaving(false);
    alert('저장되었습니다.');
  };

  const handleSubmit = async () => {
    if (!report) return;
    if (!confirm('보고서를 제출하시겠습니까? 제출 후에는 수정이 불가능합니다.')) return;
    setIsSaving(true);
    // TODO: 실제 API 호출
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setReport({ ...report, status: 'SUBMITTED' });
    setIsSaving(false);
    alert('제출되었습니다.');
  };

  const getStatusBadge = (status: ReportStatus) => {
    const variants: Record<ReportStatus, 'secondary' | 'info' | 'success' | 'error'> = {
      DRAFT: 'secondary',
      SUBMITTED: 'info',
      APPROVED: 'success',
      REJECTED: 'error',
    };
    return <Badge variant={variants[status]}>{REPORT_STATUS_LABELS[status]}</Badge>;
  };

  const getTypeBadge = (type: ReportType) => {
    const variants: Record<ReportType, 'primary' | 'warning' | 'secondary'> = {
      CONSULTING: 'primary',
      EVALUATION: 'warning',
      SUMMARY: 'secondary',
    };
    return <Badge variant={variants[type]}>{REPORT_TYPE_LABELS[type]}</Badge>;
  };

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[400px]">
        <div className="text-gray-500">보고서를 불러오는 중...</div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="p-6">
        <Card>
          <div className="p-8 text-center">
            <div className="text-gray-500 mb-4">보고서를 찾을 수 없습니다.</div>
            <Button variant="outline" onClick={() => router.push('/evaluator/reports')}>
              목록으로 돌아가기
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-start">
        <div>
          <button
            onClick={() => router.push('/evaluator/reports')}
            className="text-sm text-gray-500 hover:text-gray-700 mb-2 flex items-center gap-1"
          >
            ← 목록으로
          </button>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">
              {isEditable ? (
                <Input
                  value={report.title}
                  onChange={(e) => handleTitleChange(e.target.value)}
                  className="text-2xl font-bold"
                />
              ) : (
                report.title
              )}
            </h1>
          </div>
          <div className="flex items-center gap-2 mt-2">
            {getTypeBadge(report.report_type)}
            {getStatusBadge(report.status)}
            <span className="text-sm text-gray-500">
              작성자: {report.author} | 최종 수정: {report.updated_at}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          {isEditable && (
            <>
              <Button variant="outline" onClick={handleSave} disabled={isSaving}>
                {isSaving ? '저장 중...' : '임시 저장'}
              </Button>
              <Button variant="primary" onClick={handleSubmit} disabled={isSaving}>
                제출하기
              </Button>
            </>
          )}
          {report.status === 'APPROVED' && (
            <Button
              variant="secondary"
              onClick={handleDownloadPDF}
              disabled={isGeneratingPDF}
            >
              {isGeneratingPDF ? 'PDF 생성 중...' : 'PDF 다운로드'}
            </Button>
          )}
        </div>
      </div>

      {/* 기본 정보 */}
      <Card>
        <div className="p-4">
          <h2 className="text-lg font-semibold mb-4">기본 정보</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {report.consultant_name && (
              <div>
                <div className="text-sm text-gray-500">담당 컨설턴트</div>
                <div className="font-medium">{report.consultant_name}</div>
              </div>
            )}
            {report.company_name && (
              <div>
                <div className="text-sm text-gray-500">대상 기업</div>
                <div className="font-medium">{report.company_name}</div>
              </div>
            )}
            <div>
              <div className="text-sm text-gray-500">작성일</div>
              <div className="font-medium">{report.created_at}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500">상태</div>
              <div>{getStatusBadge(report.status)}</div>
            </div>
          </div>
        </div>
      </Card>

      {/* 탭 (편집 모드일 때만) */}
      {isEditable && (
        <div className="flex gap-2 border-b">
          <button
            onClick={() => setActiveTab('edit')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'edit'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            편집
          </button>
          <button
            onClick={() => setActiveTab('preview')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'preview'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            미리보기
          </button>
        </div>
      )}

      {/* 보고서 내용 */}
      {activeTab === 'edit' || !isEditable ? (
        <div className="space-y-6">
          {report.report_type === 'CONSULTING' && (
            <ConsultingReportForm
              content={report.content as ConsultingReportContent}
              isEditable={isEditable}
              onChange={handleContentChange}
            />
          )}
          {report.report_type === 'EVALUATION' && (
            <EvaluationReportForm
              content={report.content as EvaluationReportContent}
              isEditable={isEditable}
              onChange={handleContentChange}
            />
          )}
          {report.report_type === 'SUMMARY' && (
            <SummaryReportForm
              content={report.content as SummaryReportContent}
              isEditable={isEditable}
              onChange={handleContentChange}
            />
          )}
        </div>
      ) : (
        <ReportPreview report={report} />
      )}

      {/* 숨겨진 PDF 출력용 레이아웃 */}
      {report.status === 'APPROVED' && (
        <div
          ref={printRef}
          style={{
            position: 'absolute',
            left: '-9999px',
            top: 0,
            visibility: 'hidden',
          }}
        >
          <ReportPrintLayout report={report} />
        </div>
      )}
    </div>
  );
}

// 컨설팅 보고서 폼
function ConsultingReportForm({
  content,
  isEditable,
  onChange,
}: {
  content: ConsultingReportContent;
  isEditable: boolean;
  onChange: (field: string, value: string) => void;
}) {
  return (
    <>
      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-blue-700">1. 컨설팅 개요</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">컨설팅 기간</label>
              {isEditable ? (
                <Input
                  value={content.consulting_period}
                  onChange={(e) => onChange('consulting_period', e.target.value)}
                  placeholder="예: 2026.01.10 ~ 2026.01.20"
                />
              ) : (
                <div className="p-2 bg-gray-50 rounded">{content.consulting_period || '-'}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">컨설팅 분야</label>
              {isEditable ? (
                <Input
                  value={content.consulting_area}
                  onChange={(e) => onChange('consulting_area', e.target.value)}
                  placeholder="예: AI/ML 기반 품질 예측 시스템"
                />
              ) : (
                <div className="p-2 bg-gray-50 rounded">{content.consulting_area || '-'}</div>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-blue-700">2. 현황 분석</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">현재 현황</label>
              {isEditable ? (
                <Textarea
                  value={content.current_status}
                  onChange={(e) => onChange('current_status', e.target.value)}
                  rows={4}
                  placeholder="기업의 현재 상황을 기술하세요..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.current_status || '-'}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">문제점 분석</label>
              {isEditable ? (
                <Textarea
                  value={content.problem_analysis}
                  onChange={(e) => onChange('problem_analysis', e.target.value)}
                  rows={4}
                  placeholder="주요 문제점을 분석하세요..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.problem_analysis || '-'}</div>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-blue-700">3. 개선 방안</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">개선 계획</label>
              {isEditable ? (
                <Textarea
                  value={content.improvement_plan}
                  onChange={(e) => onChange('improvement_plan', e.target.value)}
                  rows={4}
                  placeholder="구체적인 개선 계획을 기술하세요..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.improvement_plan || '-'}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">기대 효과</label>
              {isEditable ? (
                <Textarea
                  value={content.expected_effect}
                  onChange={(e) => onChange('expected_effect', e.target.value)}
                  rows={3}
                  placeholder="예상되는 효과를 기술하세요..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.expected_effect || '-'}</div>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-blue-700">4. 실행 계획</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">세부 실행 계획</label>
              {isEditable ? (
                <Textarea
                  value={content.action_plan}
                  onChange={(e) => onChange('action_plan', e.target.value)}
                  rows={4}
                  placeholder="단계별 실행 계획을 기술하세요..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.action_plan || '-'}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">일정</label>
              {isEditable ? (
                <Input
                  value={content.timeline}
                  onChange={(e) => onChange('timeline', e.target.value)}
                  placeholder="예: 총 8주 소요 예정"
                />
              ) : (
                <div className="p-2 bg-gray-50 rounded">{content.timeline || '-'}</div>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-blue-700">5. 종합 의견</h3>
          {isEditable ? (
            <Textarea
              value={content.overall_opinion}
              onChange={(e) => onChange('overall_opinion', e.target.value)}
              rows={5}
              placeholder="종합적인 의견과 제언을 기술하세요..."
            />
          ) : (
            <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.overall_opinion || '-'}</div>
          )}
        </div>
      </Card>
    </>
  );
}

// 평가 보고서 폼
function EvaluationReportForm({
  content,
  isEditable,
  onChange,
}: {
  content: EvaluationReportContent;
  isEditable: boolean;
  onChange: (field: string, value: string) => void;
}) {
  return (
    <>
      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-orange-700">1. 평가 개요</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">평가 기간</label>
              {isEditable ? (
                <Input
                  value={content.evaluation_period}
                  onChange={(e) => onChange('evaluation_period', e.target.value)}
                  placeholder="예: 2025.07 ~ 2026.01"
                />
              ) : (
                <div className="p-2 bg-gray-50 rounded">{content.evaluation_period || '-'}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">평가 기준</label>
              {isEditable ? (
                <Input
                  value={content.evaluation_criteria}
                  onChange={(e) => onChange('evaluation_criteria', e.target.value)}
                  placeholder="예: AX 컨설턴트 역량 평가 기준 v2.0"
                />
              ) : (
                <div className="p-2 bg-gray-50 rounded">{content.evaluation_criteria || '-'}</div>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-orange-700">2. 역량 평가</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">기술 역량</label>
              {isEditable ? (
                <Textarea
                  value={content.technical_competency}
                  onChange={(e) => onChange('technical_competency', e.target.value)}
                  rows={3}
                  placeholder="기술적 역량에 대한 평가..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.technical_competency || '-'}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">컨설팅 역량</label>
              {isEditable ? (
                <Textarea
                  value={content.consulting_competency}
                  onChange={(e) => onChange('consulting_competency', e.target.value)}
                  rows={3}
                  placeholder="컨설팅 수행 역량에 대한 평가..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.consulting_competency || '-'}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">커뮤니케이션 역량</label>
              {isEditable ? (
                <Textarea
                  value={content.communication_competency}
                  onChange={(e) => onChange('communication_competency', e.target.value)}
                  rows={3}
                  placeholder="의사소통 및 협업 역량에 대한 평가..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.communication_competency || '-'}</div>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-orange-700">3. 성과 평가</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">성과 요약</label>
              {isEditable ? (
                <Textarea
                  value={content.performance_summary}
                  onChange={(e) => onChange('performance_summary', e.target.value)}
                  rows={3}
                  placeholder="주요 성과를 요약하세요..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.performance_summary || '-'}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">목표 달성률</label>
              {isEditable ? (
                <Input
                  value={content.achievement_rate}
                  onChange={(e) => onChange('achievement_rate', e.target.value)}
                  placeholder="예: 95%"
                />
              ) : (
                <div className="p-2 bg-gray-50 rounded">{content.achievement_rate || '-'}</div>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-orange-700">4. 종합 의견</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">강점</label>
                {isEditable ? (
                  <Textarea
                    value={content.strengths}
                    onChange={(e) => onChange('strengths', e.target.value)}
                    rows={3}
                    placeholder="주요 강점..."
                  />
                ) : (
                  <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.strengths || '-'}</div>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">개선 필요 사항</label>
                {isEditable ? (
                  <Textarea
                    value={content.improvements}
                    onChange={(e) => onChange('improvements', e.target.value)}
                    rows={3}
                    placeholder="개선이 필요한 사항..."
                  />
                ) : (
                  <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.improvements || '-'}</div>
                )}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">종합 등급</label>
              {isEditable ? (
                <Select
                  value={content.overall_rating}
                  onChange={(e) => onChange('overall_rating', e.target.value)}
                  options={[
                    { value: '', label: '등급 선택...' },
                    { value: 'S', label: 'S (탁월)' },
                    { value: 'A', label: 'A (우수)' },
                    { value: 'B', label: 'B (양호)' },
                    { value: 'C', label: 'C (보통)' },
                    { value: 'D', label: 'D (미흡)' },
                  ]}
                />
              ) : (
                <div className="p-2 bg-gray-50 rounded">{content.overall_rating || '-'}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">종합 의견</label>
              {isEditable ? (
                <Textarea
                  value={content.overall_opinion}
                  onChange={(e) => onChange('overall_opinion', e.target.value)}
                  rows={4}
                  placeholder="종합적인 평가 의견..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.overall_opinion || '-'}</div>
              )}
            </div>
          </div>
        </div>
      </Card>
    </>
  );
}

// 요약 보고서 폼
function SummaryReportForm({
  content,
  isEditable,
  onChange,
}: {
  content: SummaryReportContent;
  isEditable: boolean;
  onChange: (field: string, value: string) => void;
}) {
  return (
    <>
      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-gray-700">1. 보고서 범위</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">보고 기간</label>
              {isEditable ? (
                <Input
                  value={content.report_period}
                  onChange={(e) => onChange('report_period', e.target.value)}
                  placeholder="예: 2026년 1월"
                />
              ) : (
                <div className="p-2 bg-gray-50 rounded">{content.report_period || '-'}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">보고 범위</label>
              {isEditable ? (
                <Input
                  value={content.report_scope}
                  onChange={(e) => onChange('report_scope', e.target.value)}
                  placeholder="예: 전체 AX 컨설팅 활동"
                />
              ) : (
                <div className="p-2 bg-gray-50 rounded">{content.report_scope || '-'}</div>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-gray-700">2. 활동 요약</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">총 컨설팅 건수</label>
                {isEditable ? (
                  <Input
                    value={content.total_consultings}
                    onChange={(e) => onChange('total_consultings', e.target.value)}
                    placeholder="예: 15건"
                  />
                ) : (
                  <div className="p-2 bg-gray-50 rounded">{content.total_consultings || '-'}</div>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">완료 건수</label>
                {isEditable ? (
                  <Input
                    value={content.completed_consultings}
                    onChange={(e) => onChange('completed_consultings', e.target.value)}
                    placeholder="예: 12건"
                  />
                ) : (
                  <div className="p-2 bg-gray-50 rounded">{content.completed_consultings || '-'}</div>
                )}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">주요 성과</label>
              {isEditable ? (
                <Textarea
                  value={content.key_achievements}
                  onChange={(e) => onChange('key_achievements', e.target.value)}
                  rows={4}
                  placeholder="주요 성과를 기술하세요..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.key_achievements || '-'}</div>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-gray-700">3. 성과 분석</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">성과 분석</label>
              {isEditable ? (
                <Textarea
                  value={content.performance_analysis}
                  onChange={(e) => onChange('performance_analysis', e.target.value)}
                  rows={4}
                  placeholder="성과를 분석하세요..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.performance_analysis || '-'}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">통계 요약</label>
              {isEditable ? (
                <Textarea
                  value={content.statistics_summary}
                  onChange={(e) => onChange('statistics_summary', e.target.value)}
                  rows={3}
                  placeholder="주요 통계 수치를 요약하세요..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.statistics_summary || '-'}</div>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-gray-700">4. 이슈 및 개선사항</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">주요 이슈</label>
              {isEditable ? (
                <Textarea
                  value={content.issues}
                  onChange={(e) => onChange('issues', e.target.value)}
                  rows={4}
                  placeholder="발생한 이슈..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.issues || '-'}</div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">개선 사항</label>
              {isEditable ? (
                <Textarea
                  value={content.improvements}
                  onChange={(e) => onChange('improvements', e.target.value)}
                  rows={4}
                  placeholder="개선이 필요한 사항..."
                />
              ) : (
                <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.improvements || '-'}</div>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-gray-700">5. 향후 계획</h3>
          {isEditable ? (
            <Textarea
              value={content.future_plan}
              onChange={(e) => onChange('future_plan', e.target.value)}
              rows={4}
              placeholder="향후 계획을 기술하세요..."
            />
          ) : (
            <div className="p-3 bg-gray-50 rounded whitespace-pre-wrap">{content.future_plan || '-'}</div>
          )}
        </div>
      </Card>
    </>
  );
}

// 미리보기 컴포넌트
function ReportPreview({ report }: { report: ReportDetail }) {
  return (
    <Card>
      <div className="p-6">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold">{report.title}</h2>
          <p className="text-gray-500 mt-2">
            {REPORT_TYPE_LABELS[report.report_type]} | 작성일: {report.created_at}
          </p>
        </div>

        <div className="prose max-w-none">
          {report.report_type === 'CONSULTING' && (
            <ConsultingPreview content={report.content as ConsultingReportContent} />
          )}
          {report.report_type === 'EVALUATION' && (
            <EvaluationPreview content={report.content as EvaluationReportContent} />
          )}
          {report.report_type === 'SUMMARY' && (
            <SummaryPreview content={report.content as SummaryReportContent} />
          )}
        </div>
      </div>
    </Card>
  );
}

function ConsultingPreview({ content }: { content: ConsultingReportContent }) {
  return (
    <div className="space-y-6">
      <section>
        <h3 className="text-lg font-bold border-b pb-2">1. 컨설팅 개요</h3>
        <p><strong>기간:</strong> {content.consulting_period}</p>
        <p><strong>분야:</strong> {content.consulting_area}</p>
      </section>
      <section>
        <h3 className="text-lg font-bold border-b pb-2">2. 현황 분석</h3>
        <p className="whitespace-pre-wrap">{content.current_status}</p>
        <p className="whitespace-pre-wrap mt-4">{content.problem_analysis}</p>
      </section>
      <section>
        <h3 className="text-lg font-bold border-b pb-2">3. 개선 방안</h3>
        <p className="whitespace-pre-wrap">{content.improvement_plan}</p>
        <p className="whitespace-pre-wrap mt-4"><strong>기대효과:</strong> {content.expected_effect}</p>
      </section>
      <section>
        <h3 className="text-lg font-bold border-b pb-2">4. 실행 계획</h3>
        <p className="whitespace-pre-wrap">{content.action_plan}</p>
        <p><strong>일정:</strong> {content.timeline}</p>
      </section>
      <section>
        <h3 className="text-lg font-bold border-b pb-2">5. 종합 의견</h3>
        <p className="whitespace-pre-wrap">{content.overall_opinion}</p>
      </section>
    </div>
  );
}

function EvaluationPreview({ content }: { content: EvaluationReportContent }) {
  return (
    <div className="space-y-6">
      <section>
        <h3 className="text-lg font-bold border-b pb-2">1. 평가 개요</h3>
        <p><strong>기간:</strong> {content.evaluation_period}</p>
        <p><strong>기준:</strong> {content.evaluation_criteria}</p>
      </section>
      <section>
        <h3 className="text-lg font-bold border-b pb-2">2. 역량 평가</h3>
        <p><strong>기술 역량:</strong></p>
        <p className="whitespace-pre-wrap ml-4">{content.technical_competency}</p>
        <p className="mt-2"><strong>컨설팅 역량:</strong></p>
        <p className="whitespace-pre-wrap ml-4">{content.consulting_competency}</p>
        <p className="mt-2"><strong>커뮤니케이션 역량:</strong></p>
        <p className="whitespace-pre-wrap ml-4">{content.communication_competency}</p>
      </section>
      <section>
        <h3 className="text-lg font-bold border-b pb-2">3. 성과 평가</h3>
        <p className="whitespace-pre-wrap">{content.performance_summary}</p>
        <p><strong>달성률:</strong> {content.achievement_rate}</p>
      </section>
      <section>
        <h3 className="text-lg font-bold border-b pb-2">4. 종합 의견</h3>
        <p><strong>강점:</strong> {content.strengths}</p>
        <p><strong>개선사항:</strong> {content.improvements}</p>
        <p><strong>종합 등급:</strong> {content.overall_rating}</p>
        <p className="whitespace-pre-wrap mt-4">{content.overall_opinion}</p>
      </section>
    </div>
  );
}

function SummaryPreview({ content }: { content: SummaryReportContent }) {
  return (
    <div className="space-y-6">
      <section>
        <h3 className="text-lg font-bold border-b pb-2">1. 보고서 범위</h3>
        <p><strong>기간:</strong> {content.report_period}</p>
        <p><strong>범위:</strong> {content.report_scope}</p>
      </section>
      <section>
        <h3 className="text-lg font-bold border-b pb-2">2. 활동 요약</h3>
        <p><strong>총 컨설팅:</strong> {content.total_consultings}</p>
        <p><strong>완료:</strong> {content.completed_consultings}</p>
        <p className="whitespace-pre-wrap mt-4">{content.key_achievements}</p>
      </section>
      <section>
        <h3 className="text-lg font-bold border-b pb-2">3. 성과 분석</h3>
        <p className="whitespace-pre-wrap">{content.performance_analysis}</p>
        <p className="whitespace-pre-wrap mt-4">{content.statistics_summary}</p>
      </section>
      <section>
        <h3 className="text-lg font-bold border-b pb-2">4. 이슈 및 개선사항</h3>
        <p><strong>이슈:</strong></p>
        <p className="whitespace-pre-wrap ml-4">{content.issues}</p>
        <p className="mt-2"><strong>개선사항:</strong></p>
        <p className="whitespace-pre-wrap ml-4">{content.improvements}</p>
      </section>
      <section>
        <h3 className="text-lg font-bold border-b pb-2">5. 향후 계획</h3>
        <p className="whitespace-pre-wrap">{content.future_plan}</p>
      </section>
    </div>
  );
}
