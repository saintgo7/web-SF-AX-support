# AX 코칭단 평가 시스템 - 개발자 빠른 시작 가이드

## 사전 요구사항

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Poetry (Python 패키지 관리)

## 1. 프로젝트 클론

```bash
git clone <repository-url>
cd ax-coaching-eval-system
```

## 2. Docker Compose로 시작 (권장)

가장 빠른 시작 방법입니다.

```bash
cd docker
docker-compose up -d
```

서비스 접속:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs

## 3. 개발 모드 실행

### Backend

```bash
cd backend

# Poetry 설치 (처음 한 번)
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치
poetry install

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집하여 DATABASE_URL, SECRET_KEY 등 설정

# 데이터베이스 마이그레이션
poetry run alembic upgrade head

# 개발 서버 실행
poetry run uvicorn src.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# 개발 서버 실행
npm run dev
```

## 4. 테스트 실행

```bash
cd backend

# 전체 테스트
poetry run pytest

# 커버리지 포함
poetry run pytest --cov=src/app --cov-report=html
```

## 5. 주요 명령어

### 마이그레이션

```bash
# 새 마이그레이션 생성
poetry run alembic revision --autogenerate -m "Add new table"

# 마이그레이션 적용
poetry run alembic upgrade head

# 롤백
poetry run alembic downgrade -1
```

### 린트 & 타입 체크

```bash
# Frontend
npm run lint
npm run type-check
```

## 6. 프로젝트 구조 요약

```
├── backend/           # FastAPI Backend
│   ├── src/app/
│   │   ├── api/v1/    # API 엔드포인트
│   │   ├── models/    # SQLAlchemy 모델
│   │   ├── schemas/   # Pydantic 스키마
│   │   └── services/  # 비즈니스 로직
│   └── tests/         # 테스트
│
├── frontend/          # Next.js Frontend
│   ├── src/app/       # 페이지 (App Router)
│   ├── src/components/# UI 컴포넌트
│   ├── src/hooks/     # 커스텀 훅
│   ├── src/lib/       # 유틸리티 & API
│   └── src/store/     # Zustand 상태
│
└── docker/            # Docker 설정
```

## 7. 사용자 역할

| 역할 | 설명 | 경로 접두사 |
|------|------|-------------|
| ADMIN | 시스템 관리자 | /admin/* |
| EVALUATOR | 평가위원 | /evaluator/* |
| APPLICANT | 전문가 신청자 | /applicant/* |

## 8. API 엔드포인트 요약

| 경로 | 설명 |
|------|------|
| /api/v1/auth/* | 인증 (로그인, 회원가입) |
| /api/v1/experts/* | 전문가 관리 |
| /api/v1/questions/* | 평가 문항 |
| /api/v1/evaluation/* | 평가 및 채점 |
| /api/v1/applications/* | 신청 관리 |
| /api/v1/companies/* | 기업 관리 |
| /api/v1/matchings/* | 매칭 관리 |

## 9. 상세 문서

- [개발 진행 현황](./DEVELOPMENT_PROGRESS.md) - 전체 개발 문서
- [개발 계획서](./plan/plan.md) - 프로젝트 계획
- [Sprint 3 완료 보고](../SPRINT3_README.md) - Q&A 시스템 구현

---

**AX Development Team**
