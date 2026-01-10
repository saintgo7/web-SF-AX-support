import { create } from 'zustand';
import { Expert } from '@/types';

interface ExpertState {
  currentExpert: Expert | null;
  experts: Expert[];
  isLoading: boolean;
  error: string | null;
  setCurrentExpert: (expert: Expert | null) => void;
  setExperts: (experts: Expert[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useExpertStore = create<ExpertState>((set) => ({
  currentExpert: null,
  experts: [],
  isLoading: false,
  error: null,
  setCurrentExpert: (expert) => set({ currentExpert: expert }),
  setExperts: (experts) => set({ experts }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
}));
