# AX 코칭단 평가 시스템 Backend

스마트공장 AX 코칭단 전문가 평가 및 매칭 시스템의 Backend API 서비스입니다.

## 기술 스택

- **Python 3.11+**
- **FastAPI** - 웹 프레임워크
- **PostgreSQL** - 메인 데이터베이스
- **Redis** - 캐시 및 세션 저장소
- **Alembic** - 데이터베이스 마이그레이션
- **SQLAlchemy** - ORM
- **Celery** - 비동기 태스크 큐
- **scikit-learn & sentence-transformers** - ML 모델

## 프로젝트 구조

```
backend/
├── src/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── config.py            # 설정 관리
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py      # 의존성 주입
│   │   │   └── v1/
│   │   │       ├── api.py   # API 라우터
│   │   │       ├── auth.py  # 인증 API
│   │   │       ├── experts.py # 전문가 관리 API
│   │   │       ├── evaluation.py # 평가 API
│   │   │       └── matching.py # 매칭 API
│   │   ├── core/
│   │   │   ├── security.py  # JWT, 비밀번호 해시
│   │   │   └── config.py    # 설정
│   │   ├── db/
│   │   │   ├── base.py      # Base 모델
│   │   │   ├── session.py   # DB 세션
│   │   │   └── init_db.py   # 초기 데이터
│   │   ├── models/          # SQLAlchemy 모델
│   │   ├── schemas/         # Pydantic 스키마
│   │   ├── services/        # 비즈니스 로직
│   │   └── tasks/           # Celery 태스크
│   └── alembic/             # 마이그레이션
├── tests/                   # 테스트
├── pyproject.toml
└── README.md
```

## 설치 및 실행

### 1. Poetry 설치

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. 의존성 설치

```bash
cd backend
poetry install
```

### 3. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일에 필요한 설정 입력
```

### 4. 데이터베이스 마이그레이션

```bash
poetry run alembic upgrade head
```

### 5. 서버 실행

```bash
# 개발 모드
poetry run uvicorn src.main:app --reload --port 8000

# 프로덕션 모드
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 테스트

```bash
# 전체 테스트
poetry run pytest

# 커버리지 포함
poetry run pytest --cov=src --cov-report=html

# 특정 테스트
poetry run pytest tests/test_auth.py
```

## 개발 가이드

### 새로운 API 엔드포인트 추가

1. `app/schemas/`에 Pydantic 스키마 정의
2. `app/models/`에 SQLAlchemy 모델 정의 (필요한 경우)
3. `app/services/`에 비즈니스 로직 구현
4. `app/api/v1/`에 API 라우터 생성
5. `app/api/v1/api.py`에 라우터 등록

### 데이터베이스 마이그레이션 생성

```bash
poetry run alembic revision --autogenerate -m "migration message"
poetry run alembic upgrade head
```

## 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| DATABASE_URL | PostgreSQL 연결 URL | |
| REDIS_URL | Redis 연결 URL | |
| SECRET_KEY | JWT 시크릿 키 | |
| ACCESS_TOKEN_EXPIRE_MINUTES | 액세스 토큰 만료 시간(분) | 30 |
| AWS_ACCESS_KEY_ID | AWS 액세스 키 | |
| AWS_SECRET_ACCESS_KEY | AWS 시크릿 키 | |
| AWS_S3_BUCKET | S3 버킷명 | |
| ENVIRONMENT | 실행 환경 (dev/stage/prod) | dev |

## 라이선스

Copyright © 2025 AX Development Team
