import React from 'react';
import {
  ReportDetail,
  ConsultingReportContent,
  EvaluationReportContent,
  SummaryReportContent,
  REPORT_TYPE_LABELS,
  REPORT_STATUS_LABELS,
} from '@/types/report';

interface ReportPrintLayoutProps {
  report: ReportDetail;
}

export default function ReportPrintLayout({ report }: ReportPrintLayoutProps) {
  const today = new Date().toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div
      className="bg-white text-black"
      style={{
        width: '210mm',
        minHeight: '297mm',
        padding: '15mm',
        fontFamily: 'sans-serif',
        fontSize: '11pt',
        lineHeight: '1.6',
      }}
    >
      {/* 헤더 */}
      <div className="border-b-2 border-gray-800 pb-4 mb-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            AX 코칭단 관리 시스템
          </h1>
          <h2 className="text-xl font-semibold text-gray-800 mb-1">
            {report.title}
          </h2>
          <div className="text-sm text-gray-600">
            {REPORT_TYPE_LABELS[report.report_type]} | {REPORT_STATUS_LABELS[report.status]}
          </div>
        </div>
      </div>

      {/* 기본 정보 */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold border-b border-gray-300 pb-1 mb-3">
          기본 정보
        </h3>
        <table className="w-full text-sm">
          <tbody>
            {report.consultant_name && (
              <tr>
                <td className="py-1 font-medium text-gray-600 w-32">담당 컨설턴트</td>
                <td className="py-1">{report.consultant_name}</td>
              </tr>
            )}
            {report.company_name && (
              <tr>
                <td className="py-1 font-medium text-gray-600 w-32">대상 기업</td>
                <td className="py-1">{report.company_name}</td>
              </tr>
            )}
            <tr>
              <td className="py-1 font-medium text-gray-600 w-32">작성자</td>
              <td className="py-1">{report.author}</td>
            </tr>
            <tr>
              <td className="py-1 font-medium text-gray-600 w-32">작성일</td>
              <td className="py-1">{report.created_at}</td>
            </tr>
            <tr>
              <td className="py-1 font-medium text-gray-600 w-32">최종 수정일</td>
              <td className="py-1">{report.updated_at}</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* 보고서 내용 */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold border-b border-gray-300 pb-1 mb-3">
          보고서 내용
        </h3>
        {report.report_type === 'CONSULTING' && (
          <ConsultingContent content={report.content as ConsultingReportContent} />
        )}
        {report.report_type === 'EVALUATION' && (
          <EvaluationContent content={report.content as EvaluationReportContent} />
        )}
        {report.report_type === 'SUMMARY' && (
          <SummaryContent content={report.content as SummaryReportContent} />
        )}
      </div>

      {/* 푸터 */}
      <div className="mt-auto pt-6 border-t border-gray-300 text-center text-xs text-gray-500">
        <p>출력일: {today}</p>
        <p className="mt-1">© 2026 AX 코칭단 관리 시스템. All rights reserved.</p>
      </div>
    </div>
  );
}

// 컨설팅 보고서 내용
function ConsultingContent({ content }: { content: ConsultingReportContent }) {
  return (
    <div className="space-y-4">
      <Section title="1. 컨설팅 개요">
        <InfoRow label="컨설팅 기간" value={content.consulting_period} />
        <InfoRow label="컨설팅 분야" value={content.consulting_area} />
      </Section>

      <Section title="2. 현황 분석">
        <ContentBlock label="현재 현황" value={content.current_status} />
        <ContentBlock label="문제점 분석" value={content.problem_analysis} />
      </Section>

      <Section title="3. 개선 방안">
        <ContentBlock label="개선 계획" value={content.improvement_plan} />
        <ContentBlock label="기대 효과" value={content.expected_effect} />
      </Section>

      <Section title="4. 실행 계획">
        <ContentBlock label="세부 실행 계획" value={content.action_plan} />
        <ContentBlock label="일정" value={content.timeline} />
      </Section>

      <Section title="5. 종합 의견">
        <ContentBlock value={content.overall_opinion} />
      </Section>
    </div>
  );
}

// 평가 보고서 내용
function EvaluationContent({ content }: { content: EvaluationReportContent }) {
  return (
    <div className="space-y-4">
      <Section title="1. 평가 개요">
        <InfoRow label="평가 기간" value={content.evaluation_period} />
        <InfoRow label="평가 기준" value={content.evaluation_criteria} />
      </Section>

      <Section title="2. 역량 평가">
        <ContentBlock label="기술 역량" value={content.technical_competency} />
        <ContentBlock label="컨설팅 역량" value={content.consulting_competency} />
        <ContentBlock label="커뮤니케이션 역량" value={content.communication_competency} />
      </Section>

      <Section title="3. 성과 평가">
        <ContentBlock label="성과 요약" value={content.performance_summary} />
        <InfoRow label="목표 달성률" value={content.achievement_rate} />
      </Section>

      <Section title="4. 종합 의견">
        <ContentBlock label="강점" value={content.strengths} />
        <ContentBlock label="개선 필요 사항" value={content.improvements} />
        <InfoRow label="종합 등급" value={content.overall_rating} />
        <ContentBlock label="종합 의견" value={content.overall_opinion} />
      </Section>
    </div>
  );
}

// 요약 보고서 내용
function SummaryContent({ content }: { content: SummaryReportContent }) {
  return (
    <div className="space-y-4">
      <Section title="1. 보고서 범위">
        <InfoRow label="보고 기간" value={content.report_period} />
        <InfoRow label="보고 범위" value={content.report_scope} />
      </Section>

      <Section title="2. 활동 요약">
        <InfoRow label="총 컨설팅 건수" value={content.total_consultings} />
        <InfoRow label="완료 건수" value={content.completed_consultings} />
        <ContentBlock label="주요 성과" value={content.key_achievements} />
      </Section>

      <Section title="3. 성과 분석">
        <ContentBlock label="성과 분석" value={content.performance_analysis} />
        <ContentBlock label="통계 요약" value={content.statistics_summary} />
      </Section>

      <Section title="4. 이슈 및 개선사항">
        <ContentBlock label="주요 이슈" value={content.issues} />
        <ContentBlock label="개선 사항" value={content.improvements} />
      </Section>

      <Section title="5. 향후 계획">
        <ContentBlock value={content.future_plan} />
      </Section>
    </div>
  );
}

// 섹션 컴포넌트
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-4">
      <h4 className="font-semibold text-gray-800 mb-2">{title}</h4>
      <div className="pl-2">{children}</div>
    </div>
  );
}

// 단일 행 정보
function InfoRow({ label, value }: { label: string; value?: string }) {
  if (!value) return null;
  return (
    <div className="flex py-1 text-sm">
      <span className="font-medium text-gray-600 w-32 flex-shrink-0">{label}:</span>
      <span className="text-gray-900">{value}</span>
    </div>
  );
}

// 콘텐츠 블록
function ContentBlock({ label, value }: { label?: string; value?: string }) {
  if (!value) return null;
  return (
    <div className="mb-3">
      {label && <div className="font-medium text-gray-600 text-sm mb-1">{label}</div>}
      <div className="text-sm text-gray-900 whitespace-pre-wrap bg-gray-50 p-2 rounded">
        {value}
      </div>
    </div>
  );
}
