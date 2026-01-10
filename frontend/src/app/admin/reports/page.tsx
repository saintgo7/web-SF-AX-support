'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, Button, Select, Alert } from '@/components/ui';
import {
  reportsApi,
  SummaryStats,
  ExpertsReport,
  EvaluationsReport,
  MatchingsReport,
  ReportResponse,
} from '@/lib/api/reports';

type ReportType = 'summary' | 'experts' | 'evaluations' | 'matchings' | 'performance';

const REPORT_OPTIONS: { value: ReportType; label: string }[] = [
  { value: 'summary', label: '전체 현황 요약' },
  { value: 'experts', label: '전문가 현황' },
  { value: 'evaluations', label: '평가 결과 분석' },
  { value: 'matchings', label: '매칭 효율 분석' },
];

export default function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState<ReportType | ''>('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedReport, setGeneratedReport] = useState<ReportResponse | null>(null);
  const [summaryStats, setSummaryStats] = useState<SummaryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = useCallback(async () => {
    try {
      setLoading(true);
      const stats = await reportsApi.getSummary();
      setSummaryStats(stats);
    } catch (err) {
      console.error('Failed to fetch summary:', err);
      setError('통계를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  const handleGenerateReport = async () => {
    if (!selectedReport) return;

    setIsGenerating(true);
    setError(null);

    try {
      const report = await reportsApi.generateReport(selectedReport);
      setGeneratedReport(report);
    } catch (err) {
      console.error('Failed to generate report:', err);
      setError('리포트 생성에 실패했습니다.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!generatedReport) return;

    const blob = new Blob([JSON.stringify(generatedReport, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report-${generatedReport.report_type}-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatReportData = (data: Record<string, unknown>): React.ReactNode => {
    return (
      <div className="space-y-4">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="flex justify-between items-center py-2 border-b border-gray-100">
            <span className="text-gray-600">{formatKey(key)}</span>
            <span className="font-medium">
              {typeof value === 'object' && value !== null
                ? JSON.stringify(value)
                : typeof value === 'number'
                ? formatNumber(value)
                : String(value)}
            </span>
          </div>
        ))}
      </div>
    );
  };

  const formatKey = (key: string): string => {
    const translations: Record<string, string> = {
      total_experts: '총 전문가',
      qualified_experts: '자격 보유 전문가',
      pending_experts: '심사 대기 전문가',
      total_questions: '총 문항',
      total_answers: '총 답변',
      graded_answers: '채점 완료',
      pending_grading: '채점 대기',
      average_score: '평균 점수',
      completion_rate: '완료율',
      total_companies: '총 기업',
      total_demands: '총 수요',
      total_matchings: '총 매칭',
      active_matchings: '진행중 매칭',
      total: '총계',
      by_qualification: '자격 상태별',
      by_specialty: '전문 분야별',
      by_education: '학력별',
      recent_registrations: '최근 등록',
      avg_career_years: '평균 경력',
      total_graded: '채점 완료',
      avg_score: '평균 점수',
      score_distribution: '점수 분포',
      by_question_type: '문항 유형별',
      pass_rate: '합격률',
      pending_count: '대기 수',
      by_status: '상태별',
      by_type: '유형별',
      success_rate: '성공률',
      avg_match_score: '평균 매칭 점수',
    };
    return translations[key] || key;
  };

  const formatNumber = (value: number): string => {
    if (value >= 1000) {
      return value.toLocaleString();
    }
    if (value % 1 !== 0) {
      return value.toFixed(1);
    }
    return String(value);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">리포트 생성</h1>
        <p className="mt-2 text-gray-600">다양한 통계 리포트를 생성하고 다운로드하세요</p>
      </div>

      {error && (
        <Alert type="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Quick Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="p-6">
            <p className="text-sm font-medium text-gray-600">전문가 수</p>
            <p className="text-3xl font-bold text-blue-600 mt-2">
              {summaryStats?.total_experts || 0}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              자격: {summaryStats?.qualified_experts || 0}명
            </p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <p className="text-sm font-medium text-gray-600">총 평가 수</p>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {summaryStats?.total_answers || 0}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              채점 완료: {summaryStats?.graded_answers || 0}건
            </p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <p className="text-sm font-medium text-gray-600">평균 점수</p>
            <p className="text-3xl font-bold text-purple-600 mt-2">
              {(summaryStats?.average_score || 0).toFixed(1)}
            </p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <p className="text-sm font-medium text-gray-600">완료율</p>
            <p className="text-3xl font-bold text-yellow-600 mt-2">
              {(summaryStats?.completion_rate || 0).toFixed(1)}%
            </p>
          </div>
        </Card>
      </div>

      {/* Report Generation */}
      <Card>
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">리포트 생성</h2>

          <div className="max-w-md">
            <Select
              label="리포트 유형"
              options={REPORT_OPTIONS}
              placeholder="리포트 유형을 선택하세요"
              value={selectedReport}
              onChange={(e) => {
                setSelectedReport(e.target.value as ReportType);
                setGeneratedReport(null);
              }}
            />

            <div className="mt-4 flex gap-4">
              <Button
                onClick={handleGenerateReport}
                disabled={!selectedReport || isGenerating}
              >
                {isGenerating ? '생성 중...' : '생성하기'}
              </Button>

              {generatedReport && (
                <Button variant="outline" onClick={handleDownload}>
                  다운로드
                </Button>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Generated Report */}
      {generatedReport && (
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                {REPORT_OPTIONS.find((o) => o.value === generatedReport.report_type)?.label ||
                  generatedReport.report_type}
              </h2>
              <span className="text-sm text-gray-500">
                생성 시각: {new Date(generatedReport.generated_at).toLocaleString('ko-KR')}
              </span>
            </div>

            {formatReportData(generatedReport.data)}
          </div>
        </Card>
      )}

      {/* Available Reports */}
      <Card>
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">사용 가능한 리포트</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
              <div className="flex items-center gap-3 mb-3">
                <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="h-5 w-5 text-blue-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
                <h3 className="font-medium text-gray-900">전체 현황 요약</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                시스템 전체의 주요 지표와 통계를 한눈에 확인하세요.
              </p>
              <Button
                size="sm"
                variant="outline"
                className="w-full"
                onClick={() => setSelectedReport('summary')}
              >
                선택
              </Button>
            </div>

            <div className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
              <div className="flex items-center gap-3 mb-3">
                <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="h-5 w-5 text-green-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                  </svg>
                </div>
                <h3 className="font-medium text-gray-900">전문가 현황</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                등록된 전문가들의 자격, 경력 분포를 분석하세요.
              </p>
              <Button
                size="sm"
                variant="outline"
                className="w-full"
                onClick={() => setSelectedReport('experts')}
              >
                선택
              </Button>
            </div>

            <div className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
              <div className="flex items-center gap-3 mb-3">
                <div className="h-10 w-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="h-5 w-5 text-purple-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                </div>
                <h3 className="font-medium text-gray-900">평가 결과 분석</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                평가 결과의 통계, 점수 분포를 확인하세요.
              </p>
              <Button
                size="sm"
                variant="outline"
                className="w-full"
                onClick={() => setSelectedReport('evaluations')}
              >
                선택
              </Button>
            </div>

            <div className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
              <div className="flex items-center gap-3 mb-3">
                <div className="h-10 w-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <svg
                    className="h-5 w-5 text-yellow-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
                    />
                  </svg>
                </div>
                <h3 className="font-medium text-gray-900">매칭 효율 분석</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                매칭 성공률, 평균 점수를 분석하세요.
              </p>
              <Button
                size="sm"
                variant="outline"
                className="w-full"
                onClick={() => setSelectedReport('matchings')}
              >
                선택
              </Button>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
