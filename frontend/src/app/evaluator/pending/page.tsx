'use client';

import { useState } from 'react';
import { Card, Button, Badge, Alert, Textarea } from '@/components/ui';
import { useEvaluation, ExpertPendingAnswers, PendingAnswer } from '@/hooks/useEvaluation';

export default function PendingPage() {
  const { getPendingByExpert, gradeAnswerManual } = useEvaluation();
  const { data: pendingData, isLoading, refetch } = getPendingByExpert();

  const [selectedExpert, setSelectedExpert] = useState<ExpertPendingAnswers | null>(null);
  const [currentAnswerIndex, setCurrentAnswerIndex] = useState(0);
  const [scores, setScores] = useState<Record<string, number>>({});
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleStartGrading = (expert: ExpertPendingAnswers) => {
    setSelectedExpert(expert);
    setCurrentAnswerIndex(0);
    setScores({});
    setNotes({});
    setError(null);
    setSuccess(null);
  };

  const handleScoreChange = (answerId: string, score: number) => {
    setScores({ ...scores, [answerId]: score });
  };

  const handleNoteChange = (answerId: string, note: string) => {
    setNotes({ ...notes, [answerId]: note });
  };

  const handleNextAnswer = () => {
    if (selectedExpert && currentAnswerIndex < selectedExpert.answers.length - 1) {
      setCurrentAnswerIndex(currentAnswerIndex + 1);
    }
  };

  const handlePrevAnswer = () => {
    if (currentAnswerIndex > 0) {
      setCurrentAnswerIndex(currentAnswerIndex - 1);
    }
  };

  const handleSubmitAllScores = async () => {
    if (!selectedExpert) return;

    const ungraded = selectedExpert.answers.filter(
      (a) => scores[a.answer_id] === undefined
    );

    if (ungraded.length > 0) {
      setError(`채점되지 않은 답변이 ${ungraded.length}개 있습니다. 모든 답변을 채점해주세요.`);
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      for (const answer of selectedExpert.answers) {
        await gradeAnswerManual.mutateAsync({
          answerId: answer.answer_id,
          score: scores[answer.answer_id],
          comment: notes[answer.answer_id],
        });
      }

      setSuccess('모든 채점이 완료되었습니다!');
      setSelectedExpert(null);
      setScores({});
      setNotes({});
      refetch();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || '채점 제출에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitCurrentAndNext = async () => {
    if (!selectedExpert) return;

    const currentAnswer = selectedExpert.answers[currentAnswerIndex];
    const score = scores[currentAnswer.answer_id];

    if (score === undefined) {
      setError('점수를 입력해주세요.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await gradeAnswerManual.mutateAsync({
        answerId: currentAnswer.answer_id,
        score,
        comment: notes[currentAnswer.answer_id],
      });

      if (currentAnswerIndex < selectedExpert.answers.length - 1) {
        setCurrentAnswerIndex(currentAnswerIndex + 1);
        setSuccess('채점이 저장되었습니다.');
      } else {
        setSuccess('모든 채점이 완료되었습니다!');
        setSelectedExpert(null);
        setScores({});
        setNotes({});
        refetch();
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || '채점 저장에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const currentAnswer = selectedExpert?.answers[currentAnswerIndex];

  const getQuestionTypeLabel = (type: string): string => {
    const types: Record<string, string> = {
      SINGLE: '단일 선택',
      MULTIPLE: '다중 선택',
      SHORT: '단답형',
      LONG: '서술형',
    };
    return types[type] || type;
  };

  const formatResponse = (responseData: Record<string, unknown>): string => {
    if (typeof responseData === 'string') return responseData;
    if (responseData.text) return String(responseData.text);
    if (responseData.answer) return String(responseData.answer);
    if (responseData.selected) {
      const selected = responseData.selected;
      if (Array.isArray(selected)) return selected.join(', ');
      return String(selected);
    }
    return JSON.stringify(responseData, null, 2);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">채점 대기 목록</h1>
        <p className="mt-2 text-gray-600">채점이 필요한 컨설턴트 답변 목록입니다</p>
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

      {!selectedExpert ? (
        <div className="grid grid-cols-1 gap-6">
          {!pendingData || pendingData.length === 0 ? (
            <Card>
              <div className="p-12 text-center text-gray-500">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <p className="mt-4">채점 대기 중인 답변이 없습니다.</p>
              </div>
            </Card>
          ) : (
            pendingData.map((expert: ExpertPendingAnswers) => (
              <Card key={expert.expert_id}>
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {expert.expert_name}
                        </h3>
                        <Badge variant="warning">
                          {expert.pending_count}개 대기
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">
                        컨설턴트 ID: {expert.expert_id.slice(0, 8)}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        총 배점: {expert.total_max_score}점
                      </p>
                    </div>

                    <Button onClick={() => handleStartGrading(expert)}>
                      채점 시작
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      ) : (
        <>
          {/* Progress */}
          <Card>
            <div className="p-4 bg-gray-50">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  {selectedExpert.expert_name} 채점 진행 중
                </span>
                <span className="text-sm text-gray-600">
                  {currentAnswerIndex + 1} / {selectedExpert.answers.length}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{
                    width: `${((currentAnswerIndex + 1) / selectedExpert.answers.length) * 100}%`,
                  }}
                />
              </div>
            </div>
          </Card>

          {/* Grading Interface */}
          {currentAnswer && (
            <Card>
              <div className="p-6">
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900">
                      문항 {currentAnswerIndex + 1}
                    </h2>
                    <Badge variant="info">
                      {getQuestionTypeLabel(currentAnswer.question_type)}
                    </Badge>
                  </div>

                  <p className="text-sm text-gray-600 mb-4">
                    배점: {currentAnswer.max_score}점
                  </p>

                  <div className="bg-gray-50 p-4 rounded-lg mb-6">
                    <p className="text-lg text-gray-900">
                      {currentAnswer.question_content}
                    </p>
                  </div>

                  {/* Answer Display */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      컨설턴트 답변
                    </label>
                    <div className="bg-blue-50 p-4 rounded-lg whitespace-pre-wrap">
                      <p className="text-gray-900">
                        {formatResponse(currentAnswer.response_data)}
                      </p>
                    </div>
                  </div>

                  {/* Score Input */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      점수 (0 - {currentAnswer.max_score})
                    </label>
                    <input
                      type="number"
                      min="0"
                      max={currentAnswer.max_score}
                      value={scores[currentAnswer.answer_id] ?? ''}
                      onChange={(e) =>
                        handleScoreChange(
                          currentAnswer.answer_id,
                          parseInt(e.target.value) || 0
                        )
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* Note Input */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      평가 노트 (선택)
                    </label>
                    <Textarea
                      value={notes[currentAnswer.answer_id] || ''}
                      onChange={(e) =>
                        handleNoteChange(currentAnswer.answer_id, e.target.value)
                      }
                      placeholder="평가 의견을 입력하세요..."
                      rows={4}
                    />
                  </div>
                </div>

                <div className="flex justify-between border-t pt-4">
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setSelectedExpert(null);
                        setScores({});
                        setNotes({});
                      }}
                    >
                      목록으로
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handlePrevAnswer}
                      disabled={currentAnswerIndex === 0}
                    >
                      이전
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleNextAnswer}
                      disabled={currentAnswerIndex === selectedExpert.answers.length - 1}
                    >
                      다음
                    </Button>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      variant="primary"
                      onClick={handleSubmitCurrentAndNext}
                      disabled={isSubmitting}
                    >
                      {isSubmitting
                        ? '저장 중...'
                        : currentAnswerIndex === selectedExpert.answers.length - 1
                        ? '채점 완료'
                        : '저장 후 다음'}
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          )}

          {/* Summary */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">채점 현황</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {selectedExpert.answers.map((answer, idx) => (
                  <button
                    key={answer.answer_id}
                    onClick={() => setCurrentAnswerIndex(idx)}
                    className={`p-3 rounded-lg border-2 text-left transition-colors ${
                      idx === currentAnswerIndex
                        ? 'border-blue-500 bg-blue-50'
                        : scores[answer.answer_id] !== undefined
                        ? 'border-green-300 bg-green-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <p className="text-sm font-medium">문항 {idx + 1}</p>
                    <p className="text-xs text-gray-500">
                      {scores[answer.answer_id] !== undefined
                        ? `${scores[answer.answer_id]}/${answer.max_score}점`
                        : '미채점'}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
