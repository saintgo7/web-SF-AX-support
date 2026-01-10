# Sprint 3: AX 기능별 질의응답 시스템 구현 완료 보고서

## 개요

Sprint 3의 AX 기능별 질의응답 시스템 개발이 완료되었습니다. 본 시스템은 전문가 평가를 위한 문항 관리, 응답 수집, 및 자동 채점 기능을 제공합니다.

**구현 일자:** 2025-01-10
**Sprint:** 3 - AX Q&A System
**상태:** ✅ 완료

---

## 구현 내용 상세

### 1. 데이터베이스 모델 (Database Models)

#### 1.1 Question Models (`/Users/saint/01_DEV/26-ai-program/backend/src/app/models/question.py`)

**QuestionCategory 모델**
- 평가 영역을 분류하는 카테고리 모델
- 주요 필드:
  - `name`: 카테고리명 (unique)
  - `description`: 설명
  - `weight`: 가중치 (0-100)
  - `display_order`: 표시 순서
  - `is_active`: 활성화 여부

**Question 모델**
- 평가 문항 모델
- 주요 필드:
  - `category_id`: 카테고리 참조 (FK)
  - `q_type`: 문항 유형 (SINGLE, MULTIPLE, SHORT, ESSAY, FILE)
  - `content`: 문항 내용
  - `options`: 객관식 선택지 (JSONB)
  - `correct_answer`: 정답 (JSONB)
  - `scoring_rubric`: 채점 기준표 (JSONB)
  - `max_score`: 배점
  - `difficulty`: 난이도 (EASY, MEDIUM, HARD)
  - `target_specialties`: 대상 전문분야 (JSONB)
  - `explanation`: 해설
  - `is_active`: 활성화 여부

**Enums**
- `QuestionType`: SINGLE, MULTIPLE, SHORT, ESSAY, FILE
- `Difficulty`: EASY, MEDIUM, HARD
- `Specialty`: ML, DL, CV, DATA_INTELLIGENCE, COMPUTING_PLATFORM, GENERAL

#### 1.2 Answer Model (`/Users/saint/01_DEV/26-ai-program/backend/src/app/models/answer.py`)

**Answer 모델**
- 지원자 응답 저장 모델 (버전 관리 지원)
- 주요 필드:
  - `expert_id`: 전문가 참조 (FK, CASCADE)
  - `question_id`: 문항 참조 (FK, CASCADE)
  - `version`: 응답 버전 (수정 이력 추적)
  - `response_data`: 응답 내용 (JSONB)
  - `score`: 점수
  - `max_score`: 최대 점수
  - `is_correct`: 정답 여부 (객관식용)
  - `grader_id`: 채점자 참조 (FK, SET NULL)
  - `grader_comment`: 채점자 코멘트
  - `status`: 상태 (DRAFT, SUBMITTED, GRADED, REVIEWED)

---

### 2. Pydantic 스키마 (Schemas)

#### 2.1 Question Schemas (`/Users/saint/01_DEV/26-ai-program/backend/src/app/schemas/question.py`)

**Category Schemas**
- `QuestionCategoryBase`: 기본 카테고리 스키마
- `QuestionCategoryCreate`: 생성용
- `QuestionCategoryUpdate`: 수정용
- `QuestionCategory`: 응답용

**Question Schemas**
- `QuestionBase`: 기본 문항 스키마
- `QuestionCreate`: 생성용
- `QuestionUpdate`: 수정용
- `Question`: 응답용
- `QuestionQuery`: 필터링 쿼리용
- `QuestionListResponse`: 페이지네이션 응답용

#### 2.2 Answer Schemas (`/Users/saint/01_DEV/26-ai-program/backend/src/app/schemas/answer.py`)

**Answer Schemas**
- `AnswerBase`: 기본 응답 스키마
- `AnswerCreate`: 생성용
- `AnswerUpdate`: 수정용
- `Answer`: 응답용

**Grading Schemas**
- `AutoGradeRequest`: 자동 채점 요청
- `AutoGradeResponse`: 자동 채점 응답
- `ManualGradeRequest`: 수동 채점 요청
- `ManualGradeResponse`: 수동 채점 응답

