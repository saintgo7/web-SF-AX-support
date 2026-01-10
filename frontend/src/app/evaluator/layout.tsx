'use client';

import { useAuth } from '@/hooks';
import { Header, Sidebar } from '@/components/layout';

export default function EvaluatorLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  useAuth('EVALUATOR');

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar role="EVALUATOR" />
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
