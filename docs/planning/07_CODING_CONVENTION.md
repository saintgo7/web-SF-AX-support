# Coding Convention: AX 코칭단 평가 시스템

---

## 1. 일반 원칙

### 1.1 기본 원칙
- **가독성 우선**: 코드는 작성보다 읽히는 횟수가 더 많다
- **일관성 유지**: 프로젝트 전반에 걸쳐 동일한 스타일 적용
- **명시적 표현**: 암묵적인 것보다 명시적인 것이 낫다
- **단순함 추구**: 복잡한 것보다 단순한 것이 낫다

### 1.2 언어별 기준
- **Python**: PEP 8 + Black 포매터
- **TypeScript**: ESLint + Prettier
- **SQL**: 대문자 키워드, 소문자 식별자

---

## 2. Python (Backend)

### 2.1 파일 구조
```python
"""모듈 설명 (docstring).

상세한 모듈 설명이 필요한 경우 여기에 작성.
"""
import enum                           # 표준 라이브러리
import uuid
from datetime import datetime

from fastapi import APIRouter         # 서드파티
from sqlalchemy.orm import Mapped

from src.app.db.base import Base      # 로컬 임포트
from src.app.models import User
```

### 2.2 네이밍 규칙
```python
# 클래스: PascalCase
class UserRepository:
    pass

# 함수/메서드: snake_case
def get_user_by_id(user_id: str) -> User:
    pass

# 상수: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_PAGE_SIZE = 20

# 변수: snake_case
current_user = get_current_user()

# Private: 언더스코어 접두사
_internal_cache = {}

# Enum 멤버: UPPER_SNAKE_CASE
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    EVALUATOR = "EVALUATOR"
```

### 2.3 타입 힌트
```python
# 함수 시그니처
async def create_user(
    db: AsyncSession,
    user_data: UserCreate,
) -> User:
    """사용자 생성.

    Args:
        db: 데이터베이스 세션
        user_data: 사용자 생성 데이터

    Returns:
        생성된 사용자 객체

    Raises:
        DuplicateEmailError: 이메일 중복 시
    """
    pass

# SQLAlchemy 2.0 스타일
class Expert(Base):
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    career_years: Mapped[int | None] = mapped_column(Integer, nullable=True)

# 컬렉션 타입
def get_experts(ids: list[str]) -> list[Expert]:
    pass

# Optional 대신 | None 사용 (Python 3.10+)
def find_user(email: str) -> User | None:
    pass
```

### 2.4 Pydantic 모델 (스키마)
```python
from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    """사용자 생성 스키마."""

    email: str = Field(..., description="이메일 주소")
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('유효한 이메일 형식이 아닙니다')
        return v.lower()

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "name": "홍길동",
                "password": "securepass123"
            }
        }
    }
```

### 2.5 API 엔드포인트
```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/users", tags=["users"])

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="사용자 조회",
    description="ID로 사용자 정보를 조회합니다.",
)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """사용자 조회 엔드포인트."""
    user = await user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )
    return user
```

### 2.6 예외 처리
```python
# 커스텀 예외 정의
class AppError(Exception):
    """애플리케이션 기본 예외."""

    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)

class NotFoundError(AppError):
    """리소스를 찾을 수 없음."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource}을(를) 찾을 수 없습니다: {identifier}",
            code="NOT_FOUND"
        )

# 예외 처리 패턴
async def get_expert(expert_id: str) -> Expert:
    expert = await db.get(Expert, expert_id)
    if not expert:
        raise NotFoundError("전문가", expert_id)
    return expert
```

---

## 3. TypeScript (Frontend)

### 3.1 파일 구조
```typescript
/**
 * 컴포넌트/모듈 설명
 *
 * 상세 설명이 필요한 경우 여기에 작성
 */
'use client';                          // Next.js 지시문

import { useState, useEffect } from 'react';  // React
import { useQuery } from '@tanstack/react-query';  // 서드파티
import type { User } from '@/types';   // 내부 타입
import { UserCard } from './UserCard'; // 로컬 컴포넌트
```

