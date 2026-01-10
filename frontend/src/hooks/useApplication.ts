'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axiosInstance from '@/lib/axios';
import { Application, ApplicationDraft, PaginatedResponse } from '@/types';

export function useApplication() {
  const queryClient = useQueryClient();

  const getApplications = async (params?: { page?: number; page_size?: number }) => {
    const { data } = await axiosInstance.get<PaginatedResponse<Application>>('/applications', { params });
    return data;
  };

  const getApplicationById = async (id: string) => {
    const { data } = await axiosInstance.get<Application>(`/applications/${id}`);
    return data;
  };

  const createApplication = async (draft: ApplicationDraft) => {
    const { data } = await axiosInstance.post<Application>('/applications', draft);
    return data;
  };

  const updateApplication = async (id: string, draft: Partial<ApplicationDraft>) => {
    const { data } = await axiosInstance.put<Application>(`/applications/${id}`, draft);
    return data;
  };

  const submitApplication = async (id: string) => {
    const { data } = await axiosInstance.post<Application>(`/applications/${id}/submit`);
    return data;
  };

  return {
    getApplications: (params?: any) => useQuery({
      queryKey: ['applications', params],
      queryFn: () => getApplications(params),
    }),
    getApplicationById: (id: string) => useQuery({
      queryKey: ['application', id],
      queryFn: () => getApplicationById(id),
      enabled: !!id,
    }),
    createApplication: useMutation({
      mutationFn: createApplication,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['applications'] });
      },
    }),
    updateApplication: useMutation({
      mutationFn: ({ id, draft }: { id: string; draft: Partial<ApplicationDraft> }) =>
        updateApplication(id, draft),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['applications'] });
      },
    }),
    submitApplication: useMutation({
      mutationFn: submitApplication,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['applications'] });
      },
    }),
  };
}
