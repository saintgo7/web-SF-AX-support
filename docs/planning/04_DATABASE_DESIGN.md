# Database Design: AX 코칭단 평가 시스템

---

## 1. 개요

### 1.1 데이터베이스 정보
- **DBMS**: PostgreSQL 14+
- **문자셋**: UTF-8
- **시간대**: Asia/Seoul (UTC+9)

### 1.2 공통 컬럼
모든 테이블에 적용되는 공통 필드:
```sql
id          UUID PRIMARY KEY DEFAULT gen_random_uuid()
created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

---

## 2. ERD (Entity Relationship Diagram)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     users       │     │    experts      │     │  expert_scores  │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │◄───┐│ id (PK)         │────▶│ id (PK)         │
│ email           │    ││ user_id (FK)    │     │ expert_id (FK)  │
│ role            │    │├─────────────────┤     │ total_score     │
│ status          │    ││ qualification   │     │ category_scores │
└─────────────────┘    │└────────┬────────┘     └─────────────────┘
                       │         │
                       │         │
┌─────────────────┐    │         │         ┌─────────────────┐
│   applications  │    │         │         │    matchings    │
├─────────────────┤    │         │         ├─────────────────┤
│ id (PK)         │    │         ├────────▶│ id (PK)         │
│ user_id (FK)    │────┘         │         │ expert_id (FK)  │
│ status          │              │         │ demand_id (FK)  │
└─────────────────┘              │         │ status          │
                                 │         └────────┬────────┘
┌─────────────────┐              │                  │
│question_categories│            │                  │
├─────────────────┤              │                  │
│ id (PK)         │              │                  │
│ name            │◄────┐        │                  │
│ weight          │     │        │                  │
└─────────────────┘     │        │                  │
                        │        │                  │
┌─────────────────┐     │        │         ┌─────────────────┐
│    questions    │     │        │         │    companies    │
├─────────────────┤     │        │         ├─────────────────┤
│ id (PK)         │────▶│        │    ┌───▶│ id (PK)         │
│ category_id (FK)│     │        │    │    │ name            │
│ q_type          │     │        │    │    │ industry        │
│ max_score       │◄───┐│        │    │    └─────────────────┘
└─────────────────┘    ││        │    │             │
                       ││        │    │             │
┌─────────────────┐    ││        │    │    ┌────────▼────────┐
│     answers     │    ││        │    │    │     demands     │
├─────────────────┤    │└────────┼────┼───▶├─────────────────┤
│ id (PK)         │────┘         │    │    │ id (PK)         │
│ question_id (FK)│              │    │    │ company_id (FK) │
│ expert_id (FK)  │◄─────────────┘    │    │ status          │
│ score           │                   │    └─────────────────┘
└─────────────────┘                   │
                                      │
┌─────────────────┐                   │
│     reports     │                   │
├─────────────────┤                   │
│ id (PK)         │                   │
│ report_type     │                   │
│ file_url        │                   │
│ generated_by(FK)│───────────────────┘
└─────────────────┘
```

---

## 3. 테이블 상세 설계

### 3.1 users (사용자)
```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(200) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    name            VARCHAR(100) NOT NULL,
    phone           VARCHAR(20),
    role            VARCHAR(20) NOT NULL DEFAULT 'APPLICANT',
    status          VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    last_login_at   TIMESTAMP WITH TIME ZONE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enum 값
-- role: ADMIN | EVALUATOR | APPLICANT
-- status: ACTIVE | INACTIVE | SUSPENDED
```

