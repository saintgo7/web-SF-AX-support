'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, Button, Input, Select } from '@/components/ui';
import { ReportType, REPORT_TYPE_LABELS } from '@/types/report';

// Mock 데이터
const mockCompanies = [
  { id: '1', name: '(주)스마트제조' },
  { id: '2', name: '대한전자' },
  { id: '3', name: '글로벌기계' },
  { id: '4', name: '에이아이테크' },
];

const mockConsultants = [
  { id: '1', name: '김철수' },
  { id: '2', name: '이영희' },
  { id: '3', name: '박민수' },
];

export default function NewReportPage() {
  const router = useRouter();
  const [isCreating, setIsCreating] = useState(false);

  const [formData, setFormData] = useState({
    report_type: 'CONSULTING' as ReportType,
    title: '',
    company_id: '',
    consultant_id: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleTypeChange = (type: ReportType) => {
    setFormData({
      ...formData,
      report_type: type,
      title: '',
      company_id: '',
      consultant_id: '',
    });
    setErrors({});
  };

  const generateDefaultTitle = () => {
    const today = new Date();
    const dateStr = `${today.getFullYear()}.${String(today.getMonth() + 1).padStart(2, '0')}.${String(today.getDate()).padStart(2, '0')}`;

    switch (formData.report_type) {
      case 'CONSULTING': {
        const company = mockCompanies.find((c) => c.id === formData.company_id);
        return company ? `${company.name} AX 컨설팅 보고서` : '';
      }
      case 'EVALUATION': {
        const consultant = mockConsultants.find((c) => c.id === formData.consultant_id);
        return consultant ? `${consultant.name} 컨설턴트 평가 보고서` : '';
      }
      case 'SUMMARY':
        return `${today.getFullYear()}년 ${today.getMonth() + 1}월 컨설팅 현황 요약`;
      default:
        return '';
    }
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = '보고서 제목을 입력하세요.';
    }

    if (formData.report_type === 'CONSULTING') {
      if (!formData.company_id) {
        newErrors.company_id = '대상 기업을 선택하세요.';
      }
      if (!formData.consultant_id) {
        newErrors.consultant_id = '담당 컨설턴트를 선택하세요.';
      }
    }

    if (formData.report_type === 'EVALUATION') {
      if (!formData.consultant_id) {
        newErrors.consultant_id = '평가 대상 컨설턴트를 선택하세요.';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = async () => {
    if (!validate()) return;

    setIsCreating(true);

    // TODO: 실제 API 호출로 변경
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Mock: 새 보고서 ID 생성 (실제로는 API 응답에서 받음)
    const newReportId = String(Date.now());

    setIsCreating(false);

    // 생성된 보고서 상세 페이지로 이동
    router.push(`/evaluator/reports/${newReportId}`);
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      {/* 헤더 */}
      <div className="mb-6">
        <button
          onClick={() => router.push('/evaluator/reports')}
          className="text-sm text-gray-500 hover:text-gray-700 mb-2 flex items-center gap-1"
        >
          ← 목록으로
        </button>
        <h1 className="text-2xl font-bold text-gray-900">새 보고서 작성</h1>
        <p className="text-gray-500 mt-1">보고서 유형을 선택하고 기본 정보를 입력하세요.</p>
      </div>

      {/* 보고서 유형 선택 */}
      <Card>
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">1. 보고서 유형 선택</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {(['CONSULTING', 'EVALUATION', 'SUMMARY'] as ReportType[]).map((type) => (
              <button
                key={type}
                onClick={() => handleTypeChange(type)}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  formData.report_type === type
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="font-semibold mb-1">{REPORT_TYPE_LABELS[type]}</div>
                <div className="text-sm text-gray-500">
                  {type === 'CONSULTING' && '기업 컨설팅 결과 보고서'}
                  {type === 'EVALUATION' && '컨설턴트 역량 평가 보고서'}
                  {type === 'SUMMARY' && '기간별 활동 요약 보고서'}
                </div>
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* 기본 정보 입력 */}
      <Card className="mt-6">
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">2. 기본 정보 입력</h2>
          <div className="space-y-4">
            {/* 컨설팅 보고서: 기업 + 컨설턴트 선택 */}
            {formData.report_type === 'CONSULTING' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    대상 기업 <span className="text-red-500">*</span>
                  </label>
                  <Select
                    value={formData.company_id}
                    onChange={(e) => {
                      setFormData({ ...formData, company_id: e.target.value });
                      if (errors.company_id) {
                        setErrors({ ...errors, company_id: '' });
                      }
                    }}
                    options={[
                      { value: '', label: '기업을 선택하세요...' },
                      ...mockCompanies.map((c) => ({ value: c.id, label: c.name })),
                    ]}
                  />
                  {errors.company_id && (
                    <p className="mt-1 text-sm text-red-600">{errors.company_id}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    담당 컨설턴트 <span className="text-red-500">*</span>
                  </label>
                  <Select
                    value={formData.consultant_id}
                    onChange={(e) => {
                      setFormData({ ...formData, consultant_id: e.target.value });
                      if (errors.consultant_id) {
                        setErrors({ ...errors, consultant_id: '' });
                      }
                    }}
                    options={[
                      { value: '', label: '컨설턴트를 선택하세요...' },
                      ...mockConsultants.map((c) => ({ value: c.id, label: c.name })),
                    ]}
                  />
                  {errors.consultant_id && (
                    <p className="mt-1 text-sm text-red-600">{errors.consultant_id}</p>
                  )}
                </div>
              </>
            )}

            {/* 평가 보고서: 컨설턴트 선택 */}
            {formData.report_type === 'EVALUATION' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  평가 대상 컨설턴트 <span className="text-red-500">*</span>
                </label>
                <Select
                  value={formData.consultant_id}
                  onChange={(e) => {
                    setFormData({ ...formData, consultant_id: e.target.value });
                    if (errors.consultant_id) {
                      setErrors({ ...errors, consultant_id: '' });
                    }
                  }}
                  options={[
                    { value: '', label: '컨설턴트를 선택하세요...' },
                    ...mockConsultants.map((c) => ({ value: c.id, label: c.name })),
                  ]}
                />
                {errors.consultant_id && (
                  <p className="mt-1 text-sm text-red-600">{errors.consultant_id}</p>
                )}
              </div>
            )}

            {/* 요약 보고서: 추가 선택 없음 */}
            {formData.report_type === 'SUMMARY' && (
              <div className="p-4 bg-gray-50 rounded-lg text-sm text-gray-600">
                요약 보고서는 전체 컨설팅 활동을 종합하여 작성합니다.
              </div>
            )}

            {/* 보고서 제목 */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="block text-sm font-medium text-gray-700">
                  보고서 제목 <span className="text-red-500">*</span>
                </label>
                <button
                  type="button"
                  onClick={() => setFormData({ ...formData, title: generateDefaultTitle() })}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  기본 제목 생성
                </button>
              </div>
              <Input
                value={formData.title}
                onChange={(e) => {
                  setFormData({ ...formData, title: e.target.value });
                  if (errors.title) {
                    setErrors({ ...errors, title: '' });
                  }
                }}
                placeholder="보고서 제목을 입력하세요..."
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600">{errors.title}</p>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* 버튼 */}
      <div className="mt-6 flex justify-end gap-3">
        <Button variant="outline" onClick={() => router.push('/evaluator/reports')}>
          취소
        </Button>
        <Button variant="primary" onClick={handleCreate} disabled={isCreating}>
          {isCreating ? '생성 중...' : '보고서 생성'}
        </Button>
      </div>
    </div>
  );
}
