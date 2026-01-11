'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axiosInstance from '@/lib/axios';
import { Card, Button, Badge, Table, Modal, Input, Select } from '@/components/ui';
import { Column } from '@/components/ui/Table';
import { Expert, DegreeType, OrgType, QualificationStatus } from '@/types';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

export default function ExpertsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedExpert, setSelectedExpert] = useState<Expert | null>(null);

  const { data: expertsData, isLoading, refetch } = useQuery({
    queryKey: ['experts'],
    queryFn: async () => {
      const { data } = await axiosInstance.get('/experts');
      return data;
    },
  });

  const columns: Column<Expert>[] = [
    {
      key: 'id',
      header: 'ID',
      render: (_, row) => row.id.slice(0, 8),
    },
    {
      key: 'degree_type',
      header: '학위',
      render: (value) => {
        const labels: Record<string, string> = {
          PHD: '박사',
          MASTER: '석사',
          BACHELOR: '학사',
        };
        return labels[value as string] || value;
      },
    },
    {
      key: 'degree_field',
      header: '전공',
    },
    {
      key: 'career_years',
      header: '경력',
      render: (value) => `${value}년`,
    },
    {
      key: 'position',
      header: '직책',
    },
    {
      key: 'org_name',
      header: '소속',
    },
    {
      key: 'qualification_status',
      header: '자격 상태',
      render: (value) => {
        const variant = value === 'QUALIFIED' ? 'success' :
                        value === 'DISQUALIFIED' ? 'error' : 'warning';
        const labels: Record<string, string> = {
          PENDING: '검증대기',
          QUALIFIED: '자격완료',
          DISQUALIFIED: '자격미달',
        };
        return <Badge variant={variant}>{labels[value as string] || value}</Badge>;
      },
    },
    {
      key: 'created_at',
      header: '등록일',
      render: (value) => format(new Date(value as string), 'yyyy-MM-dd', { locale: ko }),
    },
  ];

  const degreeOptions = [
    { value: 'PHD', label: '박사' },
    { value: 'MASTER', label: '석사' },
    { value: 'BACHELOR', label: '학사' },
  ];

  const orgTypeOptions = [
    { value: 'UNIVERSITY', label: '대학교' },
    { value: 'COMPANY', label: '기업' },
    { value: 'RESEARCH', label: '연구소' },
    { value: 'OTHER', label: '기타' },
  ];

  const handleViewDetails = (expert: Expert) => {
    setSelectedExpert(expert);
    setIsModalOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">컨설턴트 관리</h1>
          <p className="mt-2 text-gray-600">
            등록된 컨설턴트를 관리하세요
          </p>
        </div>

        <Button onClick={() => setIsModalOpen(true)}>
          컨설턴트 추가
        </Button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="p-6">
            <p className="text-sm font-medium text-gray-600">총 컨설턴트</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {expertsData?.length || 0}
            </p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <p className="text-sm font-medium text-gray-600">자격완료</p>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {expertsData?.filter((e: Expert) => e.qualification_status === 'QUALIFIED').length || 0}
            </p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <p className="text-sm font-medium text-gray-600">검증대기</p>
            <p className="text-3xl font-bold text-yellow-600 mt-2">
              {expertsData?.filter((e: Expert) => e.qualification_status === 'PENDING').length || 0}
            </p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <p className="text-sm font-medium text-gray-600">자격미달</p>
            <p className="text-3xl font-bold text-red-600 mt-2">
              {expertsData?.filter((e: Expert) => e.qualification_status === 'DISQUALIFIED').length || 0}
            </p>
          </div>
        </Card>
      </div>

      {/* Experts List */}
      <Card>
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            컨설턴트 목록
          </h2>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <Table
              columns={columns}
              data={expertsData || []}
              keyField="id"
              onRowClick={handleViewDetails}
              emptyMessage="등록된 컨설턴트가 없습니다."
            />
          )}
        </div>
      </Card>

      {/* Expert Details Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedExpert(null);
        }}
        title={selectedExpert ? '컨설턴트 상세정보' : '새 컨설턴트 추가'}
        size="lg"
      >
        {selectedExpert ? (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ID
                </label>
                <p className="text-sm text-gray-900">{selectedExpert.id.slice(0, 8)}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  자격 상태
                </label>
                <Badge variant={
                  selectedExpert.qualification_status === 'QUALIFIED' ? 'success' :
                  selectedExpert.qualification_status === 'DISQUALIFIED' ? 'error' : 'warning'
                }>
                  {selectedExpert.qualification_status === 'QUALIFIED' ? '자격완료' :
                   selectedExpert.qualification_status === 'DISQUALIFIED' ? '자격미달' : '검증대기'}
                </Badge>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  학위
                </label>
                <p className="text-sm text-gray-900">{selectedExpert.degree_type || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  전공
                </label>
                <p className="text-sm text-gray-900">{selectedExpert.degree_field || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  경력
                </label>
                <p className="text-sm text-gray-900">{selectedExpert.career_years ? `${selectedExpert.career_years}년` : '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  직책
                </label>
                <p className="text-sm text-gray-900">{selectedExpert.position || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  소속 기관
                </label>
                <p className="text-sm text-gray-900">{selectedExpert.org_name || '-'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  기관 유형
                </label>
                <p className="text-sm text-gray-900">{selectedExpert.org_type || '-'}</p>
              </div>
            </div>

            {selectedExpert.specialties && selectedExpert.specialties.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  전문 분야
                </label>
                <div className="flex flex-wrap gap-2">
                  {selectedExpert.specialties.map((specialty, index) => (
                    <Badge key={index} variant="info">
                      {specialty}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {selectedExpert.qualification_note && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  자격 검증 내용
                </label>
                <p className="text-sm text-gray-900">{selectedExpert.qualification_note}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-gray-600">새 컨설턴트 추가 기능이 준비 중입니다.</p>
          </div>
        )}
      </Modal>
    </div>
  );
}
