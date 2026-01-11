'use client';

import { useState } from 'react';
import { Card, Badge, Input, Select, Table } from '@/components/ui';
import { Column } from '@/components/ui/Table';

interface Matching {
  id: string;
  consultant_name: string;
  company_name: string;
  company_industry: string;
  status: 'PROPOSED' | 'ACCEPTED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  match_score: number;
  created_at: string;
  start_date?: string;
  end_date?: string;
}

const mockMatchings: Matching[] = [
  {
    id: '1',
    consultant_name: '김철수',
    company_name: '(주)스마트제조',
    company_industry: '자동차부품',
    status: 'IN_PROGRESS',
    match_score: 95,
    created_at: '2026-01-05',
    start_date: '2026-01-10',
  },
  {
    id: '2',
    consultant_name: '이영희',
    company_name: '대한전자',
    company_industry: '전자부품',
    status: 'COMPLETED',
    match_score: 88,
    created_at: '2025-12-15',
    start_date: '2025-12-20',
    end_date: '2026-01-05',
  },
  {
    id: '3',
    consultant_name: '박민수',
    company_name: '글로벌기계',
    company_industry: '산업기계',
    status: 'PROPOSED',
    match_score: 82,
    created_at: '2026-01-10',
  },
  {
    id: '4',
    consultant_name: '김철수',
    company_name: '에이아이테크',
    company_industry: 'IT서비스',
    status: 'ACCEPTED',
    match_score: 91,
    created_at: '2026-01-08',
  },
];

export default function MatchingPage() {
  const [matchings] = useState<Matching[]>(mockMatchings);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredMatchings = matchings.filter((m) => {
    const matchesSearch =
      m.consultant_name.includes(searchTerm) ||
      m.company_name.includes(searchTerm);
    const matchesStatus = statusFilter === 'all' || m.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PROPOSED':
        return <Badge variant="secondary">제안됨</Badge>;
      case 'ACCEPTED':
        return <Badge variant="info">수락됨</Badge>;
      case 'IN_PROGRESS':
        return <Badge variant="warning">진행중</Badge>;
      case 'COMPLETED':
        return <Badge variant="success">완료</Badge>;
      case 'CANCELLED':
        return <Badge variant="error">취소됨</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const columns: Column<Matching>[] = [
    {
      key: 'consultant_name',
      header: '컨설턴트',
    },
    {
      key: 'company_name',
      header: '기업명',
    },
    {
      key: 'company_industry',
      header: '업종',
    },
    {
      key: 'match_score',
      header: '매칭점수',
      render: (value) => (
        <span className={`font-bold ${getMatchScoreColor(value as number)}`}>
          {value}점
        </span>
      ),
    },
    {
      key: 'status',
      header: '상태',
      render: (value) => getStatusBadge(value as string),
    },
    {
      key: 'created_at',
      header: '등록일',
    },
    {
      key: 'start_date',
      header: '시작일',
      render: (value) => value || '-',
    },
    {
      key: 'end_date',
      header: '종료일',
      render: (value) => value || '-',
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">매칭 현황</h1>
        <div className="text-sm text-gray-500">
          총 {filteredMatchings.length}건
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <div className="p-4">
            <div className="text-sm text-gray-500">전체 매칭</div>
            <div className="text-2xl font-bold text-blue-600">{matchings.length}건</div>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="text-sm text-gray-500">제안됨</div>
            <div className="text-2xl font-bold text-gray-600">
              {matchings.filter((m) => m.status === 'PROPOSED').length}건
            </div>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="text-sm text-gray-500">진행중</div>
            <div className="text-2xl font-bold text-yellow-600">
              {matchings.filter((m) => m.status === 'IN_PROGRESS').length}건
            </div>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="text-sm text-gray-500">완료</div>
            <div className="text-2xl font-bold text-green-600">
              {matchings.filter((m) => m.status === 'COMPLETED').length}건
            </div>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="text-sm text-gray-500">평균 매칭점수</div>
            <div className="text-2xl font-bold text-purple-600">
              {(matchings.reduce((sum, m) => sum + m.match_score, 0) / matchings.length).toFixed(1)}점
            </div>
          </div>
        </Card>
      </div>

      {/* 필터 */}
      <Card>
        <div className="p-4 flex gap-4">
          <div className="flex-1">
            <Input
              placeholder="컨설턴트명, 기업명으로 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            options={[
              { value: 'all', label: '전체 상태' },
              { value: 'PROPOSED', label: '제안됨' },
              { value: 'ACCEPTED', label: '수락됨' },
              { value: 'IN_PROGRESS', label: '진행중' },
              { value: 'COMPLETED', label: '완료' },
              { value: 'CANCELLED', label: '취소됨' },
            ]}
          />
        </div>
      </Card>

      {/* 매칭 목록 */}
      <Card>
        <div className="p-4">
          <Table
            columns={columns}
            data={filteredMatchings}
            keyField="id"
            emptyMessage="매칭 기록이 없습니다."
          />
        </div>
      </Card>
    </div>
  );
}