**인덱스:**
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
```

### 3.2 experts (전문가)
```sql
CREATE TABLE experts (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    degree_type          VARCHAR(20),
    degree_field         VARCHAR(100),
    career_years         INTEGER,
    position             VARCHAR(100),
    org_name             VARCHAR(200),
    org_type             VARCHAR(20),
    specialties          JSONB,
    certifications       JSONB,
    qualification_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    qualification_note   TEXT,
    created_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enum 값
-- degree_type: PHD | MASTER | BACHELOR
-- org_type: UNIVERSITY | COMPANY | RESEARCH | OTHER
-- qualification_status: PENDING | QUALIFIED | DISQUALIFIED
```

**JSONB 구조:**
```json
// specialties
["ML", "DL", "CV", "DATA_INTELLIGENCE"]

// certifications
[
    {"name": "정보처리기사", "issued_date": "2020-05-01", "issuer": "한국산업인력공단"},
    {"name": "데이터분석준전문가", "issued_date": "2021-03-15", "issuer": "한국데이터산업진흥원"}
]
```

**인덱스:**
```sql
CREATE INDEX idx_experts_user_id ON experts(user_id);
CREATE INDEX idx_experts_status ON experts(qualification_status);
CREATE INDEX idx_experts_specialties ON experts USING gin(specialties);
```

### 3.3 question_categories (문항 카테고리)
```sql
CREATE TABLE question_categories (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          VARCHAR(100) NOT NULL UNIQUE,
    description   TEXT,
    weight        INTEGER NOT NULL DEFAULT 10,
    display_order INTEGER NOT NULL DEFAULT 0,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3.4 questions (평가 문항)
```sql
CREATE TABLE questions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id       UUID NOT NULL REFERENCES question_categories(id) ON DELETE RESTRICT,
    q_type            VARCHAR(20) NOT NULL,
    content           TEXT NOT NULL,
    options           JSONB,
    correct_answer    JSONB,
    scoring_rubric    JSONB,
    max_score         INTEGER NOT NULL,
    difficulty        VARCHAR(10) NOT NULL DEFAULT 'MEDIUM',
    target_specialties JSONB,
    explanation       TEXT,
    display_order     INTEGER NOT NULL DEFAULT 0,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enum 값
-- q_type: SINGLE | MULTIPLE | SHORT | ESSAY | FILE
-- difficulty: EASY | MEDIUM | HARD
```

**JSONB 구조:**
```json
// options (객관식)
[
    {"id": 1, "text": "선택지 1"},
    {"id": 2, "text": "선택지 2"},
    {"id": 3, "text": "선택지 3"},
    {"id": 4, "text": "선택지 4"}
]

// correct_answer
{"answer_ids": [1, 3]}  // SINGLE/MULTIPLE
{"keywords": ["머신러닝", "인공지능", "학습"]}  // SHORT/ESSAY

// scoring_rubric
{
    "criteria": [
        {"name": "개념 정의", "max_score": 5, "description": "정확한 정의 포함"},
        {"name": "사례 제시", "max_score": 10, "description": "구체적 사례 2개 이상"},
        {"name": "논리성", "max_score": 5, "description": "논리적 흐름"}
    ]
}
```

**인덱스:**
```sql
CREATE INDEX idx_questions_category_id ON questions(category_id);
CREATE INDEX idx_questions_q_type ON questions(q_type);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
```

### 3.5 answers (답변)
```sql
CREATE TABLE answers (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    expert_id    UUID NOT NULL REFERENCES experts(id) ON DELETE CASCADE,
    question_id  UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    answer_data  JSONB NOT NULL,
    status       VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    score        REAL,
    feedback     TEXT,
    graded_by    UUID REFERENCES users(id) ON DELETE SET NULL,
    graded_at    TIMESTAMP WITH TIME ZONE,
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(expert_id, question_id)
);

-- Enum 값
-- status: PENDING | GRADED | REVIEWING
```

**JSONB 구조:**
```json
// answer_data (객관식)
{"selected_ids": [1, 3]}

// answer_data (주관식/서술형)
{"text": "머신러닝은 데이터로부터 학습하여..."}

// answer_data (파일)
{"file_url": "/uploads/answer_123.pdf", "file_name": "답변서.pdf"}
```

**인덱스:**
```sql
CREATE INDEX idx_answers_expert_id ON answers(expert_id);
CREATE INDEX idx_answers_question_id ON answers(question_id);
CREATE INDEX idx_answers_status ON answers(status);
CREATE UNIQUE INDEX idx_answers_expert_question ON answers(expert_id, question_id);
```

### 3.6 expert_scores (점수 집계)
```sql
CREATE TABLE expert_scores (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    expert_id         UUID NOT NULL UNIQUE REFERENCES experts(id) ON DELETE CASCADE,
    total_score       REAL NOT NULL DEFAULT 0,
    max_possible_score REAL NOT NULL DEFAULT 0,
    average_percentage REAL NOT NULL DEFAULT 0,
    category_scores   JSONB,
    graded_count      INTEGER NOT NULL DEFAULT 0,
    total_count       INTEGER NOT NULL DEFAULT 0,
    last_calculated_at TIMESTAMP WITH TIME ZONE,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**JSONB 구조:**
```json
// category_scores
{
    "ML 기초": {"score": 45, "max": 50, "percentage": 90},
    "DL 응용": {"score": 38, "max": 45, "percentage": 84.4},
    "CV 실습": {"score": 40, "max": 50, "percentage": 80}
}
```

### 3.7 companies (기업)
```sql
CREATE TABLE companies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(200) NOT NULL,
    business_number VARCHAR(20) UNIQUE,
    industry        VARCHAR(20) NOT NULL DEFAULT 'MANUFACTURING',
    size            VARCHAR(20) NOT NULL DEFAULT 'SMALL',
    employee_count  INTEGER,
    address         VARCHAR(500),
    contact_name    VARCHAR(100),
    contact_email   VARCHAR(200),
    contact_phone   VARCHAR(20),
    description     TEXT,
    website         VARCHAR(500),
    registered_by   UUID REFERENCES users(id) ON DELETE SET NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enum 값
-- industry: MANUFACTURING | IT | FINANCE | HEALTHCARE | LOGISTICS | RETAIL | ENERGY | OTHER
-- size: STARTUP | SMALL | MEDIUM | LARGE
```

### 3.8 demands (기업 수요)
```sql
CREATE TABLE demands (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id           UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    title                VARCHAR(200) NOT NULL,
    description          TEXT,
    required_specialties JSONB,
    expert_count         INTEGER NOT NULL DEFAULT 1,
    project_duration     VARCHAR(100),
    budget_range         VARCHAR(100),
    requirements         JSONB,
    status               VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    priority             INTEGER NOT NULL DEFAULT 3,
    is_active            BOOLEAN NOT NULL DEFAULT TRUE,
    created_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enum 값
-- status: PENDING | MATCHED | IN_PROGRESS | COMPLETED | CANCELLED
```

**인덱스:**
```sql
CREATE INDEX idx_demands_company_id ON demands(company_id);
CREATE INDEX idx_demands_status ON demands(status);
CREATE INDEX idx_demands_specialties ON demands USING gin(required_specialties);
```

### 3.9 matchings (매칭)
```sql
CREATE TABLE matchings (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    expert_id          UUID NOT NULL REFERENCES experts(id) ON DELETE CASCADE,
    demand_id          UUID NOT NULL REFERENCES demands(id) ON DELETE CASCADE,
    matching_type      VARCHAR(20) NOT NULL DEFAULT 'AUTO',
    status             VARCHAR(20) NOT NULL DEFAULT 'PROPOSED',
    match_score        REAL,
    score_breakdown    JSONB,
    matching_reason    TEXT,
    expert_response    TEXT,
    expert_responded_at VARCHAR(50),
    company_feedback   TEXT,
    company_rating     INTEGER CHECK (company_rating >= 1 AND company_rating <= 5),
    matched_by         UUID REFERENCES users(id) ON DELETE SET NULL,
    project_start_date VARCHAR(50),
    project_end_date   VARCHAR(50),
    is_active          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at         TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enum 값
-- matching_type: AUTO | MANUAL | REQUESTED
-- status: PROPOSED | ACCEPTED | REJECTED | IN_PROGRESS | COMPLETED | CANCELLED
```

**JSONB 구조:**
```json
// score_breakdown
{
    "specialty": 95.0,
    "qualification": 100.0,
    "career": 80.0,
    "evaluation": 85.0,
    "availability": 70.0
}
```

**인덱스:**
```sql
CREATE INDEX idx_matchings_expert_id ON matchings(expert_id);
CREATE INDEX idx_matchings_demand_id ON matchings(demand_id);
CREATE INDEX idx_matchings_status ON matchings(status);
CREATE INDEX idx_matchings_score ON matchings(match_score DESC);
```

### 3.10 reports (보고서)
```sql
CREATE TABLE reports (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_type   VARCHAR(30) NOT NULL,
    title         VARCHAR(200) NOT NULL,
    parameters    JSONB,
    data          JSONB,
    file_url      VARCHAR(500),
    generated_by  UUID REFERENCES users(id) ON DELETE SET NULL,
    status        VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enum 값
-- report_type: EXPERT_EVALUATION | SYSTEM_SUMMARY | MATCHING_ANALYSIS
-- status: PENDING | COMPLETED | FAILED
```

**인덱스:**
```sql
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_generated_by ON reports(generated_by);
CREATE INDEX idx_reports_status ON reports(status);
```

### 3.11 applications (지원서)
```sql
CREATE TABLE applications (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    application_type VARCHAR(20) NOT NULL DEFAULT 'NEW',
    status           VARCHAR(20) NOT NULL DEFAULT 'SUBMITTED',
    submitted_at     TIMESTAMP WITH TIME ZONE,
    reviewed_at      TIMESTAMP WITH TIME ZONE,
    reviewed_by      UUID REFERENCES users(id) ON DELETE SET NULL,
    review_note      TEXT,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enum 값
-- application_type: NEW | RENEWAL
-- status: DRAFT | SUBMITTED | REVIEWING | APPROVED | REJECTED
```

---

## 4. 마이그레이션 이력

| 버전 | 날짜 | 설명 |
|------|------|------|
| 001 | 2026-01-08 | 초기 스키마 생성 (users, experts, questions, answers) |
| 002 | 2026-01-09 | 기업/매칭 테이블 추가 (companies, demands, matchings) |
| 003 | 2026-01-10 | 점수 집계 테이블 추가 (expert_scores) |
| 004 | 2026-01-10 | 보고서 테이블 추가 (reports) |

---

## 5. 성능 최적화

### 5.1 인덱스 전략
- **단일 컬럼 인덱스**: 자주 조회되는 FK 및 상태 필드
- **GIN 인덱스**: JSONB 배열 필드 (specialties, required_specialties)
- **복합 인덱스**: 자주 함께 조회되는 필드 조합

### 5.2 파티셔닝 (향후)
- answers 테이블: 월별 파티셔닝 고려
- reports 테이블: 연도별 파티셔닝 고려

### 5.3 캐싱 전략
- 매칭 스코어: Redis 캐시 (TTL: 1시간)
- 전문가 목록: Redis 캐시 (TTL: 5분)

---

## 6. 백업 및 복구

### 6.1 백업 정책
- **일일 백업**: 매일 03:00 AM (전체 백업)
- **보관 기간**: 30일

### 6.2 복구 절차
```bash
# 백업에서 복구
pg_restore -U postgres -d ax_coaching backup_file.dump
```

---

## 부록: DDL 스크립트

전체 DDL 스크립트는 다음 위치에서 확인:
- `backend/src/alembic/versions/` - 마이그레이션 파일
