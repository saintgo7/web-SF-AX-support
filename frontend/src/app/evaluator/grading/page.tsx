'use client';

import { useState } from 'react';
import { Card, Badge, Input, Select, Table, Button } from '@/components/ui';

interface GradingItem {
  id: string;
  consultant_name: string;
  question_category: string;
  question_type: 'ESSAY' | 'SHORT' | 'MULTIPLE';
  submitted_at: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
  score?: number;
  max_score: number;
  graded_at?: string;
}

const mockGradingItems: GradingItem[] = [
  {
    id: '1',
    consultant_name: '김철수',
    question_category: 'ML 역량',
    question_type: 'ESSAY',
    submitted_at: '2026-01-10 14:30',
    status: 'PENDING',
    max_score: 20,
  },
  {
    id: '2',
    consultant_name: '김철수',
    question_category: 'DL 역량',
    question_type: 'ESSAY',
    submitted_at: '2026-01-10 14:35',
    status: 'PENDING',
    max_score: 20,
  },
  {
    id: '3',
    consultant_name: '이영희',
    question_category: 'CV 역량',
    question_type: 'ESSAY',
    submitted_at: '2026-01-09 10:20',
    status: 'IN_PROGRESS',
    max_score: 20,
  },
  {
    id: '4',
    consultant_name: '박민수',
    question_category: 'ML 역량',
    question_type: 'SHORT',
    submitted_at: '2026-01-08 16:00',
    status: 'COMPLETED',
    score: 18,
    max_score: 20,
    graded_at: '2026-01-09 09:00',
  },
  {
    id: '5',
    consultant_name: '이영희',
    question_category: '컨설팅 수행계획',
    question_type: 'ESSAY',
    submitted_at: '2026-01-09 10:25',
    status: 'COMPLETED',
    score: 16,
    max_score: 20,
    graded_at: '2026-01-10 11:00',
  },
];

export default function GradingPage() {
  const [items, setItems] = useState<GradingItem[]>(mockGradingItems);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState<'pending' | 'completed'>('pending');

  const filteredItems = items.filter((item) => {
    const matchesSearch = item.consultant_name.includes(searchTerm);
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
    const matchesTab =
      activeTab === 'pending'
        ? item.status === 'PENDING' || item.status === 'IN_PROGRESS'
        : item.status === 'COMPLETED';
    return matchesSearch && matchesStatus && matchesTab;
  });

  const pendingCount = items.filter(
    (i) => i.status === 'PENDING' || i.status === 'IN_PROGRESS'
  ).length;
  const completedCount = items.filter((i) => i.status === 'COMPLETED').length;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING':
        return <Badge variant="warning">대기중</Badge>;
      case 'IN_PROGRESS':
        return <Badge variant="info">채점중</Badge>;
      case 'COMPLETED':
        return <Badge variant="success">완료</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'ESSAY':
        return <Badge variant="secondary">서술형</Badge>;
      case 'SHORT':
        return <Badge variant="secondary">단답형</Badge>;
      case 'MULTIPLE':
        return <Badge variant="secondary">객관식</Badge>;
      default:
        return <Badge>{type}</Badge>;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">평가 채점</h1>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-gray-500">전체 답변</div>
          <div className="text-2xl font-bold text-blue-600">{items.length}건</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-500">채점 대기</div>
          <div className="text-2xl font-bold text-yellow-600">{pendingCount}건</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-500">채점 완료</div>
          <div className="text-2xl font-bold text-green-600">{completedCount}건</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-500">완료율</div>
          <div className="text-2xl font-bold text-purple-600">
            {((completedCount / items.length) * 100).toFixed(0)}%
          </div>
        </Card>
      </div>

      {/* 탭 */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab('pending')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'pending'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          채점 대기 ({pendingCount})
        </button>
        <button
          onClick={() => setActiveTab('completed')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'completed'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          채점 완료 ({completedCount})
        </button>
      </div>

      {/* 필터 */}
      <Card className="p-4">
        <div className="flex gap-4">
          <div className="flex-1">
            <Input
              placeholder="컨설턴트명으로 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          {activeTab === 'pending' && (
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              options={[
                { value: 'all', label: '전체 상태' },
                { value: 'PENDING', label: '대기중' },
                { value: 'IN_PROGRESS', label: '채점중' },
              ]}
            />
          )}
        </div>
      </Card>

      {/* 채점 목록 */}
      <Card>
        <Table>
          <Table.Head>
            <Table.Row>
              <Table.Header>컨설턴트</Table.Header>
              <Table.Header>평가영역</Table.Header>
              <Table.Header>문항유형</Table.Header>
              <Table.Header>제출시간</Table.Header>
              <Table.Header>상태</Table.Header>
              {activeTab === 'completed' && (
                <>
                  <Table.Header>점수</Table.Header>
                  <Table.Header>채점시간</Table.Header>
                </>
              )}
              <Table.Header>작업</Table.Header>
            </Table.Row>
          </Table.Head>
          <Table.Body>
            {filteredItems.map((item) => (
              <Table.Row key={item.id}>
                <Table.Cell className="font-medium">{item.consultant_name}</Table.Cell>
                <Table.Cell>{item.question_category}</Table.Cell>
                <Table.Cell>{getTypeBadge(item.question_type)}</Table.Cell>
                <Table.Cell>{item.submitted_at}</Table.Cell>
                <Table.Cell>{getStatusBadge(item.status)}</Table.Cell>
                {activeTab === 'completed' && (
                  <>
                    <Table.Cell>
                      <span className="font-bold text-blue-600">
                        {item.score}/{item.max_score}
                      </span>
                    </Table.Cell>
                    <Table.Cell>{item.graded_at}</Table.Cell>
                  </>
                )}
                <Table.Cell>
                  <Button
                    variant={activeTab === 'pending' ? 'primary' : 'outline'}
                    size="sm"
                  >
                    {activeTab === 'pending' ? '채점하기' : '상세보기'}
                  </Button>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>

        {filteredItems.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            {activeTab === 'pending' ? '채점 대기 중인 항목이 없습니다.' : '채점 완료된 항목이 없습니다.'}
          </div>
        )}
      </Card>
    </div>
  );
}
