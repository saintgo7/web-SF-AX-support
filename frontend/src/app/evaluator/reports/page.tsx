'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, Badge, Input, Select, Table, Button } from '@/components/ui';
import { Column } from '@/components/ui/Table';
import {
  Report,
  ReportType,
  ReportStatus,
  REPORT_TYPE_LABELS,
  REPORT_STATUS_LABELS,
} from '@/types/report';

const mockReports: Report[] = [
  {
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
  },
  {
    id: '2',
    title: '대한전자 AX 컨설팅 최종 보고서',
    report_type: 'CONSULTING',
    consultant_id: '2',
    consultant_name: '이영희',
    company_id: '2',
    company_name: '대한전자',
    status: 'APPROVED',
    created_at: '2026-01-05',
    updated_at: '2026-01-08',
    author_id: '1',
    author: '홍길동',
  },
  {
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
  },
  {
    id: '4',
    title: '2026년 1월 컨설팅 현황 요약',
    report_type: 'SUMMARY',
    status: 'DRAFT',
    created_at: '2026-01-11',
    updated_at: '2026-01-11',
    author_id: '1',
    author: '홍길동',
  },
];

export default function ReportsPage() {
  const router = useRouter();
  const [reports] = useState<Report[]>(mockReports);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredReports = reports.filter((r) => {
    const matchesSearch =
      r.title.includes(searchTerm) ||
      r.consultant_name?.includes(searchTerm) ||
      r.company_name?.includes(searchTerm);
    const matchesStatus = statusFilter === 'all' || r.status === statusFilter;
    const matchesType = typeFilter === 'all' || r.report_type === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

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

  const handleViewReport = (reportId: string) => {
    router.push(`/evaluator/reports/${reportId}`);
  };

  const handleCreateReport = () => {
    router.push('/evaluator/reports/new');
  };

  const columns: Column<Report>[] = [
    {
      key: 'title',
      header: '제목',
      render: (value, row) => (
        <button
          onClick={() => handleViewReport(row.id)}
          className="font-medium text-blue-600 hover:text-blue-800 hover:underline text-left"
        >
          {value as string}
        </button>
      ),
    },
    {
      key: 'report_type',
      header: '유형',
      render: (value) => getTypeBadge(value as ReportType),
    },
    {
      key: 'consultant_name',
      header: '컨설턴트',
      render: (value) => value || '-',
    },
    {
      key: 'company_name',
      header: '기업',
      render: (value) => value || '-',
    },
    {
      key: 'status',
      header: '상태',
      render: (value) => getStatusBadge(value as ReportStatus),
    },
    {
      key: 'author',
      header: '작성자',
    },
    {
      key: 'created_at',
      header: '작성일',
    },
    {
      key: 'updated_at',
      header: '수정일',
    },
    {
      key: 'id',
      header: '작업',
      render: (_, row) => (
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleViewReport(row.id)}
          >
            {row.status === 'DRAFT' ? '편집' : '보기'}
          </Button>
          {row.status === 'APPROVED' && (
            <Button variant="secondary" size="sm">
              PDF
            </Button>
          )}
        </div>
      ),
    },
  ];

  // 통계 계산
  const stats = {
    total: reports.length,
    draft: reports.filter((r) => r.status === 'DRAFT').length,
    submitted: reports.filter((r) => r.status === 'SUBMITTED').length,
    approved: reports.filter((r) => r.status === 'APPROVED').length,
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">보고서 작성/관리</h1>
        <Button variant="primary" onClick={handleCreateReport}>
          + 새 보고서 작성
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="p-4">
            <div className="text-sm text-gray-500">전체 보고서</div>
            <div className="text-2xl font-bold text-blue-600">{stats.total}건</div>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="text-sm text-gray-500">작성중</div>
            <div className="text-2xl font-bold text-gray-600">{stats.draft}건</div>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="text-sm text-gray-500">제출됨</div>
            <div className="text-2xl font-bold text-blue-600">{stats.submitted}건</div>
          </div>
        </Card>
        <Card>
          <div className="p-4">
            <div className="text-sm text-gray-500">승인됨</div>
            <div className="text-2xl font-bold text-green-600">{stats.approved}건</div>
          </div>
        </Card>
      </div>

      {/* 필터 */}
      <Card>
        <div className="p-4 flex gap-4">
          <div className="flex-1">
            <Input
              placeholder="제목, 컨설턴트, 기업명으로 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            options={[
              { value: 'all', label: '전체 유형' },
              { value: 'CONSULTING', label: '컨설팅 보고서' },
              { value: 'EVALUATION', label: '평가 보고서' },
              { value: 'SUMMARY', label: '요약 보고서' },
            ]}
          />
          <Select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            options={[
              { value: 'all', label: '전체 상태' },
              { value: 'DRAFT', label: '작성중' },
              { value: 'SUBMITTED', label: '제출됨' },
              { value: 'APPROVED', label: '승인됨' },
              { value: 'REJECTED', label: '반려됨' },
            ]}
          />
        </div>
      </Card>

      {/* 보고서 목록 */}
      <Card>
        <div className="p-4">
          <Table
            columns={columns}
            data={filteredReports}
            keyField="id"
            emptyMessage="등록된 보고서가 없습니다."
          />
        </div>
      </Card>
    </div>
  );
}
