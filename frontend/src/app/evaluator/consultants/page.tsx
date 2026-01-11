'use client';

import { useState } from 'react';
import { Card, Badge, Input, Select, Table, Button } from '@/components/ui';
import { Column } from '@/components/ui/Table';

interface Consultant {
  id: string;
  name: string;
  email: string;
  specialties: string[];
  qualification_status: 'PENDING' | 'QUALIFIED' | 'DISQUALIFIED';
  career_years: number;
  org_name: string;
  matching_count: number;
  avg_score: number;
}

const mockConsultants: Consultant[] = [
  {
    id: '1',
    name: '김철수',
    email: 'kim@example.com',
    specialties: ['ML', 'DL'],
    qualification_status: 'QUALIFIED',
    career_years: 10,
    org_name: '삼성전자',
    matching_count: 5,
    avg_score: 92.5,
  },
  {
    id: '2',
    name: '이영희',
    email: 'lee@example.com',
    specialties: ['CV', '데이터인텔리전스'],
    qualification_status: 'QUALIFIED',
    career_years: 8,
    org_name: 'LG AI연구원',
    matching_count: 3,
    avg_score: 88.0,
  },
  {
    id: '3',
    name: '박민수',
    email: 'park@example.com',
    specialties: ['ML'],
    qualification_status: 'PENDING',
    career_years: 5,
    org_name: '네이버',
    matching_count: 0,
    avg_score: 0,
  },
];

export default function ConsultantsPage() {
  const [consultants] = useState<Consultant[]>(mockConsultants);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filteredConsultants = consultants.filter((c) => {
    const matchesSearch =
      c.name.includes(searchTerm) ||
      c.email.includes(searchTerm) ||
      c.org_name.includes(searchTerm);
    const matchesStatus =
      statusFilter === 'all' || c.qualification_status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'QUALIFIED':
        return <Badge variant="success">자격인증</Badge>;
      case 'PENDING':
        return <Badge variant="warning">심사중</Badge>;
      case 'DISQUALIFIED':
        return <Badge variant="error">부적격</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const columns: Column<Consultant>[] = [
    {
      key: 'name',
      header: '이름',
      render: (_, row) => (
        <div>
          <div className="font-medium">{row.name}</div>
          <div className="text-sm text-gray-500">{row.email}</div>
        </div>
      ),
    },
    {
      key: 'org_name',
      header: '소속기관',
    },
    {
      key: 'specialties',
      header: '전문분야',
      render: (value) => (
        <div className="flex gap-1 flex-wrap">
          {(value as string[]).map((s) => (
            <Badge key={s} variant="secondary">
              {s}
            </Badge>
          ))}
        </div>
      ),
    },
    {
      key: 'career_years',
      header: '경력',
      render: (value) => `${value}년`,
    },
    {
      key: 'qualification_status',
      header: '자격상태',
      render: (value) => getStatusBadge(value as string),
    },
    {
      key: 'matching_count',
      header: '매칭수',
      render: (value) => `${value}건`,
    },
    {
      key: 'avg_score',
      header: '평균점수',
      render: (value) => (value as number) > 0 ? `${value}점` : '-',
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">AX 컨설턴트 현황</h1>
        <div className="text-sm text-gray-500">
          총 {filteredConsultants.length}명
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="p-4">
            <div className="text-sm text-gray-500">전체 컨설턴트</div>
            <div className="text-2xl font-bold text-blue-600">{consultants.length}명</div>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="text-sm text-gray-500">자격인증 완료</div>
            <div className="text-2xl font-bold text-green-600">
              {consultants.filter((c) => c.qualification_status === 'QUALIFIED').length}명
            </div>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="text-sm text-gray-500">심사중</div>
            <div className="text-2xl font-bold text-yellow-600">
              {consultants.filter((c) => c.qualification_status === 'PENDING').length}명
            </div>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="text-sm text-gray-500">평균 평가점수</div>
            <div className="text-2xl font-bold text-purple-600">
              {(consultants.filter(c => c.avg_score > 0).reduce((sum, c) => sum + c.avg_score, 0) /
                consultants.filter(c => c.avg_score > 0).length || 0).toFixed(1)}점
            </div>
          </div>
        </Card>
      </div>

      {/* 필터 */}
      <Card>
        <div className="p-4 flex gap-4">
          <div className="flex-1">
            <Input
              placeholder="이름, 이메일, 소속기관으로 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            options={[
              { value: 'all', label: '전체 상태' },
              { value: 'QUALIFIED', label: '자격인증' },
              { value: 'PENDING', label: '심사중' },
              { value: 'DISQUALIFIED', label: '부적격' },
            ]}
          />
        </div>
      </Card>

      {/* 컨설턴트 목록 */}
      <Card>
        <div className="p-4">
          <Table
            columns={columns}
            data={filteredConsultants}
            keyField="id"
            emptyMessage="등록된 컨설턴트가 없습니다."
          />
        </div>
      </Card>
    </div>
  );
}
