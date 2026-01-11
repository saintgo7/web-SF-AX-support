'use client';

import { useState } from 'react';
import { Card, Button, Badge, Table, Alert, Select, Modal, Tabs, TabContent, TabButton } from '@/components/ui';
import { Column } from '@/components/ui/Table';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { useMatching } from '@/hooks/useMatching';
import { RecommendationCard } from '@/components/matching';
import { matchingsApi } from '@/lib/api/matchings';
import { companiesApi } from '@/lib/api/companies';
import { expertApi } from '@/lib/api/expert';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { Matching, MatchingStatus, RecommendedCandidate } from '@/types/matching';

const STATUS_LABELS: Record<MatchingStatus, string> = {
  PROPOSED: '제안됨',
  ACCEPTED: '수락',
  REJECTED: '거절',
  IN_PROGRESS: '진행중',
  COMPLETED: '완료',
  CANCELLED: '취소',
};

const STATUS_VARIANTS: Record<MatchingStatus, 'default' | 'success' | 'warning' | 'error'> = {
  PROPOSED: 'default',
  ACCEPTED: 'success',
  REJECTED: 'error',
  IN_PROGRESS: 'warning',
  COMPLETED: 'success',
  CANCELLED: 'error',
};

export default function MatchingPage() {
  const queryClient = useQueryClient();
  const matching = useMatching();

  const [activeTab, setActiveTab] = useState<'list' | 'recommendations' | 'analytics'>('list');
  const [selectedDemand, setSelectedDemand] = useState<string>('');
  const [manualExpert, setManualExpert] = useState<string>('');
  const [manualDemand, setManualDemand] = useState<string>('');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [showAutoMatchModal, setShowAutoMatchModal] = useState(false);

  // Fetch matchings list
  const { data: matchingsData, isLoading: matchingsLoading } = useQuery({
    queryKey: ['matchings'],
    queryFn: () => matchingsApi.getMatchings(),
  });

  // Fetch demands
  const { data: demandsData } = useQuery({
    queryKey: ['demands', 'PENDING'],
    queryFn: () => companiesApi.getDemands({ status: 'PENDING' }),
  });

  // Fetch experts
  const { data: expertsData } = useQuery({
    queryKey: ['experts'],
    queryFn: () => expertApi.getExperts(),
  });

  // Fetch analytics
  const { data: analyticsData } = useQuery({
    queryKey: ['matching-analytics'],
    queryFn: () => matchingsApi.getAnalytics(),
    enabled: activeTab === 'analytics',
  });

  // Fetch intelligent recommendations when demand is selected
  const { data: recommendationsData, isLoading: recommendationsLoading, refetch: refetchRecommendations } = useQuery({
    queryKey: ['recommendations', selectedDemand],
    queryFn: () => matchingsApi.getRecommendations({
      demand_id: selectedDemand,
      top_n: 10,
      min_score: 40,
    }),
    enabled: !!selectedDemand && activeTab === 'recommendations',
  });

  // Mutations
  const updateStatusMutation = useMutation({
    mutationFn: ({ matchingId, status }: { matchingId: string; status: MatchingStatus }) =>
      matchingsApi.updateMatching(matchingId, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matchings'] });
      queryClient.invalidateQueries({ queryKey: ['matching-analytics'] });
      setMessage({ type: 'success', text: '상태가 변경되었습니다.' });
    },
    onError: () => {
      setMessage({ type: 'error', text: '상태 변경에 실패했습니다.' });
    },
  });

  const createMatchingMutation = useMutation({
    mutationFn: matchingsApi.createMatching,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matchings'] });
      queryClient.invalidateQueries({ queryKey: ['matching-analytics'] });
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
      setMessage({ type: 'success', text: '매칭이 생성되었습니다.' });
      setManualExpert('');
      setManualDemand('');
    },
    onError: () => {
      setMessage({ type: 'error', text: '매칭 생성에 실패했습니다.' });
    },
  });

  const matchings = matchingsData?.items || [];
  const demands = demandsData?.items || [];
  const experts = expertsData?.items?.map((e: { id: string; user?: { name: string } }) => ({
    id: e.id,
    name: e.user?.name || 'Unknown',
  })) || [];

  const columns: Column<Matching>[] = [
    {
      key: 'id',
      header: '매칭 ID',
      render: (_, row) => (
        <span className="font-mono text-sm">{row.id.slice(0, 8)}</span>
      ),
    },
    {
      key: 'expert_id',
      header: '컨설턴트',
      render: (_, row) => (
        <div>
          <p className="font-medium">{row.expert_id.slice(0, 8)}</p>
          {row.match_score && (
            <p className="text-xs text-gray-500">점수: {row.match_score.toFixed(1)}점</p>
          )}
        </div>
      ),
    },
    {
      key: 'demand_id',
      header: '수요',
      render: (_, row) => (
        <div>
          <p className="font-medium">{row.demand_id.slice(0, 8)}</p>
        </div>
      ),
    },
    {
      key: 'matching_type',
      header: '유형',
      render: (value) => (
        <Badge variant={value === 'AUTO' ? 'default' : 'warning'}>
          {value === 'AUTO' ? '자동' : '수동'}
        </Badge>
      ),
    },
    {
      key: 'status',
      header: '상태',
      render: (value) => (
        <Badge variant={STATUS_VARIANTS[value as MatchingStatus]}>
          {STATUS_LABELS[value as MatchingStatus]}
        </Badge>
      ),
    },
    {
      key: 'created_at',
      header: '생성일',
      render: (value) => format(new Date(value as string), 'yyyy-MM-dd HH:mm', { locale: ko }),
    },
    {
      key: 'actions',
      header: '관리',
      render: (_, row) => (
        <div className="flex gap-2">
          {row.status === 'PROPOSED' && (
            <>
              <Button
                size="sm"
                variant="outline"
                onClick={() => updateStatusMutation.mutate({ matchingId: row.id, status: 'ACCEPTED' })}
              >
                수락
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => updateStatusMutation.mutate({ matchingId: row.id, status: 'REJECTED' })}
              >
                거절
              </Button>
            </>
          )}
          {row.status === 'ACCEPTED' && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => updateStatusMutation.mutate({ matchingId: row.id, status: 'IN_PROGRESS' })}
            >
              진행 시작
            </Button>
          )}
          {row.status === 'IN_PROGRESS' && (
            <Button
              size="sm"
              variant="primary"
              onClick={() => updateStatusMutation.mutate({ matchingId: row.id, status: 'COMPLETED' })}
            >
              완료
            </Button>
          )}
        </div>
      ),
    },
  ];

  const handlePropose = (expertId: string) => {
    if (!selectedDemand) return;

    createMatchingMutation.mutate({
      expert_id: expertId,
      demand_id: selectedDemand,
      matching_type: 'AUTO',
      matching_reason: 'AI 추천 알고리즘 기반 매칭',
    });
  };

  const handleManualMatch = () => {
    if (!manualExpert || !manualDemand) {
      setMessage({ type: 'error', text: '컨설턴트와 수요를 모두 선택해주세요.' });
      return;
    }

    createMatchingMutation.mutate({
      expert_id: manualExpert,
      demand_id: manualDemand,
      matching_type: 'MANUAL',
      matching_reason: '운영자 수동 매칭',
    });
  };

  const stats = {
    total: matchings.length,
    proposed: matchings.filter((m) => m.status === 'PROPOSED').length,
    accepted: matchings.filter((m) => m.status === 'ACCEPTED').length,
    inProgress: matchings.filter((m) => m.status === 'IN_PROGRESS').length,
    completed: matchings.filter((m) => m.status === 'COMPLETED').length,
  };

  const demandOptions = demands.map((d: { id: string; title: string; company?: { name: string } }) => ({
    value: d.id,
    label: `${d.title} (${d.company?.name || 'Unknown'})`,
  }));

  const expertOptions = experts.map((e: { id: string; name: string }) => ({
    value: e.id,
    label: e.name,
  }));

  if (matchingsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">매칭 관리</h1>
          <p className="mt-2 text-gray-600">컨설턴트와 기업 수요를 매칭하세요</p>
        </div>
      </div>

      {message && (
        <Alert type={message.type} onClose={() => setMessage(null)}>
          {message.text}
        </Alert>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <Card>
          <div className="p-6">
            <p className="text-sm font-medium text-gray-600">총 매칭</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <p className="text-sm font-medium text-gray-600">제안됨</p>
            <p className="text-3xl font-bold text-gray-600 mt-2">{stats.proposed}</p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <p className="text-sm font-medium text-gray-600">수락</p>
            <p className="text-3xl font-bold text-blue-600 mt-2">{stats.accepted}</p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <p className="text-sm font-medium text-gray-600">진행중</p>
            <p className="text-3xl font-bold text-yellow-600 mt-2">{stats.inProgress}</p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <p className="text-sm font-medium text-gray-600">완료</p>
            <p className="text-3xl font-bold text-green-600 mt-2">{stats.completed}</p>
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'list', label: '매칭 목록' },
            { id: 'recommendations', label: 'AI 추천' },
            { id: 'analytics', label: '분석' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as 'list' | 'recommendations' | 'analytics')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'list' && (
        <>
          {/* Matchings List */}
          <Card>
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">매칭 목록</h2>
              <Table
                columns={columns}
                data={matchings}
                keyField="id"
                emptyMessage="매칭 내역이 없습니다."
              />
            </div>
          </Card>

          {/* Manual Matching Section */}
          <Card>
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">수동 매칭</h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Select
                  label="수요 선택"
                  placeholder="수요를 선택하세요"
                  options={demandOptions}
                  value={manualDemand}
                  onChange={(e) => setManualDemand(e.target.value)}
                />

                <Select
                  label="컨설턴트 선택"
                  placeholder="컨설턴트를 선택하세요"
                  options={expertOptions}
                  value={manualExpert}
                  onChange={(e) => setManualExpert(e.target.value)}
                />

                <div className="flex items-end">
                  <Button
                    className="w-full"
                    onClick={handleManualMatch}
                    disabled={createMatchingMutation.isPending}
                  >
                    {createMatchingMutation.isPending ? '생성 중...' : '매칭 생성'}
                  </Button>
                </div>
              </div>

              <p className="text-sm text-gray-600 mt-4">
                수동으로 특정 컨설턴트를 수요에 매칭하려면 위에서 선택하세요.
              </p>
            </div>
          </Card>
        </>
      )}

      {activeTab === 'recommendations' && (
        <div className="space-y-6">
          {/* Demand Selection */}
          <Card>
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">AI 컨설턴트 추천</h2>
              <p className="text-gray-600 mb-4">
                수요를 선택하면 AI가 가장 적합한 컨설턴트를 추천합니다.
                추천 알고리즘은 전문분야(40%), 평가성과(20%), 자격검증(15%), 경력(15%), 가용성(10%)을 종합적으로 분석합니다.
              </p>

              <div className="flex gap-4">
                <div className="flex-1">
                  <Select
                    label="수요 선택"
                    placeholder="추천받을 수요를 선택하세요"
                    options={demandOptions}
                    value={selectedDemand}
                    onChange={(e) => setSelectedDemand(e.target.value)}
                  />
                </div>
                <div className="flex items-end">
                  <Button
                    onClick={() => refetchRecommendations()}
                    disabled={!selectedDemand || recommendationsLoading}
                  >
                    {recommendationsLoading ? '분석 중...' : '추천 갱신'}
                  </Button>
                </div>
              </div>
            </div>
          </Card>

          {/* Recommendations Grid */}
          {selectedDemand && (
            <div>
              {recommendationsLoading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">AI가 컨설턴트를 분석하고 있습니다...</p>
                  </div>
                </div>
              ) : recommendationsData?.candidates && recommendationsData.candidates.length > 0 ? (
                <>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">
                      추천 컨설턴트 ({recommendationsData.total_candidates}명)
                    </h3>
                    <span className="text-sm text-gray-500">
                      알고리즘 버전: {recommendationsData.algorithm_version}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {recommendationsData.candidates.map((candidate: RecommendedCandidate) => (
                      <RecommendationCard
                        key={candidate.expert_id}
                        candidate={candidate}
                        onPropose={handlePropose}
                        onViewDetails={(id) => window.open(`/admin/experts/${id}`, '_blank')}
                        isLoading={createMatchingMutation.isPending}
                      />
                    ))}
                  </div>
                </>
              ) : (
                <Card>
                  <div className="p-12 text-center">
                    <svg
                      className="mx-auto h-12 w-12 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <h3 className="mt-4 text-lg font-medium text-gray-900">추천 결과 없음</h3>
                    <p className="mt-2 text-gray-500">
                      현재 조건에 맞는 컨설턴트가 없습니다. 최소 점수 기준을 낮춰보세요.
                    </p>
                  </div>
                </Card>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Success Rate */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">매칭 성공률</h3>
              <div className="flex items-center justify-center">
                <div className="relative w-40 h-40">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="#e5e7eb"
                      strokeWidth="12"
                      fill="none"
                    />
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="#22c55e"
                      strokeWidth="12"
                      fill="none"
                      strokeDasharray={`${(analyticsData?.success_rate || 0) * 4.4} 440`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-3xl font-bold text-gray-900">
                      {analyticsData?.success_rate?.toFixed(1) || 0}%
                    </span>
                  </div>
                </div>
              </div>
              <p className="text-center text-gray-600 mt-4">
                완료된 매칭 / 전체 종료된 매칭
              </p>
            </div>
          </Card>

          {/* Average Score */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">평균 매칭 점수</h3>
              <div className="text-center py-8">
                <p className="text-5xl font-bold text-blue-600">
                  {analyticsData?.average_match_score?.toFixed(1) || 0}
                </p>
                <p className="text-gray-600 mt-2">/ 100점</p>
              </div>
            </div>
          </Card>

          {/* Status Distribution */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">상태별 분포</h3>
              <div className="space-y-3">
                {Object.entries(analyticsData?.status_distribution || {}).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Badge variant={STATUS_VARIANTS[status as MatchingStatus] || 'default'}>
                        {STATUS_LABELS[status as MatchingStatus] || status}
                      </Badge>
                    </div>
                    <span className="font-medium">{count as number}건</span>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          {/* Top Matched Experts */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">매칭 많은 컨설턴트 TOP 5</h3>
              <div className="space-y-3">
                {analyticsData?.top_matched_experts?.map((expert, idx) => (
                  <div key={expert.expert_id} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <span className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-sm font-medium mr-3 ${
                        idx === 0 ? 'bg-yellow-500' :
                        idx === 1 ? 'bg-gray-400' :
                        idx === 2 ? 'bg-amber-600' : 'bg-gray-300'
                      }`}>
                        {idx + 1}
                      </span>
                      <span className="font-mono text-sm">{expert.expert_id.slice(0, 8)}...</span>
                    </div>
                    <span className="font-medium">{expert.match_count}회</span>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          {/* Summary Stats */}
          <Card className="md:col-span-2">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">요약</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <p className="text-3xl font-bold text-gray-900">
                    {analyticsData?.total_active_matchings || 0}
                  </p>
                  <p className="text-gray-600">활성 매칭</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-600">
                    {analyticsData?.total_completed || 0}
                  </p>
                  <p className="text-gray-600">완료된 매칭</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-600">
                    {analyticsData?.success_rate?.toFixed(1) || 0}%
                  </p>
                  <p className="text-gray-600">성공률</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-purple-600">
                    {analyticsData?.average_match_score?.toFixed(1) || 0}
                  </p>
                  <p className="text-gray-600">평균 점수</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
