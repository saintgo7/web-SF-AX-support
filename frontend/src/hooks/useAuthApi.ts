'use client';

import { useMutation } from '@tanstack/react-query';
import axiosInstance from '@/lib/axios';
import { LoginRequest, LoginResponse, RegisterRequest } from '@/types';
import { useAuthStore } from '@/store';

export function useAuthApi() {
  const setAuth = useAuthStore((state) => state.setAuth);

  const login = useMutation({
    mutationFn: async (credentials: LoginRequest) => {
      const { data } = await axiosInstance.post<LoginResponse>('/auth/login', credentials);
      return data;
    },
    onSuccess: (data) => {
      setAuth(data);
    },
  });

  const register = useMutation({
    mutationFn: async (userData: RegisterRequest) => {
      const { data } = await axiosInstance.post<LoginResponse>('/auth/register', userData);
      return data;
    },
    onSuccess: (data) => {
      setAuth(data);
    },
  });

  const logout = useMutation({
    mutationFn: async () => {
      await axiosInstance.post('/auth/logout');
    },
  });

  return {
    login,
    register,
    logout,
  };
}
