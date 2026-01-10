'use client';

import { useAuth } from '@/hooks';
import { Header, Sidebar } from '@/components/layout';

export default function ApplicantLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  useAuth('APPLICANT');

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar role="APPLICANT" />
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
