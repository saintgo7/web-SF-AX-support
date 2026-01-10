'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axiosInstance from '@/lib/axios';
import { Evaluation, Answer, EvaluationSession, GradingStatistics, AIGradeResponse, ExpertScoreResponse } from '@/types';

export interface PendingAnswer {
  answer_id: string;
  question_id: string;
  question_content: string;
  question_type: string;
  max_score: number;
  response_data: Record<string, unknown>;
  created_at: string;
}

export interface ExpertPendingAnswers {
  expert_id: string;
  expert_name: string;
  pending_count: number;
  total_max_score: number;
  answers: PendingAnswer[];
}

export function useEvaluation() {
  const queryClient = useQueryClient();

  const getEvaluations = async (params?: { status?: string; page?: number }) => {
    const { data } = await axiosInstance.get('/evaluations', { params });
    return data;
  };

  const getEvaluationById = async (id: string) => {
    const { data } = await axiosInstance.get<Evaluation>(`/evaluations/${id}`);
    return data;
  };

  const startEvaluation = async (evaluationId: string) => {
    const { data } = await axiosInstance.post<EvaluationSession>(`/evaluations/${evaluationId}/start`);
    return data;
  };

  const submitAnswer = async (evaluationId: string, answer: Answer) => {
    const { data } = await axiosInstance.post(`/evaluations/${evaluationId}/answer`, answer);
    return data;
  };

  const submitEvaluation = async (evaluationId: string) => {
    const { data } = await axiosInstance.post(`/evaluations/${evaluationId}/submit`);
    return data;
  };

  const scoreAnswer = async (evaluationId: string, questionId: string, score: number, note?: string) => {
    const { data } = await axiosInstance.post(`/evaluations/${evaluationId}/score`, {
      question_id: questionId,
      score,
      note,
    });
    return data;
  };

  const getPendingByExpert = async (): Promise<ExpertPendingAnswers[]> => {
    const { data } = await axiosInstance.get<ExpertPendingAnswers[]>('/evaluation/pending-by-expert');
    return data;
  };

  const gradeAnswerManual = async (answerId: string, score: number, comment?: string) => {
    const { data } = await axiosInstance.post(`/evaluation/grade/${answerId}/manual`, {
      score,
      grader_comment: comment,
    });
    return data;
  };

  const getGradingStatistics = async (): Promise<GradingStatistics> => {
    const { data } = await axiosInstance.get<GradingStatistics>('/evaluation/statistics');
    return data;
  };

  const requestAIGrade = async (answerId: string): Promise<AIGradeResponse> => {
    const { data } = await axiosInstance.post<AIGradeResponse>('/evaluation/grade/ai', {
      answer_id: answerId,
    });
    return data;
  };

  const getExpertScore = async (expertId: string): Promise<ExpertScoreResponse> => {
    const { data } = await axiosInstance.get<ExpertScoreResponse>(`/evaluation/scores/${expertId}`);
    return data;
  };

  const recalculateExpertScore = async (expertId: string) => {
    const { data } = await axiosInstance.post(`/evaluation/scores/${expertId}/recalculate`);
    return data;
  };

  return {
    getEvaluations: (params?: any) => useQuery({
      queryKey: ['evaluations', params],
      queryFn: () => getEvaluations(params),
    }),
    getEvaluationById: (id: string) => useQuery({
      queryKey: ['evaluation', id],
      queryFn: () => getEvaluationById(id),
      enabled: !!id,
    }),
    startEvaluation: useMutation({
      mutationFn: startEvaluation,
    }),
    submitAnswer: useMutation({
      mutationFn: ({ evaluationId, answer }: { evaluationId: string; answer: Answer }) =>
        submitAnswer(evaluationId, answer),
    }),
    submitEvaluation: useMutation({
      mutationFn: submitEvaluation,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['evaluations'] });
      },
    }),
    scoreAnswer: useMutation({
      mutationFn: ({ evaluationId, questionId, score, note }: {
        evaluationId: string;
        questionId: string;
        score: number;
        note?: string;
      }) => scoreAnswer(evaluationId, questionId, score, note),
    }),
    getPendingByExpert: () => useQuery({
      queryKey: ['pending-by-expert'],
      queryFn: getPendingByExpert,
    }),
    gradeAnswerManual: useMutation({
      mutationFn: ({ answerId, score, comment }: {
        answerId: string;
        score: number;
        comment?: string;
      }) => gradeAnswerManual(answerId, score, comment),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['pending-by-expert'] });
      },
    }),
    getGradingStatistics: () => useQuery({
      queryKey: ['grading-statistics'],
      queryFn: getGradingStatistics,
      refetchInterval: 60000, // Refresh every minute
    }),
    requestAIGrade: useMutation({
      mutationFn: (answerId: string) => requestAIGrade(answerId),
    }),
    getExpertScore: (expertId: string) => useQuery({
      queryKey: ['expert-score', expertId],
      queryFn: () => getExpertScore(expertId),
      enabled: !!expertId,
    }),
    recalculateExpertScore: useMutation({
      mutationFn: (expertId: string) => recalculateExpertScore(expertId),
      onSuccess: (_, expertId) => {
        queryClient.invalidateQueries({ queryKey: ['expert-score', expertId] });
      },
    }),
  };
}
