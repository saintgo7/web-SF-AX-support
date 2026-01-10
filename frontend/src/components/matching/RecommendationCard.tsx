/**
 * RecommendationCard - Displays intelligent match recommendation
 *
 * Shows expert information with detailed score breakdown and recommendation reasons.
 * Used in the matching page for displaying AI-powered expert recommendations.
 */
'use client';

import { useState } from 'react';
import type {
  RecommendedCandidate,
  MatchScoreBreakdown,
} from '@/types/matching';

interface RecommendationCardProps {
  candidate: RecommendedCandidate;
  onPropose?: (expertId: string) => void;
  onSkip?: (expertId: string) => void;
  onViewDetails?: (expertId: string) => void;
  isLoading?: boolean;
}

// Score bar component for visual representation
function ScoreBar({
  label,
  score,
  maxScore = 100,
  weight,
}: {
  label: string;
  score: number;
  maxScore?: number;
  weight: string;
}) {
  const percentage = Math.min((score / maxScore) * 100, 100);
  const getBarColor = (pct: number) => {
    if (pct >= 80) return 'bg-green-500';
    if (pct >= 60) return 'bg-blue-500';
    if (pct >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="mb-2">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">
          {label} <span className="text-gray-400">({weight})</span>
        </span>
        <span className="font-medium">{score.toFixed(1)}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${getBarColor(percentage)}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

// Radar chart for score visualization (simplified CSS-based)
function ScoreRadar({ breakdown }: { breakdown: MatchScoreBreakdown }) {
  const scores = [
    { label: '전문분야', value: breakdown.specialty, angle: 0 },
    { label: '자격검증', value: breakdown.qualification, angle: 72 },
    { label: '경력', value: breakdown.career, angle: 144 },
    { label: '평가', value: breakdown.evaluation, angle: 216 },
    { label: '가용성', value: breakdown.availability, angle: 288 },
  ];

  return (
    <div className="relative w-32 h-32 mx-auto">
      {/* Center point */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-2 h-2 bg-blue-500 rounded-full" />
      </div>
      {/* Score points */}
      {scores.map((score, i) => {
        const radius = (score.value / 100) * 50;
        const x = 64 + radius * Math.cos((score.angle - 90) * (Math.PI / 180));
        const y = 64 + radius * Math.sin((score.angle - 90) * (Math.PI / 180));

        return (
          <div
            key={i}
            className="absolute w-3 h-3 bg-blue-500 rounded-full transform -translate-x-1/2 -translate-y-1/2 opacity-80"
            style={{ left: x, top: y }}
            title={`${score.label}: ${score.value.toFixed(1)}`}
          />
        );
      })}
    </div>
  );
}

export function RecommendationCard({
  candidate,
  onPropose,
  onSkip,
  onViewDetails,
  isLoading = false,
}: RecommendationCardProps) {
  const [showDetails, setShowDetails] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 60) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getQualificationBadge = (status: string) => {
    const badges: Record<string, { color: string; label: string }> = {
      QUALIFIED: { color: 'bg-green-100 text-green-800', label: '인증됨' },
      PENDING: { color: 'bg-yellow-100 text-yellow-800', label: '심사중' },
      DISQUALIFIED: { color: 'bg-red-100 text-red-800', label: '미인증' },
    };
    return badges[status] || { color: 'bg-gray-100 text-gray-800', label: status };
  };

  const qualification = getQualificationBadge(candidate.qualification_status);

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {candidate.expert_name}
            </h3>
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${qualification.color}`}
            >
              {qualification.label}
            </span>
          </div>
          <div
            className={`px-3 py-2 rounded-lg border ${getScoreColor(candidate.total_score)}`}
          >
            <div className="text-2xl font-bold">
              {candidate.total_score.toFixed(1)}
            </div>
            <div className="text-xs text-center">점</div>
          </div>
        </div>
      </div>

      {/* Specialties */}
      {candidate.specialties && candidate.specialties.length > 0 && (
        <div className="px-4 py-3 border-b border-gray-100">
          <div className="text-sm text-gray-500 mb-2">전문분야</div>
          <div className="flex flex-wrap gap-1">
            {candidate.specialties.map((specialty, i) => (
              <span
                key={i}
                className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-700"
              >
                {specialty}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recommendation Reasons */}
      <div className="px-4 py-3 border-b border-gray-100">
        <div className="text-sm text-gray-500 mb-2">추천 이유</div>
        <ul className="space-y-1">
          {candidate.recommendation_reasons.map((reason, i) => (
            <li key={i} className="flex items-center text-sm text-gray-700">
              <svg
                className="w-4 h-4 mr-2 text-green-500 flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              {reason}
            </li>
          ))}
        </ul>
      </div>

      {/* Expandable Score Breakdown */}
      <div className="px-4 py-3">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="flex items-center justify-between w-full text-sm text-gray-600 hover:text-gray-900"
        >
          <span>점수 상세</span>
          <svg
            className={`w-5 h-5 transition-transform ${showDetails ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>

        {showDetails && (
          <div className="mt-4 space-y-1">
            <ScoreBar
              label="전문분야 일치"
              score={candidate.score_breakdown.specialty}
              weight="40%"
            />
            <ScoreBar
              label="평가 성과"
              score={candidate.score_breakdown.evaluation}
              weight="20%"
            />
            <ScoreBar
              label="자격 검증"
              score={candidate.score_breakdown.qualification}
              weight="15%"
            />
            <ScoreBar
              label="경력"
              score={candidate.score_breakdown.career}
              weight="15%"
            />
            <ScoreBar
              label="가용성"
              score={candidate.score_breakdown.availability}
              weight="10%"
            />
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="px-4 py-3 bg-gray-50 rounded-b-lg flex gap-2">
        <button
          onClick={() => onPropose?.(candidate.expert_id)}
          disabled={isLoading}
          className="flex-1 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          매칭 제안
        </button>
        <button
          onClick={() => onViewDetails?.(candidate.expert_id)}
          className="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-100 transition-colors"
        >
          상세보기
        </button>
        <button
          onClick={() => onSkip?.(candidate.expert_id)}
          className="px-4 py-2 text-gray-500 text-sm hover:text-gray-700 transition-colors"
          title="건너뛰기"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default RecommendationCard;