### 3.2 네이밍 규칙
```typescript
// 컴포넌트: PascalCase
function UserProfile() {}

// 훅: use 접두사 + camelCase
function useUserData() {}

// 함수: camelCase
function formatDate(date: Date): string {}

// 상수: UPPER_SNAKE_CASE
const MAX_FILE_SIZE = 10 * 1024 * 1024;

// 타입/인터페이스: PascalCase
interface UserData {
  id: string;
  name: string;
}

// Enum: PascalCase (멤버도 PascalCase 또는 UPPER_SNAKE)
enum UserRole {
  Admin = 'ADMIN',
  Evaluator = 'EVALUATOR',
}

// 파일명
// - 컴포넌트: PascalCase.tsx (UserProfile.tsx)
// - 유틸/훅: camelCase.ts (useAuth.ts, formatDate.ts)
// - 타입: camelCase.ts (user.ts, matching.ts)
```

### 3.3 타입 정의
```typescript
// 인터페이스 사용 (확장 가능성 있을 때)
interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  createdAt: string;
}

// 타입 별칭 사용 (유니온, 유틸리티 타입)
type UserRole = 'ADMIN' | 'EVALUATOR' | 'APPLICANT';

type PartialUser = Partial<User>;

// 제네릭 활용
interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
}

// Props 타입
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}
```

### 3.4 React 컴포넌트
```typescript
/**
 * 사용자 프로필 카드 컴포넌트
 *
 * 사용자 정보를 카드 형태로 표시합니다.
 */
interface UserCardProps {
  user: User;
  onEdit?: (userId: string) => void;
  className?: string;
}

export function UserCard({
  user,
  onEdit,
  className = '',
}: UserCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleEdit = useCallback(() => {
    onEdit?.(user.id);
  }, [user.id, onEdit]);

  return (
    <div className={`user-card ${className}`}>
      <h3>{user.name}</h3>
      {/* ... */}
    </div>
  );
}

// 기본 내보내기는 페이지 컴포넌트에만 사용
export default function UserPage() {}
```

### 3.5 React Query 훅
```typescript
/**
 * 사용자 데이터 훅
 */
export function useUser(userId: string) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => usersApi.getUser(userId),
    enabled: !!userId,
  });
}

/**
 * 사용자 생성 뮤테이션
 */
export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UserCreate) => usersApi.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
```

### 3.6 API 클라이언트
```typescript
/**
 * 사용자 API 클라이언트
 */
export const usersApi = {
  /**
   * 사용자 목록 조회
   */
  async getUsers(params?: UserListParams): Promise<PaginatedResponse<User>> {
    const response = await apiClient.get('/users', { params });
    return response.data;
  },

  /**
   * 사용자 상세 조회
   */
  async getUser(userId: string): Promise<User> {
    const response = await apiClient.get(`/users/${userId}`);
    return response.data;
  },

  /**
   * 사용자 생성
   */
  async createUser(data: UserCreate): Promise<User> {
    const response = await apiClient.post('/users', data);
    return response.data;
  },
};
```

---

## 4. SQL 규칙

### 4.1 명명 규칙
```sql
-- 테이블: snake_case, 복수형
CREATE TABLE users (...);
CREATE TABLE question_categories (...);

-- 컬럼: snake_case
user_id, created_at, is_active

-- 인덱스: idx_{테이블}_{컬럼}
CREATE INDEX idx_users_email ON users(email);

-- 외래키: fk_{현재테이블}_{참조테이블}
CONSTRAINT fk_experts_users FOREIGN KEY (user_id) REFERENCES users(id)
```

### 4.2 쿼리 포매팅
```sql
-- 키워드 대문자
SELECT
    u.id,
    u.email,
    e.career_years
FROM users u
INNER JOIN experts e ON e.user_id = u.id
WHERE u.is_active = TRUE
    AND e.qualification_status = 'QUALIFIED'
ORDER BY e.career_years DESC
LIMIT 10;
```

---

## 5. Git 컨벤션

### 5.1 브랜치 네이밍
```
main              # 프로덕션
develop           # 개발 통합
feature/기능명    # 새 기능
fix/버그설명      # 버그 수정
hotfix/긴급수정   # 긴급 수정

예시:
feature/ai-matching
fix/pdf-korean-font
hotfix/login-session
```