**Batch Schemas**
- `AnswerSubmitRequest`: 일괄 제출 요청
- `AnswerSubmitResponse`: 일괄 제출 응답
- `ExpertAnswersResponse`: 전문가 응답 요약

---

### 3. 서비스 레이어 (Service Layer)

#### 3.1 Question Service (`/Users/saint/01_DEV/26-ai-program/backend/src/app/services/question_service.py`)

**제공 기능**
- `create_category()`: 카테고리 생성
- `get_category()`: 카테고리 조회
- `list_categories()`: 카테고리 목록 (페이지네이션)
- `update_category()`: 카테고리 수정
- `delete_category()`: 카테고리 삭제 (soft delete)
- `create_question()`: 문항 생성
- `get_question()`: 문항 조회
- `list_questions()`: 문항 목록 (필터링, 페이지네이션)
- `update_question()`: 문항 수정
- `delete_question()`: 문항 삭제 (soft delete)
- `get_questions_by_specialties()`: 전문분야별 문항 조회

**특징**
- 비즈니스 로직 분리
- JSONB 필드 쿼리 지원 (전문분야 필터링)
- Soft delete 패턴 적용
- 페이지네이션 지원

#### 3.2 Grading Service (`/Users/saint/01_DEV/26-ai-program/backend/src/app/services/grading_service.py`)

**제공 기능**
- `auto_grade_answer()`: 객관식 자동 채점
  - 단일 선택: 정확히 일치해야 정답
  - 다중 선택: 모든 정답 선택, 오답 없어야 만점
  - 부분 정답: 일부만 맞으면 부분 점수 부여
- `manual_grade_answer()`: 주관식 수동 채점
- `submit_answer()`: 응답 제출/수정 (버전 관리)
- `get_expert_answers_summary()`: 전문가별 응답 요약

**특징**
- 객관식 즉시 채점
- 주관식 수동 채점 지원
- 응답 버전 관리 (수정 이력 추적)
- 종합 점수 계산

---

### 4. API 엔드포인트 (API Endpoints)

#### 4.1 Questions API (`/Users/saint/01_DEV/26-ai-program/backend/src/app/api/v1/questions.py`)

**Base URL:** `/api/v1/questions`

**Category Endpoints**
- `POST /categories` - 카테고리 생성 (Operator only)
- `GET /categories` - 카테고리 목록
- `GET /categories/{category_id}` - 카테고리 조회
- `PUT /categories/{category_id}` - 카테고리 수정 (Operator only)
- `DELETE /categories/{category_id}` - 카테고리 삭제 (Operator only)

**Question Endpoints**
- `POST ""` - 문항 생성 (Operator only)
- `GET ""` - 문항 목록 (필터링, 페이지네이션)
  - Query params: `skip`, `limit`, `category_id`, `q_type`, `specialty`, `active_only`
- `GET /{question_id}` - 문항 조회
- `PUT /{question_id}` - 문항 수정 (Operator only)
- `DELETE /{question_id}` - 문항 삭제 (Operator only)
- `GET /by-specialties/{specialties}` - 전문분야별 문항 조회

#### 4.2 Evaluation API (`/Users/saint/01_DEV/26-ai-program/backend/src/app/api/v1/evaluation.py`)

**Base URL:** `/api/v1/evaluation`

**Answer Endpoints**
- `POST /answers` - 응답 생성/수정 (Draft mode)
- `POST /submit` - 일괄 제출
- `GET /answers/{answer_id}` - 응답 조회
- `PUT /answers/{answer_id}` - 응답 수정 (Draft만 가능)
- `GET /experts/{expert_id}/answers` - 전문가별 응답 목록

**Grading Endpoints**
- `POST /grade/auto` - 자동 채점 (Operator only)
- `POST /grade/{answer_id}/manual` - 수동 채점 (Operator only)
- `POST /grade/batch/{expert_id}` - 일괄 자동 채점 (Operator only)

---

### 5. 테스트 코드 (Tests)

#### 5.1 Unit Tests (`/Users/saint/01_DEV/26-ai-program/backend/tests/test_question_service.py`)

**Question Service Tests (15개)**
- 카테고리 CRUD 테스트
- 문항 CRUD 테스트
- 필터링 테스트
- 전문분야별 조회 테스트
- Soft delete 테스트

