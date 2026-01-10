'use client';

import { useState } from 'react';
import { useEvaluation } from '@/hooks';
import { Card, Button, Alert, Badge } from '@/components/ui';
import { Evaluation, Answer } from '@/types';

export default function EvaluationPage() {
  const { getEvaluations, startEvaluation, submitAnswer, submitEvaluation } = useEvaluation();
  const { data: evaluationsData, isLoading } = getEvaluations({ status: 'IN_PROGRESS' });
  const { data: pendingEvaluations } = getEvaluations({ status: 'PENDING' });

  const [currentEvaluation, setCurrentEvaluation] = useState<Evaluation | null>(null);
  const [session, setSession] = useState<any>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleStartEvaluation = async (evaluation: Evaluation) => {
    try {
      setError(null);
      const result = await startEvaluation.mutateAsync(evaluation.id);
      setCurrentEvaluation(evaluation);
      setSession(result);
      setCurrentQuestionIndex(0);
      setAnswers([]);
    } catch (err: any) {
      setError(err.response?.data?.detail || '평가 시작에 실패했습니다.');
    }
  };

  const handleNextQuestion = () => {
    if (session && currentQuestionIndex < session.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleAnswerChange = (response: string) => {
    if (!session) return;

    const question = session.questions[currentQuestionIndex];
    const existingAnswerIndex = answers.findIndex(a => a.question_id === question.id);

    const newAnswer: Answer = {
      question_id: question.id,
      response,
    };

    if (existingAnswerIndex >= 0) {
      const newAnswers = [...answers];
      newAnswers[existingAnswerIndex] = newAnswer;
      setAnswers(newAnswers);
    } else {
      setAnswers([...answers, newAnswer]);
    }
  };

  const handleSubmitEvaluation = async () => {
    if (!currentEvaluation) return;

    try {
      setError(null);
      // Submit all answers
      for (const answer of answers) {
        await submitAnswer.mutateAsync({
          evaluationId: currentEvaluation.id,
          answer,
        });
      }

      // Submit evaluation
      await submitEvaluation.mutateAsync(currentEvaluation.id);

      setCurrentEvaluation(null);
      setSession(null);
      setCurrentQuestionIndex(0);
      setAnswers([]);
    } catch (err: any) {
      setError(err.response?.data?.detail || '제출에 실패했습니다.');
    }
  };

  const currentQuestion = session?.questions?.[currentQuestionIndex];
  const currentAnswer = answers.find(a => a.question_id === currentQuestion?.id);

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
        <h1 className="text-3xl font-bold text-gray-900">평가 응시</h1>
        <p className="mt-2 text-gray-600">
          진행 중인 평가를 완료하세요
        </p>
      </div>

      {error && (
        <Alert type="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {!currentEvaluation ? (
        <>
          {/* In Progress Evaluations */}
          <Card>
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                진행 중인 평가
              </h2>

              {evaluationsData?.items?.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p>진행 중인 평가가 없습니다.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {evaluationsData?.items?.map((evaluation: Evaluation) => (
                    <div
                      key={evaluation.id}
                      className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                    >
                      <div>
                        <h3 className="font-medium text-gray-900">
                          평가 ID: {evaluation.id.slice(0, 8)}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          최대 점수: {evaluation.max_score}점
                        </p>
                      </div>
                      <Button
                        onClick={() => handleStartEvaluation(evaluation)}
                        disabled={startEvaluation.isPending}
                      >
                        이어하기
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>

          {/* Pending Evaluations */}
          <Card>
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                대기 중인 평가
              </h2>

              {pendingEvaluations?.items?.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p>대기 중인 평가가 없습니다.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {pendingEvaluations?.items?.map((evaluation: Evaluation) => (
                    <div
                      key={evaluation.id}
                      className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                    >
                      <div>
                        <h3 className="font-medium text-gray-900">
                          평가 ID: {evaluation.id.slice(0, 8)}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          최대 점수: {evaluation.max_score}점
                        </p>
                      </div>
                      <Badge variant="warning">대기 중</Badge>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>
        </>
      ) : (
        <>
          {/* Question View */}
          <Card>
            <div className="p-6">
              <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-gray-900">
                    문항 {currentQuestionIndex + 1} / {session?.questions?.length}
                  </h2>
                  <Badge variant="info">
                    {currentQuestion?.category}
                  </Badge>
                </div>

                {session?.questions && (
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${((currentQuestionIndex + 1) / session.questions.length) * 100}%`,
                      }}
                    />
                  </div>
                )}

                <p className="text-sm text-gray-600 mb-2">
                  배점: {currentQuestion?.max_score}점
                </p>
                <p className="text-lg text-gray-900">
                  {currentQuestion?.content}
                </p>
              </div>

              <textarea
                value={currentAnswer?.response || ''}
                onChange={(e) => handleAnswerChange(e.target.value)}
                placeholder="답안을 입력하세요..."
                rows={10}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
              />

              <div className="flex justify-between mt-6">
                <Button
                  variant="outline"
                  onClick={handlePreviousQuestion}
                  disabled={currentQuestionIndex === 0}
                >
                  이전 문항
                </Button>

                {currentQuestionIndex < (session?.questions?.length || 0) - 1 ? (
                  <Button onClick={handleNextQuestion}>
                    다음 문항
                  </Button>
                ) : (
                  <Button
                    onClick={handleSubmitEvaluation}
                    isLoading={submitEvaluation.isPending}
                  >
                    제출하기
                  </Button>
                )}
              </div>
            </div>
          </Card>

          <Button
            variant="outline"
            onClick={() => {
              setCurrentEvaluation(null);
              setSession(null);
            }}
          >
            나가기
          </Button>
        </>
      )}
    </div>
  );
}
