# AX 코칭단 평가 시스템

스마트공장 AX 코칭단 전문가 평가 및 매칭 시스템입니다. AX 코칭단 전문가 100명 내외를 선정하고, 200개 내외의 수요기업과 효과적으로 매칭하기 위한 평가 및 관리 플랫폼입니다.

## 프로젝트 개요

- **프로젝트명:** 스마트공장 AX 코칭단 전문가 평가 및 매칭 시스템
- **버전:** 0.1.0
- **개발기관:** AX Development Team

## 주요 기능

### [A] 전문가 자격요건 자동 검증
- 학위/경력 조건 충족 여부 판정
- 해당분야(ML, DL, CV, 데이터인텔리전스) 매칭
- 자동 판정 결과 생성 (적합/부적합/검토필요)

### [B] AX 기능별 질의응답 시스템
- 분야별 평가 문항 DB 설계/구축
- 응답 수집 및 자동 채점
- 평가위원 채점 인터페이스

### [C] 평가 점수 산정 및 리포트
- 가중치 기반 종합 점수 산출
- 평가 결과 보고서 자동 생성
- PDF 출력

### [D] 수요기업 매칭 지원
- 전문가-기업 적합도 분석
- 최적 매칭 추천 알고리즘

## 기술 스택

### Backend
- **Python 3.11+**
- **FastAPI** - 웹 프레임워크
- **PostgreSQL** - 메인 데이터베이스
- **Redis** - 캐시 및 세션 저장소
- **Alembic** - 데이터베이스 마이그레이션
- **SQLAlchemy** - ORM
- **scikit-learn & sentence-transformers** - ML 모델

### Frontend
- **Next.js 14** - React Framework
- **TypeScript** - 타입 안정성
- **Tailwind CSS** - 스타일링
- **Zustand** - 상태 관리
- **React Query** - 데이터 패칭
- **React Hook Form** - 폼 관리

### Infrastructure
- **Docker & Docker Compose** - 컨테이너화
- **GitHub Actions** - CI/CD

## 프로젝트 구조

```
ax-coaching-eval-system/
├── backend/           # FastAPI Backend
│   ├── src/
│   │   ├── app/
│   │   │   ├── api/   # API Endpoints
│   │   │   ├── core/  # Security, Config
│   │   │   ├── db/    # Database
│   │   │   ├── models/# SQLAlchemy Models
│   │   │   ├── schemas/# Pydantic Schemas
│   │   │   └── services/# Business Logic
│   │   ├── alembic/  # Migrations
│   │   └── main.py   # Application Entry
│   └── pyproject.toml
├── frontend/          # Next.js Frontend
│   ├── src/
│   │   ├── app/      # Next.js App Router
│   │   ├── components/# React Components
│   │   ├── hooks/    # Custom Hooks
│   │   ├── lib/      # Utilities
│   │   └── types/    # TypeScript Types
│   └── package.json
├── docker/            # Docker Configuration
│   └── docker-compose.yml
├── docs/              # Documentation
│   └── plan/
│       └── plan.md    # 개발 계획서
└── README.md
```

## 빠른 시작

### 1. Docker Compose로 시작 (권장)

```bash
# Docker Compose로 모든 서비스 시작
cd docker
docker-compose up -d

# 서비스 중지
docker-compose down

# 로그 확인
docker-compose logs -f
```

서비스가 시작되면:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 2. 개발 모드로 실행

#### Backend
```bash
cd backend

# Poetry 설치 (처음 한 번)
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치
poetry install

# 환경 변수 설정
cp .env.example .env

# 데이터베이스 마이그레이션
poetry run alembic upgrade head

# 서버 실행
poetry run uvicorn src.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env.local

# 개발 서버 실행
npm run dev
```

## 환경 설정

### Backend (.env)
```bash
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ax_eval
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=true
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 데이터베이스 마이그레이션

```bash
cd backend

# 새 마이그레이션 생성
poetry run alembic revision --autogenerate -m "migration message"

# 마이그레이션 적용
poetry run alembic upgrade head

# 마이그레이션 롤백
poetry run alembic downgrade -1
```

## 테스트

### Backend
```bash
cd backend

# 전체 테스트
poetry run pytest

# 커버리지 포함
poetry run pytest --cov=src --cov-report=html
```

### Frontend
```bash
cd frontend

# 타입 체크
npm run type-check

# 린트
npm run lint
```

## 개발 일정

| 단계 | 기간 | 상태 |
|------|------|------|
| Sprint 1: 기반 구축 | W5-W6 | ✅ 완료 |
| Sprint 2: 자격검증 | W7-W8 | 🚧 진행 중 |
| Sprint 3: 평가시스템 | W9-W10 | ⏳ 대기 |
| Sprint 4: 채점시스템 | W11-W12 | ⏳ 대기 |
| Sprint 5: 리포트 | W13-W14 | ⏳ 대기 |
| Sprint 6: 매칭시스템 | W15-W16 | ⏳ 대기 |

## 문서

- [개발 계획서](docs/plan/plan.md) - 상세 프로젝트 계획
- [Backend README](backend/README.md) - 백엔드 개발 가이드
- [Frontend README](frontend/README.md) - 프론트엔드 개발 가이드

## 기여

이 프로젝트에 기여하고 싶으시다면:

1. 이슈를 생성하여 개선사항 제안
2. Fork 후 브랜치 생성
3. 변경사항 커밋
4. Pull Request 전송

## 라이선스

Copyright © 2025 AX Development Team. All rights reserved.

## 연락처

- 프로젝트 관리자: ops@example.kr
- 기술 지원: support@vendor.kr