#### 5.2 Grading Service Tests (`/Users/saint/01_DEV/26-ai-program/backend/tests/test_grading_service.py`)

**Grading Service Tests (12개)**
- 단일 선택 정답/오답 자동 채점
- 다중 선택 정답/부분 정답 자동 채점
- 주관식 자동 채점 실패 테스트
- 수동 채점 테스트
- 점수 초과 검증 테스트
- 응답 제출/수정 테스트
- 응답 요약 조회 테스트

#### 5.3 API Integration Tests (`/Users/saint/01_DEV/26-ai-program/backend/tests/test_questions_api.py`)

**Questions API Tests (13개)**
- 카테고리 CRUD API 테스트
- 문항 CRUD API 테스트
- 필터링 API 테스트
- 전문분야별 조회 API 테스트
- 권한 검증 테스트

#### 5.4 Evaluation API Tests (`/Users/saint/01_DEV/26-ai-program/backend/tests/test_evaluation_api.py`)

**Evaluation API Tests (14개)**
- 응답 CRUD API 테스트
- 일괄 제출 API 테스트
- 자동 채점 API 테스트
- 수동 채점 API 테스트
- 일괄 채점 API 테스트
- 권한 검증 테스트

---

### 6. 라우터 등록

**파일:** `/Users/saint/01_DEV/26-ai-program/backend/src/app/api/v1/api.py`

```python
from src.app.api.v1 import auth, experts, questions, evaluation

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(experts.router)
api_router.include_router(questions.router)
api_router.include_router(evaluation.router)
```

---

## 데이터베이스 마이그레이션 방법

### Step 1: 마이그레이션 생성

```bash
cd /Users/saint/01_DEV/26-ai-program/backend
alembic revision --autogenerate -m "Add questions and answers tables for evaluation system"
```

### Step 2: 마이그레이션 검토

생성된 마이그레이션 파일이 다음을 포함하는지 확인:
- `question_categories` 테이블 생성
- `questions` 테이블 생성
- `answers` 테이블 생성
- Enum 타입 생성 (questiontype, difficulty, answerstatus)
- 인덱스 생성 (category_id, expert_id, question_id, status, target_specialties)
- 외래 키 제약조건

### Step 3: 마이그레이션 적용

```bash
# 개발 환경
alembic upgrade head

# 확인
alembic current
```

### Step 4: 검증

```sql
-- 테이블 확인
SELECT table_name FROM information_schema.tables
WHERE table_name IN ('question_categories', 'questions', 'answers');

-- 열 확인
\d question_categories
\d questions
\d answers
```

**상세 가이드:** `/Users/saint/01_DEV/26-ai-program/backend/MIGRATION_GUIDE.md` 참조

---

## 파일 구조

```
backend/
├── src/app/
│   ├── models/
│   │   ├── question.py          # Question, QuestionCategory 모델
│   │   └── answer.py            # Answer 모델
│   ├── schemas/
│   │   ├── question.py          # Question 관련 스키마
│   │   └── answer.py            # Answer 관련 스키마
│   ├── services/
│   │   ├── question_service.py  # Question 비즈니스 로직
│   │   └── grading_service.py   # Grading 비즈니스 로직
│   └── api/v1/
│       ├── questions.py         # Questions API
│       ├── evaluation.py        # Evaluation API
│       └── api.py              # 라우터 등록 (수정됨)
├── tests/
│   ├── test_question_service.py # Question service 테스트
│   ├── test_grading_service.py  # Grading service 테스트
│   ├── test_questions_api.py    # Questions API 테스트
│   ├── test_evaluation_api.py   # Evaluation API 테스트
│   └── conftest.py             # 테스트 fixtures (수정됨)
├── MIGRATION_GUIDE.md          # 마이그레이션 가이드
└── SPRINT3_IMPLEMENTATION_SUMMARY.md  # 본 문서
```

---

## 기술적 특징

### 1. SQLAlchemy 2.0 Async 패턴
- AsyncSession 사용
- `select()`, `where()`, `join()` 등 2.0 스타일 쿼리
- 비동기 처리로 높은 성능

### 2. Pydantic v2 스키마
- `model_dump()`, `from_attributes` 등 v2 기능 사용
- 타입 안정성 확보
- 자동 데이터 검증

