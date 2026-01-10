'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axiosInstance from '@/lib/axios';
import { Expert, QualificationVerifyResponse } from '@/types';

export function useExpert() {
  const queryClient = useQueryClient();

  const getExpertProfile = async () => {
    const { data } = await axiosInstance.get<Expert>('/expert/profile');
    return data;
  };

  const updateExpertProfile = async (profileData: Partial<Expert>) => {
    const { data } = await axiosInstance.put<Expert>('/expert/profile', profileData);
    return data;
  };

  const verifyQualification = async () => {
    const { data } = await axiosInstance.post<QualificationVerifyResponse>('/expert/verify-qualification');
    return data;
  };

  return {
    getExpertProfile: () => useQuery({
      queryKey: ['expert', 'profile'],
      queryFn: getExpertProfile,
    }),
    updateExpertProfile: useMutation({
      mutationFn: updateExpertProfile,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['expert', 'profile'] });
      },
    }),
    verifyQualification: () => useMutation({
      mutationFn: verifyQualification,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['expert', 'profile'] });
      },
    }),
  };
}
