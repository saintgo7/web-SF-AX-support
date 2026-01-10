'use client';

import { useAuth } from '@/hooks';
import { Header, Sidebar } from '@/components/layout';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  useAuth('ADMIN');

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar role="ADMIN" />
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
