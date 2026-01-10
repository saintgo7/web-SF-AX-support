# Sprint 3: AX 기능별 질의응답 시스템

## 구현 완료 개요

Sprint 3의 AX 기능별 질의응답 시스템 개발이 완료되었습니다.

- **구현 기간:** 2025-01-10
- **상태:** ✅ 완료
- **총 파일:** 13개 (모델 2, 스키마 2, 서비스 2, API 2, 테스트 4, 문서 2)

## 주요 기능

### 1. 분야별 평가 문항 DB 모델
- ✅ Question 모델 (객관식, 주관식, 파일첨부)
- ✅ QuestionCategory 모델 (평가 영역)
- ✅ 문항 CRUD API

### 2. 응답 수집 시스템
- ✅ Answer 모델 (버전 관리 지원)
- ✅ 응답 제출 API
- ✅ 일괄 제출 지원

### 3. 객관식 자동 채점
- ✅ 단일 선택 정답 매칭
- ✅ 다중 선택 부분 점수
- ✅ 자동 채점 API

## 파일 구조

```
backend/
├── src/app/
│   ├── models/
│   │   ├── question.py          # Question, QuestionCategory
│   │   └── answer.py            # Answer with versioning
│   ├── schemas/
│   │   ├── question.py          # Question schemas
│   │   └── answer.py            # Answer schemas
│   ├── services/
│   │   ├── question_service.py  # Question business logic
│   │   └── grading_service.py   # Auto-grading logic
│   └── api/v1/
│       ├── questions.py         # Questions API
│       ├── evaluation.py        # Evaluation API
│       └── api.py              # Router registry
├── tests/
│   ├── test_question_service.py # 15 unit tests
│   ├── test_grading_service.py  # 12 unit tests
│   ├── test_questions_api.py    # 13 integration tests
│   ├── test_evaluation_api.py   # 14 integration tests
│   └── conftest.py             # Test fixtures
├── MIGRATION_GUIDE.md          # Database migration guide
└── SPRINT3_IMPLEMENTATION_SUMMARY.md  # Detailed summary
```

## API 엔드포인트

### Questions API
- `POST /api/v1/questions/categories` - 카테고리 생성
- `GET /api/v1/questions/categories` - 카테고리 목록
- `POST /api/v1/questions` - 문항 생성
- `GET /api/v1/questions` - 문항 목록 (필터링 지원)
- `GET /api/v1/questions/by-specialties/{specialties}` - 전문분야별 문항

### Evaluation API
- `POST /api/v1/evaluation/answers` - 응답 생성
- `POST /api/v1/evaluation/submit` - 일괄 제출
- `POST /api/v1/evaluation/grade/auto` - 자동 채점
- `POST /api/v1/evaluation/grade/{id}/manual` - 수동 채점
- `POST /api/v1/evaluation/grade/batch/{expert_id}` - 일괄 채점

## 빠른 시작

### 1. 마이그레이션 실행

```bash
cd backend

# 마이그레이션 생성
alembic revision --autogenerate -m "Add questions and answers tables"

# 마이그레이션 적용
alembic upgrade head
```

자세한 내용은 [MIGRATION_GUIDE.md](/Users/saint/01_DEV/26-ai-program/backend/MIGRATION_GUIDE.md)를 참조하세요.

### 2. 테스트 실행

```bash
cd backend

# 전체 테스트
pytest

# 특정 테스트 파일
pytest tests/test_question_service.py
pytest tests/test_questions_api.py

# 커버리지 확인
pytest --cov=src/app --cov-report=html
```

### 3. 서버 실행

```bash
cd backend

# 개발 서버
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 주요 기술 특징

- **SQLAlchemy 2.0 Async:** 비동기 데이터베이스 처리
- **Pydantic v2:** 타입 안정성과 자동 검증
- **FastAPI:** 빠르고 현대적인 API 프레임워크
- **JSONB:** 유연한 데이터 구조 (PostgreSQL)
- **Service Layer:** 비즈니스 로직 분리
- **Soft Delete:** 데이터 영구 보존
- **Versioning:** 응답 수정 이력 추적

## 데이터 모델

### Question
- 객관식 (단일/다중 선택)
- 주관식 (단답/서술)
- 파일첨부
- 난이도 (EASY/MEDIUM/HARD)
- 전문분야별 타겟팅

### Answer
- 버전 관리 (수정 이력)
- 자동/수동 채점 지원
- 채점자 코멘트
- 상태 관리 (DRAFT/SUBMITTED/GRADED)

## 테스트 커버리지

- 단위 테스트: 27개
- 통합 테스트: 27개
- 총 54개 테스트 케이스

## 문서

- [상세 구현 보고서](/Users/saint/01_DEV/26-ai-program/backend/SPRINT3_IMPLEMENTATION_SUMMARY.md)
- [마이그레이션 가이드](/Users/saint/01_DEV/26-ai-program/backend/MIGRATION_GUIDE.md)

## 다음 단계 (Sprint 4)

- 평가 점수 산정 및 리포트
- 수요기업 매칭 지원
- 추천 알고리즘

---

**구현자:** Claude Code (Anthropic)
**프로젝트:** 스마트공장 AX 코칭단 평가 시스템
**Sprint:** 3 - AX Q&A System