### 3. FastAPI 의존성 주입
- `get_db()`, `get_current_user()`, `get_current_operator()` 등
- 모듈화된 인증/권한 검사

### 4. Service Layer 분리
- 비즈니스 로직을 API 레이어에서 분리
- 재사용 가능한 서비스 함수
- 테스트 용이성 향상

### 5. JSONB 활용
- 유연한 데이터 구조 (options, correct_answer, response_data)
- GIN 인덱스로 JSONB 쿼리 최적화
- PostgreSQL 기능 활용

### 6. Soft Delete 패턴
- 데이터 영구 보존
- `is_active` 필드로 논리적 삭제
- 감사 추적 용이

### 7. 버전 관리
- 응답 수정 이력 추적
- `version` 필드로 변경 사항 관리

---

## 사용 예시

### 1. 카테고리 생성

```python
POST /api/v1/questions/categories
{
  "name": "Machine Learning",
  "description": "ML 관련 문제",
  "weight": 20,
  "display_order": 1
}
```

### 2. 객관식 문항 생성

```python
POST /api/v1/questions
{
  "category_id": "uuid",
  "q_type": "SINGLE",
  "content": "머신러닝의 목적은?",
  "options": {
    "A": "데이터 저장",
    "B": "패턴 학습 및 예측",
    "C": "네트워크 구축",
    "D": "시스템 운영"
  },
  "correct_answer": {"value": "B"},
  "max_score": 10,
  "difficulty": "EASY",
  "target_specialties": ["ML"],
  "explanation": "머신러닝은 데이터에서 패턴을 학습합니다."
}
```

### 3. 응답 제출

```python
POST /api/v1/evaluation/answers
{
  "expert_id": "expert_uuid",
  "question_id": "question_uuid",
  "response_data": {"value": "B"}
}
```

### 4. 자동 채점

```python
POST /api/v1/evaluation/grade/auto
{
  "answer_id": "answer_uuid"
}

# Response:
{
  "answer_id": "uuid",
  "score": 10.0,
  "max_score": 10,
  "is_correct": true,
  "feedback": "정답입니다."
}
```

### 5. 주관식 수동 채점

```python
POST /api/v1/evaluation/grade/{answer_id}/manual
{
  "score": 15.0,
  "grader_comment": "잘 설명함"
}
```

---

## 다음 단계 (Sprint 4)

Sprint 4에서 구현할 기능들:
1. **평가 점수 산정 및 리포트**
   - 가중치 기반 종합 점수 산출
   - 개인별 평가 리포트 생성
   - 통계 리포트

2. **수요기업 매칭 지원**
   - 기업 프로파일 관리
   - 전문가-기업 적합도 분석
   - 추천 알고리즘

---

## 검증 체크리스트

- [x] Question/QuestionCategory 모델 생성
- [x] Answer 모델 생성 (버전 관리 포함)
- [x] Pydantic 스키마 생성
- [x] Service 레이어 구현
- [x] Questions API 구현
- [x] Evaluation API 구현
- [x] 라우터 등록
- [x] 단위 테스트 작성 (27개)
- [x] 통합 테스트 작성 (27개)
- [x] 마이그레이션 가이드 작성
- [ ] 마이그레이션 실행 (DB 관리자 필요)
- [ ] 통합 테스트 실행
- [ ] 코드 리뷰
- [ ] 문서 최종화

---

## 참고 문서

- 기존 모델: `/Users/saint/01_DEV/26-ai-program/backend/src/app/models/expert.py`
- 요구사항: `/Users/saint/01_DEV/26-ai-program/docs/plan/plan.md` (FR-B01~FR-B07)
- API 패턴: `/Users/saint/01_DEV/26-ai-program/backend/src/app/api/v1/experts.py`
- 마이그레이션 가이드: `/Users/saint/01_DEV/26-ai-program/backend/MIGRATION_GUIDE.md`

---

**구현 완료일:** 2025-01-10
**총 파일 수:** 11개
**총 라인 수:** 약 3,500 라인
**테스트 커버리지:** 단위 테스트 27개, 통합 테스트 27개

---

이 문서는 Sprint 3의 모든 구현 내용을 포함하고 있습니다. 추가 질문이나 수정 사항이 있으시면 알려주십시오.
