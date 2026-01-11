'use client';

import { useState } from 'react';
import { Card, Badge, Input, Select, Table, Button } from '@/components/ui';

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
  const [matchings, setMatchings] = useState<Matching[]>(mockMatchings);
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
        <Card className="p-4">
          <div className="text-sm text-gray-500">전체 매칭</div>
          <div className="text-2xl font-bold text-blue-600">{matchings.length}건</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-500">제안됨</div>
          <div className="text-2xl font-bold text-gray-600">
            {matchings.filter((m) => m.status === 'PROPOSED').length}건
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-500">진행중</div>
          <div className="text-2xl font-bold text-yellow-600">
            {matchings.filter((m) => m.status === 'IN_PROGRESS').length}건
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-500">완료</div>
          <div className="text-2xl font-bold text-green-600">
            {matchings.filter((m) => m.status === 'COMPLETED').length}건
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-500">평균 매칭점수</div>
          <div className="text-2xl font-bold text-purple-600">
            {(matchings.reduce((sum, m) => sum + m.match_score, 0) / matchings.length).toFixed(1)}점
          </div>
        </Card>
      </div>

      {/* 필터 */}
      <Card className="p-4">
        <div className="flex gap-4">
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
        <Table>
          <Table.Head>
            <Table.Row>
              <Table.Header>컨설턴트</Table.Header>
              <Table.Header>기업명</Table.Header>
              <Table.Header>업종</Table.Header>
              <Table.Header>매칭점수</Table.Header>
              <Table.Header>상태</Table.Header>
              <Table.Header>등록일</Table.Header>
              <Table.Header>시작일</Table.Header>
              <Table.Header>종료일</Table.Header>
              <Table.Header>상세</Table.Header>
            </Table.Row>
          </Table.Head>
          <Table.Body>
            {filteredMatchings.map((matching) => (
              <Table.Row key={matching.id}>
                <Table.Cell className="font-medium">{matching.consultant_name}</Table.Cell>
                <Table.Cell>{matching.company_name}</Table.Cell>
                <Table.Cell>{matching.company_industry}</Table.Cell>
                <Table.Cell>
                  <span className={`font-bold ${getMatchScoreColor(matching.match_score)}`}>
                    {matching.match_score}점
                  </span>
                </Table.Cell>
                <Table.Cell>{getStatusBadge(matching.status)}</Table.Cell>
                <Table.Cell>{matching.created_at}</Table.Cell>
                <Table.Cell>{matching.start_date || '-'}</Table.Cell>
                <Table.Cell>{matching.end_date || '-'}</Table.Cell>
                <Table.Cell>
                  <Button variant="outline" size="sm">
                    상세보기
                  </Button>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </Card>
    </div>
  );
}
