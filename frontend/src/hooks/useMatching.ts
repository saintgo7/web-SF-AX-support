/**
 * React Query hooks for matching operations.
 *
 * Provides type-safe hooks for:
 * - Core CRUD operations
 * - Auto-matching
 * - Intelligent recommendations (Sprint 6)
 * - Analytics
 */
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { matchingsApi } from '@/lib/api/matchings';
import type {
  MatchingStatus,
  MatchingCreate,
  MatchingUpdate,
  MatchingExpertResponse,
  MatchingCompanyFeedback,
  AutoMatchRequest,
  RecommendRequest,
} from '@/types/matching';

// Query keys for cache management
export const matchingKeys = {
  all: ['matchings'] as const,
  lists: () => [...matchingKeys.all, 'list'] as const,
  list: (params?: { page?: number; page_size?: number; status?: MatchingStatus }) =>
    [...matchingKeys.lists(), params] as const,
  details: () => [...matchingKeys.all, 'detail'] as const,
  detail: (id: string) => [...matchingKeys.details(), id] as const,
  expert: (expertId: string) => [...matchingKeys.all, 'expert', expertId] as const,
  demand: (demandId: string) => [...matchingKeys.all, 'demand', demandId] as const,
  summary: () => [...matchingKeys.all, 'summary'] as const,
  analytics: () => [...matchingKeys.all, 'analytics'] as const,
  recommendations: (demandId: string) =>
    [...matchingKeys.all, 'recommendations', demandId] as const,
  compatibility: (expertId: string, demandId: string) =>
    [...matchingKeys.all, 'compatibility', expertId, demandId] as const,
};

/**
 * Hook for matching operations
 */
export function useMatching() {
  const queryClient = useQueryClient();

  return {
    // =========================================================================
    // Query Hooks
    // =========================================================================

    /**
     * Get paginated list of matchings
     */
    getMatchings: (params?: {
      page?: number;
      page_size?: number;
      status?: MatchingStatus;
    }) =>
      useQuery({
        queryKey: matchingKeys.list(params),
        queryFn: () => matchingsApi.getMatchings(params),
      }),

    /**
     * Get matching by ID
     */
    getMatching: (matchingId: string) =>
      useQuery({
        queryKey: matchingKeys.detail(matchingId),
        queryFn: () => matchingsApi.getMatching(matchingId),
        enabled: !!matchingId,
      }),

    /**
     * Get matchings for a specific expert
     */
    getExpertMatchings: (
      expertId: string,
      params?: { page?: number; page_size?: number }
    ) =>
      useQuery({
        queryKey: matchingKeys.expert(expertId),
        queryFn: () => matchingsApi.getExpertMatchings(expertId, params),
        enabled: !!expertId,
      }),

    /**
     * Get matching summary statistics
     */
    getSummary: () =>
      useQuery({
        queryKey: matchingKeys.summary(),
        queryFn: () => matchingsApi.getSummary(),
      }),

    /**
     * Get matching analytics (Sprint 6)
     */
    getAnalytics: () =>
      useQuery({
        queryKey: matchingKeys.analytics(),
        queryFn: () => matchingsApi.getAnalytics(),
        refetchInterval: 60000, // Refresh every minute
      }),

    /**
     * Get intelligent recommendations for a demand (Sprint 6)
     */
    getRecommendations: (request: RecommendRequest) =>
      useQuery({
        queryKey: matchingKeys.recommendations(request.demand_id),
        queryFn: () => matchingsApi.getRecommendations(request),
        enabled: !!request.demand_id,
      }),

    /**
     * Check compatibility between expert and demand (Sprint 6)
     */
    checkCompatibility: (expertId: string, demandId: string) =>
      useQuery({
        queryKey: matchingKeys.compatibility(expertId, demandId),
        queryFn: () => matchingsApi.checkCompatibility(expertId, demandId),
        enabled: !!expertId && !!demandId,
      }),

    // =========================================================================
    // Mutation Hooks
    // =========================================================================

    /**
     * Create manual matching
     */
    createMatching: useMutation({
      mutationFn: (data: MatchingCreate) => matchingsApi.createMatching(data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: matchingKeys.lists() });
        queryClient.invalidateQueries({ queryKey: matchingKeys.summary() });
        queryClient.invalidateQueries({ queryKey: matchingKeys.analytics() });
      },
    }),

    /**
     * Update matching
     */
    updateMatching: useMutation({
      mutationFn: ({
        matchingId,
        data,
      }: {
        matchingId: string;
        data: MatchingUpdate;
      }) => matchingsApi.updateMatching(matchingId, data),
      onSuccess: (_, { matchingId }) => {
        queryClient.invalidateQueries({ queryKey: matchingKeys.detail(matchingId) });
        queryClient.invalidateQueries({ queryKey: matchingKeys.lists() });
        queryClient.invalidateQueries({ queryKey: matchingKeys.summary() });
      },
    }),

    /**
     * Delete matching
     */
    deleteMatching: useMutation({
      mutationFn: (matchingId: string) => matchingsApi.deleteMatching(matchingId),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: matchingKeys.lists() });
        queryClient.invalidateQueries({ queryKey: matchingKeys.summary() });
        queryClient.invalidateQueries({ queryKey: matchingKeys.analytics() });
      },
    }),

    /**
     * Expert response to matching proposal
     */
    respondToMatching: useMutation({
      mutationFn: ({
        matchingId,
        response,
      }: {
        matchingId: string;
        response: MatchingExpertResponse;
      }) => matchingsApi.respondToMatching(matchingId, response),
      onSuccess: (_, { matchingId }) => {
        queryClient.invalidateQueries({ queryKey: matchingKeys.detail(matchingId) });
        queryClient.invalidateQueries({ queryKey: matchingKeys.lists() });
        queryClient.invalidateQueries({ queryKey: matchingKeys.summary() });
      },
    }),

    /**
     * Submit company feedback
     */
    submitFeedback: useMutation({
      mutationFn: ({
        matchingId,
        feedback,
      }: {
        matchingId: string;
        feedback: MatchingCompanyFeedback;
      }) => matchingsApi.submitFeedback(matchingId, feedback),
      onSuccess: (_, { matchingId }) => {
        queryClient.invalidateQueries({ queryKey: matchingKeys.detail(matchingId) });
        queryClient.invalidateQueries({ queryKey: matchingKeys.lists() });
      },
    }),

    /**
     * Auto-match for a demand
     */
    autoMatch: useMutation({
      mutationFn: (request: AutoMatchRequest) => matchingsApi.autoMatch(request),
    }),

    /**
     * Create matchings from auto-match candidates
     */
    createAutoMatchings: useMutation({
      mutationFn: ({
        demandId,
        expertIds,
      }: {
        demandId: string;
        expertIds: string[];
      }) => matchingsApi.createAutoMatchings(demandId, expertIds),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: matchingKeys.lists() });
        queryClient.invalidateQueries({ queryKey: matchingKeys.summary() });
        queryClient.invalidateQueries({ queryKey: matchingKeys.analytics() });
      },
    }),

    /**
     * Get intelligent recommendations (mutation for on-demand fetching)
     */
    fetchRecommendations: useMutation({
      mutationFn: (request: RecommendRequest) =>
        matchingsApi.getRecommendations(request),
    }),

    /**
     * Check compatibility (mutation for on-demand fetching)
     */
    fetchCompatibility: useMutation({
      mutationFn: ({
        expertId,
        demandId,
      }: {
        expertId: string;
        demandId: string;
      }) => matchingsApi.checkCompatibility(expertId, demandId),
    }),
  };
}

// Default export
export default useMatching;
