import { useRouter } from 'next/navigation';
import Button from '../ui/Button';

interface HeaderProps {
  user?: {
    name: string;
    email: string;
    role: string;
  } | null;
}

export default function Header({ user }: HeaderProps) {
  const router = useRouter();

  const handleLogout = () => {
    if (typeof window !== 'undefined') {
      localStorage.clear();
      router.push('/auth/login');
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <button
              onClick={() => router.push('/')}
              className="text-xl font-bold text-blue-600 hover:text-blue-700"
            >
              AX 코칭단 관리 시스템
            </button>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            {user && (
              <>
                {user.role === 'APPLICANT' && (
                  <>
                    <button
                      onClick={() => router.push('/applicant/dashboard')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      대시보드
                    </button>
                    <button
                      onClick={() => router.push('/applicant/application')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      신청서 작성
                    </button>
                    <button
                      onClick={() => router.push('/applicant/evaluation')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      평가 응시
                    </button>
                    <button
                      onClick={() => router.push('/applicant/results')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      결과 조회
                    </button>
                  </>
                )}
                {user.role === 'EVALUATOR' && (
                  <>
                    <button
                      onClick={() => router.push('/evaluator/dashboard')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      대시보드
                    </button>
                    <button
                      onClick={() => router.push('/evaluator/consultants')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      컨설턴트 현황
                    </button>
                    <button
                      onClick={() => router.push('/evaluator/matching')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      매칭 현황
                    </button>
                    <button
                      onClick={() => router.push('/evaluator/reports')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      보고서 작성
                    </button>
                    <button
                      onClick={() => router.push('/evaluator/grading')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      평가 채점
                    </button>
                  </>
                )}
                {user.role === 'ADMIN' && (
                  <>
                    <button
                      onClick={() => router.push('/admin/dashboard')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      대시보드
                    </button>
                    <button
                      onClick={() => router.push('/admin/experts')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      컨설턴트 관리
                    </button>
                    <button
                      onClick={() => router.push('/admin/questions')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      문항 관리
                    </button>
                    <button
                      onClick={() => router.push('/admin/matching')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      매칭 관리
                    </button>
                    <button
                      onClick={() => router.push('/admin/reports')}
                      className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                    >
                      리포트
                    </button>
                  </>
                )}
              </>
            )}
          </nav>

          {/* User menu */}
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-sm text-gray-700">{user.name}</span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogout}
                >
                  로그아웃
                </Button>
              </>
            ) : (
              <Button
                variant="primary"
                size="sm"
                onClick={() => router.push('/auth/login')}
              >
                로그인
              </Button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
