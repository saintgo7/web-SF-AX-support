'use client';

import { useAuth, useExpert, useApplication } from '@/hooks';
import { Card, Badge, Table } from '@/components/ui';
import { Column } from '@/components/ui/Table';
import { Application, Expert } from '@/types';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

export default function ApplicantDashboard() {
  const { user } = useAuth();
  const { getExpertProfile } = useExpert();
  const { getApplications } = useApplication();

  const { data: expert } = getExpertProfile();
  const { data: applicationsData } = getApplications();

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return 'success';
      case 'REJECTED':
        return 'error';
      case 'UNDER_REVIEW':
        return 'info';
      case 'SUBMITTED':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      DRAFT: '임시저장',
      SUBMITTED: '제출완료',
      UNDER_REVIEW: '검토중',
      APPROVED: '승인',
      REJECTED: '반려',
    };
    return labels[status] || status;
  };

  const columns: Column<Application>[] = [
    {
      key: 'id',
      header: '신청서 ID',
      render: (_, row) => row.id.slice(0, 8),
    },
    {
      key: 'status',
      header: '상태',
      render: (value) => (
        <Badge variant={getStatusBadgeVariant(value as string)}>
          {getStatusLabel(value as string)}
        </Badge>
      ),
    },
    {
      key: 'submission_date',
      header: '제출일',
      render: (value) =>
        value ? format(new Date(value as string), 'yyyy-MM-dd', { locale: ko }) : '-',
    },
    {
      key: 'created_at',
      header: '생성일',
      render: (value) => format(new Date(value as string), 'yyyy-MM-dd', { locale: ko }),
    },
  ];

  const getQualificationStatusBadge = (status?: string) => {
    if (!expert?.qualification_status) return null;

    const variant = status === 'QUALIFIED' ? 'success' :
                    status === 'DISQUALIFIED' ? 'error' : 'warning';
    const label = status === 'QUALIFIED' ? '자격검증 완료' :
                  status === 'DISQUALIFIED' ? '자격미달' : '검증대기';

    return <Badge variant={variant}>{label}</Badge>;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          신청자 대시보드
        </h1>
        <p className="mt-2 text-gray-600">
          환영합니다, {user?.name}님
        </p>
      </div>

      {/* Profile Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              기본 정보
            </h3>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">이름</dt>
                <dd className="mt-1 text-sm text-gray-900">{user?.name}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">이메일</dt>
                <dd className="mt-1 text-sm text-gray-900">{user?.email}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">자격 상태</dt>
                <dd className="mt-1">
                  {getQualificationStatusBadge(expert?.qualification_status)}
                </dd>
              </div>
            </dl>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              전문가 정보
            </h3>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">학위</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {expert?.degree_type || '-'} / {expert?.degree_field || '-'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">경력</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {expert?.career_years ? `${expert.career_years}년` : '-'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">직책</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {expert?.position || '-'}
                </dd>
              </div>
            </dl>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              신청서 현황
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">총 신청서</span>
                <span className="text-2xl font-bold text-blue-600">
                  {applicationsData?.total || 0}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">제출완료</span>
                <span className="text-2xl font-bold text-green-600">
                  {applicationsData?.items?.filter((a: Application) => a.status === 'SUBMITTED').length || 0}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">검토중</span>
                <span className="text-2xl font-bold text-yellow-600">
                  {applicationsData?.items?.filter((a: Application) => a.status === 'UNDER_REVIEW').length || 0}
                </span>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Applications List */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              신청서 목록
            </h3>
          </div>

          <Table
            columns={columns}
            data={applicationsData?.items || []}
            keyField="id"
            emptyMessage="신청서가 없습니다."
          />
        </div>
      </Card>
    </div>
  );
}
