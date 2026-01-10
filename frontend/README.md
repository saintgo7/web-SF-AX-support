# AX 코칭단 평가 시스템 Frontend

스마트공장 AX 코칭단 전문가 평가 및 매칭 시스템의 Frontend 애플리케이션입니다.

## 기술 스택

- **Next.js 14** - React Framework
- **TypeScript** - 타입 안정성
- **Tailwind CSS** - 스타일링
- **Zustand** - 상태 관리
- **React Query** - 데이터 패칭
- **React Hook Form** - 폼 관리
- **Axios** - HTTP 클라이언트

## 프로젝트 구조

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── auth/                 # 인증 페이지
│   │   │   ├── login/           # 로그인
│   │   │   └── register/        # 회원가입
│   │   ├── applicant/            # 신청자 페이지
│   │   │   ├── dashboard/       # 대시보드
│   │   │   ├── application/     # 신청서 작성
│   │   │   ├── evaluation/      # 평가 응시
│   │   │   └── results/         # 결과 조회
│   │   ├── evaluator/            # 평가위원 페이지
│   │   │   ├── dashboard/       # 대시보드
│   │   │   ├── pending/         # 채점 대기 목록
│   │   │   └── history/         # 채점 완료 내역
│   │   ├── admin/                # 관리자 페이지
│   │   │   ├── dashboard/       # 대시보드
│   │   │   ├── experts/         # 전문가 관리
│   │   │   ├── questions/       # 문항 관리
│   │   │   ├── matching/        # 매칭 관리
│   │   │   └── reports/         # 리포트 생성
│   │   ├── layout.tsx           # 루트 레이아웃
│   │   └── page.tsx             # 홈 페이지
│   ├── components/               # React 컴포넌트
│   │   ├── ui/                  # 기본 UI 컴포넌트
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Textarea.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Alert.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Badge.tsx
│   │   │   └── index.ts
│   │   ├── layout/              # 레이아웃 컴포넌트
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── index.ts
│   │   └── index.ts
│   ├── hooks/                    # 커스텀 React Hooks
│   │   ├── useAuth.ts           # 인증 훅
│   │   ├── useAuthApi.ts        # 인증 API 훅
│   │   ├── useExpert.ts         # 전문가 훅
│   │   ├── useApplication.ts    # 신청서 훅
│   │   ├── useEvaluation.ts     # 평가 훅
│   │   └── index.ts
│   ├── lib/                      # 유틸리티 및 설정
│   │   ├── api/                 # API 클라이언트
│   │   │   ├── auth.ts
│   │   │   ├── expert.ts
│   │   │   ├── application.ts
│   │   │   ├── evaluation.ts
│   │   │   ├── matching.ts
│   │   │   └── index.ts
│   │   ├── validations/         # Zod 스키마
│   │   │   ├── auth.ts
│   │   │   ├── expert.ts
│   │   │   └── index.ts
│   │   ├── axios.ts             # Axios 설정
│   │   ├── constants.ts         # 상수 정의
│   │   ├── utils.ts             # 유틸리티 함수
│   │   └── index.ts
│   ├── store/                    # Zustand 상태관리
│   │   ├── authStore.ts         # 인증 스토어
│   │   ├── expertStore.ts       # 전문가 스토어
│   │   └── index.ts
│   ├── types/                    # TypeScript 타입 정의
│   │   ├── user.ts              # 사용자 타입
│   │   ├── expert.ts            # 전문가 타입
│   │   ├── application.ts       # 신청서 타입
│   │   ├── evaluation.ts        # 평가 타입
│   │   ├── matching.ts          # 매칭 타입
│   │   ├── common.ts            # 공통 타입
│   │   └── index.ts
│   └── globals.css               # 전역 스타일
├── public/                       # 정적 파일
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 설치 및 실행

### 1. 의존성 설치

```bash
cd frontend
npm install
```

### 2. 환경 변수 설정

```bash
cp .env.example .env.local
# .env.local 파일에 필요한 설정 입력
```

### 3. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 http://localhost:3000 접속

### 4. 프로덕션 빌드

```bash
npm run build
npm start
```

## 주요 기능

### 인증
- 로그인/로그아웃
- 회원가입
- 토큰 관리

### 신청자 (Applicant)
- 신청서 작성
- 자격검증 결과 확인
- 평가응시
- 결과 조회

### 평가위원 (Evaluator)
- 대시보드
- 채점 수행
- 채점 이력

### 관리자 (Admin)
- 전문가 관리
- 문항 관리
- 매칭 관리
- 리포트 생성

## 개발 가이드

### 컴포넌트 사용

```tsx
import { Button, Input, Card, Modal } from '@/components/ui';

export default function MyPage() {
  return (
    <Card>
      <Input label="이메일" type="email" />
      <Button onClick={() => {}}>제출</Button>
    </Card>
  );
}
```

### 상태 관리 (Zustand)

```tsx
import { useAuthStore } from '@/store';

export default function MyComponent() {
  const { user, isAuthenticated, logout } = useAuthStore();

  return (
    <div>
      {isAuthenticated && <p>Welcome, {user?.name}</p>}
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### 데이터 패칭 (React Query)

```tsx
import { useExpert } from '@/hooks';

export default function ExpertProfile() {
  const { getExpertProfile } = useExpert();
  const { data, isLoading, error } = getExpertProfile();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading profile</div>;

  return <div>{data?.name}</div>;
}
```

### 폼 관리 (React Hook Form + Zod)

```tsx
import { useForm } from 'react-hook-form';
import { loginSchema } from '@/lib/validations';

export default function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = (data) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input {...register('email')} error={errors.email?.message} />
      <Button type="submit">Login</Button>
    </form>
  );
}
```

### API 호출

```tsx
import { authApi } from '@/lib/api';

export default function AuthService() {
  const handleLogin = async () => {
    try {
      const data = await authApi.login({
        email: 'user@example.com',
        password: 'password123',
      });
      console.log('Login successful:', data);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };
}
```

## 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| NEXT_PUBLIC_API_URL | Backend API URL | http://localhost:8000/api/v1 |
| NEXT_PUBLIC_APP_NAME | 애플리케이션 이름 | AX 코칭단 평가 시스템 |
| NEXT_PUBLIC_APP_URL | 애플리케이션 URL | http://localhost:3000 |

## 라이선스

Copyright © 2025 AX Development Team
