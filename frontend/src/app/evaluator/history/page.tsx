'use client';

import { useEvaluation } from '@/hooks';
import { Card, Badge, Table } from '@/components/ui';
import { Column } from '@/components/ui/Table';
import { Evaluation } from '@/types';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

export default function HistoryPage() {
  const { getEvaluations } = useEvaluation();
  const { data: completedData, isLoading } = getEvaluations({ status: 'COMPLETED' });

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
      key: 'score',
      header: '점수',
      render: (_, row) => (
        <div className="flex items-center gap-2">
          <span className="font-semibold">
            {row.score || 0}
          </span>
          <span className="text-gray-400">/ {row.max_score}</span>
          <Badge variant={row.score && row.score >= row.max_score * 0.8 ? 'success' : 'default'}>
            {row.score && row.score >= row.max_score * 0.8 ? '우수' : '보통'}
          </Badge>
        </div>
      ),
    },
    {
      key: 'evaluated_at',
      header: '채점일',
      render: (value) =>
        value ? format(new Date(value as string), 'yyyy-MM-dd HH:mm', { locale: ko }) : '-',
    },
  ];

  const calculateAverageScore = () => {
    if (!completedData?.items?.length) return 0;
    const total = completedData.items.reduce(
      (sum: number, e: Evaluation) => sum + (e.score || 0),
      0
    );
    return (total / completedData.items.length).toFixed(1);
  };

  const calculateMaxScore = () => {
    if (!completedData?.items?.length) return 0;
    return Math.max(
      ...completedData.items.map((e: Evaluation) => e.score || 0)
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">채점 완료 내역</h1>
        <p className="mt-2 text-gray-600">
          완료된 채점 내역을 확인하세요
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              총 채점 완료
            </h3>
            <p className="text-3xl font-bold text-blue-600">
              {completedData?.items?.length || 0}건
            </p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              평균 점수
            </h3>
            <p className="text-3xl font-bold text-green-600">
              {calculateAverageScore()}점
            </p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              최고 점수
            </h3>
            <p className="text-3xl font-bold text-purple-600">
              {calculateMaxScore()}점
            </p>
          </div>
        </Card>
      </div>

      {/* Completed Evaluations List */}
      <Card>
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            채점 완료 목록
          </h2>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <Table
              columns={columns}
              data={completedData?.items || []}
              keyField="id"
              emptyMessage="완료된 채점이 없습니다."
            />
          )}
        </div>
      </Card>
    </div>
  );
}
