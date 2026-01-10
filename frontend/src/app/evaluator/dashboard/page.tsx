'use client';

import { useAuth } from '@/hooks';
import { useEvaluation } from '@/hooks';
import { Card, Badge, Table } from '@/components/ui';
import { Column } from '@/components/ui/Table';
import { Evaluation, GradingStatistics } from '@/types';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import Link from 'next/link';

/**
 * Progress bar component for visualization.
 */
function ProgressBar({ value, max, color = 'blue' }: { value: number; max: number; color?: string }) {
  const percentage = max > 0 ? (value / max) * 100 : 0;
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    purple: 'bg-purple-500',
  };

  return (
    <div className="w-full bg-gray-200 rounded-full h-2.5">
      <div
        className={`${colorClasses[color] || colorClasses.blue} h-2.5 rounded-full transition-all duration-300`}
        style={{ width: `${Math.min(percentage, 100)}%` }}
      />
    </div>
  );
}

/**
 * Statistics card component.
 */
function StatCard({
  title,
  value,
  subtitle,
  icon,
  iconBg,
  iconColor,
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  iconBg: string;
  iconColor: string;
}) {
  return (
    <Card>
      <div className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className={`text-3xl font-bold mt-2 ${iconColor}`}>{value}</p>
            {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
          </div>
          <div className={`h-12 w-12 ${iconBg} rounded-full flex items-center justify-center`}>
            {icon}
          </div>
        </div>
      </div>
    </Card>
  );
}

export default function EvaluatorDashboard() {
  const { user } = useAuth();
  const { getEvaluations, getGradingStatistics, getPendingByExpert } = useEvaluation();

  // Fetch grading statistics
  const { data: statsData, isLoading: statsLoading } = getGradingStatistics();
  const stats: GradingStatistics | undefined = statsData;

  // Fetch pending evaluations
  const { data: pendingData } = getEvaluations({ status: 'PENDING' });
  const { data: inProgressData } = getEvaluations({ status: 'IN_PROGRESS' });
  const { data: completedData } = getEvaluations({ status: 'COMPLETED' });

  // Fetch pending by expert
  const { data: pendingByExpert } = getPendingByExpert();

  const columns: Column<Evaluation>[] = [
    {
      key: 'id',
      header: '평가 ID',
      render: (_, row) => row.id.slice(0, 8),
    },
    {
      key: 'application_id',
      header: '신청서 ID',
      render: (_, row) => row.application_id.slice(0, 8),
    },
    {
      key: 'status',
      header: '상태',
      render: (value) => {
        const variant = value === 'COMPLETED' ? 'success' :
                        value === 'IN_PROGRESS' ? 'warning' : 'default';
        const label = value === 'COMPLETED' ? '완료' :
                      value === 'IN_PROGRESS' ? '진행중' : '대기';
        return <Badge variant={variant}>{label}</Badge>;
      },
    },
    {
      key: 'created_at',
      header: '생성일',
      render: (value) => format(new Date(value as string), 'yyyy-MM-dd', { locale: ko }),
    },
  ];

  const recentEvaluations = [
    ...(pendingData?.items || []).slice(0, 2),
    ...(inProgressData?.items || []).slice(0, 2),
    ...(completedData?.items || []).slice(0, 2),
  ].slice(0, 5);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            평가위원 대시보드
          </h1>
          <p className="mt-2 text-gray-600">
            환영합니다, {user?.name}님
          </p>
        </div>
        <Link
          href="/evaluator/pending"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          채점 시작하기
          <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Link>
      </div>

      {/* Main Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="채점 대기"
          value={stats?.pending_answers || pendingData?.items?.length || 0}
          subtitle="답변 수"
          iconBg="bg-blue-100"
          iconColor="text-blue-600"
          icon={
            <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />

        <StatCard
          title="오늘 채점"
          value={stats?.graded_today || 0}
          subtitle="답변 수"
          iconBg="bg-green-100"
          iconColor="text-green-600"
          icon={
            <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />

        <StatCard
          title="평균 점수"
          value={stats?.average_score ? `${stats.average_score.toFixed(1)}%` : '-'}
          subtitle="전체 평균"
          iconBg="bg-purple-100"
          iconColor="text-purple-600"
          icon={
            <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          }
        />

        <StatCard
          title="전문가 현황"
          value={`${stats?.fully_graded_experts || 0}/${stats?.experts_with_submissions || 0}`}
          subtitle="채점 완료/제출"
          iconBg="bg-yellow-100"
          iconColor="text-yellow-600"
          icon={
            <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          }
        />
      </div>

      {/* Grading Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Overall Progress */}
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">전체 채점 진행률</h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-600">완료된 답변</span>
                  <span className="text-sm font-medium">
                    {stats?.graded_answers || 0} / {stats?.total_answers || 0}
                  </span>
                </div>
                <ProgressBar
                  value={stats?.graded_answers || 0}
                  max={stats?.total_answers || 1}
                  color="green"
                />
              </div>

              <div className="pt-4 border-t">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-green-600">{stats?.highest_score?.toFixed(1) || '-'}%</p>
                    <p className="text-xs text-gray-500">최고 점수</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-blue-600">{stats?.average_score?.toFixed(1) || '-'}%</p>
                    <p className="text-xs text-gray-500">평균 점수</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-red-600">{stats?.lowest_score?.toFixed(1) || '-'}%</p>
                    <p className="text-xs text-gray-500">최저 점수</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Pending by Expert */}
        <Card>
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">전문가별 대기 현황</h2>
              <Link href="/evaluator/pending" className="text-sm text-blue-600 hover:underline">
                전체 보기
              </Link>
            </div>
            <div className="space-y-3">
              {pendingByExpert?.slice(0, 5).map((expert) => (
                <div key={expert.expert_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{expert.expert_name}</p>
                    <p className="text-xs text-gray-500">{expert.pending_count}개 답변 대기</p>
                  </div>
                  <Link
                    href={`/evaluator/pending?expert_id=${expert.expert_id}`}
                    className="text-sm text-blue-600 hover:underline"
                  >
                    채점하기
                  </Link>
                </div>
              ))}
              {(!pendingByExpert || pendingByExpert.length === 0) && (
                <p className="text-center text-gray-500 py-4">대기 중인 답변이 없습니다.</p>
              )}
            </div>
          </div>
        </Card>
      </div>

      {/* Category Statistics */}
      {stats?.category_stats && stats.category_stats.length > 0 && (
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">카테고리별 채점 현황</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {stats.category_stats.map((cat) => (
                <div key={cat.category_id} className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-gray-900">{cat.category_name}</h3>
                  <div className="mt-2">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-500">진행률</span>
                      <span>{cat.graded_answers}/{cat.total_answers}</span>
                    </div>
                    <ProgressBar
                      value={cat.graded_answers}
                      max={cat.total_answers || 1}
                      color="blue"
                    />
                  </div>
                  <p className="mt-2 text-sm text-gray-600">
                    평균 점수: <span className="font-medium">{cat.average_score?.toFixed(1) || '-'}%</span>
                  </p>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Recent Evaluations */}
      <Card>
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            최근 평가 목록
          </h2>

          <Table
            columns={columns}
            data={recentEvaluations}
            keyField="id"
            emptyMessage="평가가 없습니다."
          />
        </div>
      </Card>
    </div>
  );
}
