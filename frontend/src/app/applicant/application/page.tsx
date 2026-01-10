'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { useExpert, useApplication } from '@/hooks';
import { Button, Input, Select, Textarea, Card, Alert } from '@/components/ui';
import { Expert, DegreeType, OrgType } from '@/types';

export default function ApplicationPage() {
  const router = useRouter();
  const { getExpertProfile, updateExpertProfile, verifyQualification } = useExpert();
  const { createApplication } = useApplication();
  const { data: expert } = getExpertProfile();

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register: registerExpert,
    handleSubmit: handleSubmitExpert,
    formState: { errors: expertErrors },
  } = useForm<Partial<Expert>>();

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

  const onExpertSubmit = async (data: Partial<Expert>) => {
    try {
      setError(null);
      setIsSubmitting(true);
      await updateExpertProfile.mutateAsync(data);
      setSuccess('전문가 정보가 저장되었습니다.');
    } catch (err: any) {
      setError(err.response?.data?.detail || '저장에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleVerifyQualification = async () => {
    try {
      setError(null);
      setIsSubmitting(true);
      await verifyQualification().mutateAsync();
      setSuccess('자격 검증이 완료되었습니다.');
    } catch (err: any) {
      setError(err.response?.data?.detail || '자격 검증에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateApplication = async () => {
    try {
      setError(null);
      setIsSubmitting(true);
      const result = await createApplication.mutateAsync({
        personal_statement: '',
        experience_description: '',
        motivation: '',
      });
      router.push(`/applicant/application/${result.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || '신청서 생성에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">신청서 작성</h1>
        <p className="mt-2 text-gray-600">
          자격검증 대상 정보를 입력하고 신청서를 작성하세요
        </p>
      </div>

      {error && (
        <Alert type="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert type="success" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Expert Profile Form */}
      <Card>
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            전문가 기본 정보
          </h2>

          <form onSubmit={handleSubmitExpert(onExpertSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Select
                label="학위"
                options={degreeOptions}
                placeholder="학위를 선택하세요"
                defaultValue={expert?.degree_type}
                error={expertErrors.degree_type?.message}
                {...registerExpert('degree_type')}
              />

              <Input
                label="전공 분야"
                placeholder="예: 기계공학, 전기전자"
                defaultValue={expert?.degree_field}
                error={expertErrors.degree_field?.message}
                {...registerExpert('degree_field', {
                  required: '전공 분야를 입력해주세요',
                })}
              />

              <Input
                label="경력 연수"
                type="number"
                placeholder="예: 5"
                defaultValue={expert?.career_years}
                error={expertErrors.career_years?.message}
                {...registerExpert('career_years', {
                  required: '경력 연수를 입력해주세요',
                  min: { value: 0, message: '0 이상의 값을 입력해주세요' },
                })}
              />

              <Input
                label="직책"
                placeholder="예: 수석연구원"
                defaultValue={expert?.position}
                error={expertErrors.position?.message}
                {...registerExpert('position', {
                  required: '직책을 입력해주세요',
                })}
              />

              <Input
                label="소속 기관명"
                placeholder="예: 000대학교"
                defaultValue={expert?.org_name}
                error={expertErrors.org_name?.message}
                {...registerExpert('org_name', {
                  required: '소속 기관명을 입력해주세요',
                })}
              />

              <Select
                label="소속 기관 유형"
                options={orgTypeOptions}
                placeholder="기관 유형을 선택하세요"
                defaultValue={expert?.org_type}
                error={expertErrors.org_type?.message}
                {...registerExpert('org_type')}
              />
            </div>

            <Textarea
              label="전문 분야 (콤마로 구분)"
              placeholder="예: 스마트공장, 자동화, 로봇공학"
              rows={3}
              defaultValue={expert?.specialties?.join(', ')}
              error={expertErrors.specialties?.message}
              {...registerExpert('specialties')}
            />

            <div className="flex gap-4">
              <Button
                type="submit"
                isLoading={isSubmitting}
                disabled={updateExpertProfile.isPending}
              >
                저장하기
              </Button>

              <Button
                type="button"
                variant="secondary"
                onClick={handleVerifyQualification}
                isLoading={isSubmitting}
                disabled={verifyQualification().isPending}
              >
                자격 검증하기
              </Button>
            </div>
          </form>
        </div>
      </Card>

      {/* Application Actions */}
      <Card>
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            신청서 관리
          </h2>

          <div className="flex gap-4">
            <Button
              onClick={handleCreateApplication}
              isLoading={isSubmitting}
              disabled={createApplication.isPending}
            >
              새 신청서 작성
            </Button>

            <Button
              variant="outline"
              onClick={() => router.push('/applicant/dashboard')}
            >
              대시보드로 돌아가기
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
