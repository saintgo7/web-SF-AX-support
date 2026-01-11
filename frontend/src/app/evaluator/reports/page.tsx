'use client';

import { useState } from 'react';
import { Card, Badge, Input, Select, Table, Button, Modal, Textarea } from '@/components/ui';

interface Report {
  id: string;
  title: string;
  report_type: 'CONSULTING' | 'EVALUATION' | 'SUMMARY';
  consultant_name?: string;
  company_name?: string;
  status: 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REJECTED';
  created_at: string;
  updated_at: string;
  author: string;
}

const mockReports: Report[] = [
  {
    id: '1',
    title: '(주)스마트제조 AX 컨설팅 보고서',
    report_type: 'CONSULTING',
    consultant_name: '김철수',
    company_name: '(주)스마트제조',
    status: 'SUBMITTED',
    created_at: '2026-01-10',
    updated_at: '2026-01-10',
    author: '홍길동',
  },
  {
    id: '2',
    title: '대한전자 AX 컨설팅 최종 보고서',
    report_type: 'CONSULTING',
    consultant_name: '이영희',
    company_name: '대한전자',
    status: 'APPROVED',
    created_at: '2026-01-05',
    updated_at: '2026-01-08',
    author: '홍길동',
  },
  {
    id: '3',
    title: '김철수 컨설턴트 평가 보고서',
    report_type: 'EVALUATION',
    consultant_name: '김철수',
    status: 'DRAFT',
    created_at: '2026-01-11',
    updated_at: '2026-01-11',
    author: '홍길동',
  },
  {
    id: '4',
    title: '2026년 1월 컨설팅 현황 요약',
    report_type: 'SUMMARY',
    status: 'DRAFT',
    created_at: '2026-01-11',
    updated_at: '2026-01-11',
    author: '홍길동',
  },
];

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>(mockReports);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newReportType, setNewReportType] = useState<string>('CONSULTING');

  const filteredReports = reports.filter((r) => {
    const matchesSearch =
      r.title.includes(searchTerm) ||
      r.consultant_name?.includes(searchTerm) ||
      r.company_name?.includes(searchTerm);
    const matchesStatus = statusFilter === 'all' || r.status === statusFilter;
    const matchesType = typeFilter === 'all' || r.report_type === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'DRAFT':
        return <Badge variant="secondary">작성중</Badge>;
      case 'SUBMITTED':
        return <Badge variant="info">제출됨</Badge>;
      case 'APPROVED':
        return <Badge variant="success">승인됨</Badge>;
      case 'REJECTED':
        return <Badge variant="error">반려됨</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'CONSULTING':
        return <Badge variant="primary">컨설팅</Badge>;
      case 'EVALUATION':
        return <Badge variant="warning">평가</Badge>;
      case 'SUMMARY':
        return <Badge variant="secondary">요약</Badge>;
      default:
        return <Badge>{type}</Badge>;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">보고서 작성/관리</h1>
        <Button variant="primary" onClick={() => setIsCreateModalOpen(true)}>
          + 새 보고서 작성
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-gray-500">전체 보고서</div>
          <div className="text-2xl font-bold text-blue-600">{reports.length}건</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-500">작성중</div>
          <div className="text-2xl font-bold text-gray-600">
            {reports.filter((r) => r.status === 'DRAFT').length}건
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-500">제출됨</div>
          <div className="text-2xl font-bold text-blue-600">
            {reports.filter((r) => r.status === 'SUBMITTED').length}건
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-500">승인됨</div>
          <div className="text-2xl font-bold text-green-600">
            {reports.filter((r) => r.status === 'APPROVED').length}건
          </div>
        </Card>
      </div>

      {/* 필터 */}
      <Card className="p-4">
        <div className="flex gap-4">
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
        <Table>
          <Table.Head>
            <Table.Row>
              <Table.Header>제목</Table.Header>
              <Table.Header>유형</Table.Header>
              <Table.Header>컨설턴트</Table.Header>
              <Table.Header>기업</Table.Header>
              <Table.Header>상태</Table.Header>
              <Table.Header>작성자</Table.Header>
              <Table.Header>작성일</Table.Header>
              <Table.Header>수정일</Table.Header>
              <Table.Header>작업</Table.Header>
            </Table.Row>
          </Table.Head>
          <Table.Body>
            {filteredReports.map((report) => (
              <Table.Row key={report.id}>
                <Table.Cell className="font-medium">{report.title}</Table.Cell>
                <Table.Cell>{getTypeBadge(report.report_type)}</Table.Cell>
                <Table.Cell>{report.consultant_name || '-'}</Table.Cell>
                <Table.Cell>{report.company_name || '-'}</Table.Cell>
                <Table.Cell>{getStatusBadge(report.status)}</Table.Cell>
                <Table.Cell>{report.author}</Table.Cell>
                <Table.Cell>{report.created_at}</Table.Cell>
                <Table.Cell>{report.updated_at}</Table.Cell>
                <Table.Cell>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      {report.status === 'DRAFT' ? '편집' : '보기'}
                    </Button>
                    {report.status === 'APPROVED' && (
                      <Button variant="secondary" size="sm">
                        PDF
                      </Button>
                    )}
                  </div>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </Card>

      {/* 새 보고서 작성 모달 */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="새 보고서 작성"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              보고서 유형
            </label>
            <Select
              value={newReportType}
              onChange={(e) => setNewReportType(e.target.value)}
              options={[
                { value: 'CONSULTING', label: '컨설팅 보고서' },
                { value: 'EVALUATION', label: '평가 보고서' },
                { value: 'SUMMARY', label: '요약 보고서' },
              ]}
            />
          </div>

          {newReportType === 'CONSULTING' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  대상 기업
                </label>
                <Select
                  options={[
                    { value: '', label: '기업 선택...' },
                    { value: '1', label: '(주)스마트제조' },
                    { value: '2', label: '대한전자' },
                    { value: '3', label: '글로벌기계' },
                  ]}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  담당 컨설턴트
                </label>
                <Select
                  options={[
                    { value: '', label: '컨설턴트 선택...' },
                    { value: '1', label: '김철수' },
                    { value: '2', label: '이영희' },
                    { value: '3', label: '박민수' },
                  ]}
                />
              </div>
            </>
          )}

          {newReportType === 'EVALUATION' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                평가 대상 컨설턴트
              </label>
              <Select
                options={[
                  { value: '', label: '컨설턴트 선택...' },
                  { value: '1', label: '김철수' },
                  { value: '2', label: '이영희' },
                  { value: '3', label: '박민수' },
                ]}
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              보고서 제목
            </label>
            <Input placeholder="보고서 제목을 입력하세요..." />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setIsCreateModalOpen(false)}>
              취소
            </Button>
            <Button variant="primary" onClick={() => setIsCreateModalOpen(false)}>
              작성 시작
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
