'use client';

import { useRouter, usePathname } from 'next/navigation';
import { clsx } from 'clsx';

interface SidebarItem {
  label: string;
  path: string;
  icon?: React.ReactNode;
}

interface SidebarProps {
  role: 'APPLICANT' | 'EVALUATOR' | 'ADMIN';
  items: SidebarItem[];
}

const menuItems: Record<
  string,
  Record<string, SidebarItem[]>
> = {
  APPLICANT: {
    main: [
      { label: '대시보드', path: '/applicant/dashboard' },
      { label: '신청서 작성', path: '/applicant/application' },
      { label: '평가 응시', path: '/applicant/evaluation' },
      { label: '결과 조회', path: '/applicant/results' },
    ],
  },
  EVALUATOR: {
    main: [
      { label: '대시보드', path: '/evaluator/dashboard' },
      { label: '채점 대기', path: '/evaluator/pending' },
      { label: '채점 완료', path: '/evaluator/history' },
    ],
  },
  ADMIN: {
    main: [
      { label: '대시보드', path: '/admin/dashboard' },
      { label: '전문가 관리', path: '/admin/experts' },
      { label: '문항 관리', path: '/admin/questions' },
      { label: '매칭 관리', path: '/admin/matching' },
      { label: '리포트', path: '/admin/reports' },
    ],
  },
};

export default function Sidebar({ role }: Omit<SidebarProps, 'items'>) {
  const router = useRouter();
  const pathname = usePathname();
  const items = menuItems[role]?.main || [];

  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen">
      <nav className="p-4 space-y-1">
        {items.map((item) => {
          const isActive = pathname === item.path || pathname.startsWith(item.path + '/');
          return (
            <button
              key={item.path}
              onClick={() => router.push(item.path)}
              className={clsx(
                'w-full text-left px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-100'
              )}
            >
              {item.label}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
