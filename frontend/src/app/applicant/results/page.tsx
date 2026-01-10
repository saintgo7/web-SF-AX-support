'use client';

import { useEvaluation } from '@/hooks';
import { Card, Badge, Table } from '@/components/ui';
import { Column } from '@/components/ui/Table';
import { Evaluation } from '@/types';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

export default function ResultsPage() {
  const { getEvaluations } = useEvaluation();
  const { data: evaluationsData, isLoading } = getEvaluations({ status: 'COMPLETED' });

  const columns: Column<Evaluation>[] = [
    {
      key: 'id',
      header: '평가 ID',
      render: (_, row) => row.id.slice(0, 8),
    },
    {
      key: 'score',
      header: '점수',
      render: (_, row) => (
        <span className="font-semibold">
          {row.score || '-'} / {row.max_score}
        </span>
      ),
    },
    {
      key: 'evaluated_at',
      header: '평가일',
      render: (value) =>
        value ? format(new Date(value as string), 'yyyy-MM-dd HH:mm', { locale: ko }) : '-',
    },
    {
      key: 'feedback',
      header: '피드백',
      render: (value) => (
        <span className="text-sm text-gray-600">
          {value ? (value as string).slice(0, 50) + '...' : '-'}
        </span>
      ),
    },
  ];

  const getScoreBadgeVariant = (score: number, maxScore: number) => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 80) return 'success';
    if (percentage >= 60) return 'warning';
    return 'error';
  };

  const getScoreLabel = (score: number, maxScore: number) => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 80) return '우수';
    if (percentage >= 60) return '보통';
    return '미달';
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">결과 조회</h1>
        <p className="mt-2 text-gray-600">
          평가 결과를 확인하세요
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                평가 완료 내역
              </h2>
              <span className="text-sm text-gray-600">
                총 {evaluationsData?.items?.length || 0}건
              </span>
            </div>

            <Table
              columns={columns}
              data={evaluationsData?.items || []}
              keyField="id"
              emptyMessage="완료된 평가가 없습니다."
            />
          </div>
        </Card>
      )}

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              평균 점수
            </h3>
            <div className="text-3xl font-bold text-blue-600">
              {evaluationsData?.items?.length
                ? (
                    evaluationsData.items.reduce(
                      (sum: number, e: Evaluation) => sum + (e.score || 0),
                      0
                    ) / evaluationsData.items.length
                  ).toFixed(1)
                : '-'}
            </div>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              최고 점수
            </h3>
            <div className="text-3xl font-bold text-green-600">
              {evaluationsData?.items?.length
                ? Math.max(
                    ...evaluationsData.items.map((e: Evaluation) => e.score || 0)
                  )
                : '-'}
            </div>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              완료한 평가
            </h3>
            <div className="text-3xl font-bold text-purple-600">
              {evaluationsData?.items?.length || 0}건
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