### 5.2 커밋 메시지
```
<타입>: <제목>

<본문 (선택)>

<푸터 (선택)>

타입:
- feat: 새 기능
- fix: 버그 수정
- docs: 문서 수정
- style: 포매팅
- refactor: 리팩토링
- test: 테스트
- chore: 빌드/설정

예시:
feat: AI 매칭 추천 알고리즘 구현

- sentence-transformers 기반 의미 유사도 계산
- 5가지 가중치 기반 점수 산출
- RecommendedCandidate 스키마 추가

Closes #123
```

### 5.3 PR 규칙
```markdown
## 변경 사항
- 변경 내용 요약

## 테스트
- [ ] 단위 테스트 통과
- [ ] 수동 테스트 완료

## 체크리스트
- [ ] 코드 리뷰 요청
- [ ] 문서 업데이트
```

---

## 6. 주석 규칙

### 6.1 코드 주석
```python
# 한 줄 주석: 코드 위에 작성
# 복잡한 로직 설명이 필요한 경우에만 사용
score = specialty * 0.4 + evaluation * 0.2  # 가중치 기반 점수

# TODO: 향후 개선 필요
# FIXME: 버그 수정 필요
# NOTE: 참고 사항
# HACK: 임시 해결책
```

### 6.2 문서화 주석
```python
def calculate_match_score(
    expert: Expert,
    demand: Demand,
) -> float:
    """전문가-수요 매칭 점수를 계산합니다.

    가중치 기반 점수 계산:
    - 전문분야 일치: 40%
    - 평가 성과: 20%
    - 자격 검증: 15%
    - 경력: 15%
    - 가용성: 10%

    Args:
        expert: 전문가 정보
        demand: 기업 수요 정보

    Returns:
        0-100 사이의 매칭 점수

    Raises:
        ValueError: 필수 데이터 누락 시

    Example:
        >>> score = calculate_match_score(expert, demand)
        >>> print(f"매칭 점수: {score}")
    """
    pass
```

---

## 7. 디렉토리 구조

### 7.1 Backend
```
backend/
├── src/
│   └── app/
│       ├── api/
│       │   └── v1/           # API 버전별 라우터
│       ├── core/             # 설정, 보안
│       ├── db/               # DB 연결, 마이그레이션
│       ├── models/           # SQLAlchemy 모델
│       ├── schemas/          # Pydantic 스키마
│       ├── services/         # 비즈니스 로직
│       ├── ml/               # ML 모듈
│       └── utils/            # 유틸리티
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── pyproject.toml
└── README.md
```

### 7.2 Frontend
```
frontend/
├── src/
│   ├── app/                  # Next.js App Router
│   │   ├── (auth)/           # 라우트 그룹
│   │   ├── admin/
│   │   ├── evaluator/
│   │   └── applicant/
│   ├── components/           # 재사용 컴포넌트
│   │   ├── ui/               # 기본 UI 컴포넌트
│   │   ├── forms/            # 폼 컴포넌트
│   │   └── layouts/          # 레이아웃 컴포넌트
│   ├── hooks/                # 커스텀 훅
│   ├── lib/                  # 라이브러리
│   │   ├── api/              # API 클라이언트
│   │   └── utils/            # 유틸리티
│   ├── types/                # TypeScript 타입
│   └── styles/               # 전역 스타일
├── public/                   # 정적 파일
├── next.config.js
└── package.json
```

---

## 8. 도구 설정

### 8.1 Python (pyproject.toml)
```toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.11"
strict = true
```

### 8.2 TypeScript (eslint.config.js)
```javascript
export default [
  {
    rules: {
      '@typescript-eslint/no-unused-vars': 'error',
      '@typescript-eslint/explicit-function-return-type': 'warn',
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
    },
  },
];
```

### 8.3 Prettier (.prettierrc)
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

---

## 부록: 체크리스트

### 코드 리뷰 체크리스트
- [ ] 네이밍 규칙 준수
- [ ] 타입 힌트/타입 정의 완료
- [ ] 에러 처리 적절
- [ ] 불필요한 코드 없음
- [ ] 테스트 작성됨
- [ ] 문서화됨
