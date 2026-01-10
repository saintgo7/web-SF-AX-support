'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store';

export function useAuth(requiredRole?: string) {
  const router = useRouter();
  const { user, isAuthenticated, clearAuth } = useAuthStore();

  useEffect(() => {
    // Check if user is authenticated
    if (!isAuthenticated) {
      router.push('/auth/login');
      return;
    }

    // Check role if required
    if (requiredRole && user?.role !== requiredRole) {
      router.push('/');
      return;
    }
  }, [isAuthenticated, user, requiredRole, router]);

  const logout = () => {
    clearAuth();
    router.push('/auth/login');
  };

  return {
    user,
    isAuthenticated,
    logout,
  };
}
