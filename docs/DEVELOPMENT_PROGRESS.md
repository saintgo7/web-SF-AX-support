# AX 코칭단 평가 시스템 - 개발 진행 현황 문서

**문서번호:** AX-DEV-PROGRESS-2025-001
**버전:** 1.0
**작성일:** 2026-01-10
**프로젝트명:** 스마트공장 AX 코칭단 전문가 평가 및 매칭 시스템

---

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [기술 스택](#2-기술-스택)
3. [시스템 아키텍처](#3-시스템-아키텍처)
4. [개발 진행 현황](#4-개발-진행-현황)
5. [구현 완료 기능](#5-구현-완료-기능)
6. [데이터 모델](#6-데이터-모델)
7. [API 명세](#7-api-명세)
8. [프론트엔드 구조](#8-프론트엔드-구조)
9. [테스트 현황](#9-테스트-현황)
10. [배포 환경](#10-배포-환경)
11. [향후 개발 계획](#11-향후-개발-계획)

---

## 1. 프로젝트 개요

### 1.1 프로젝트 목적

스마트공장 AX 코칭단 전문가 평가 및 매칭 시스템은 다음 목표를 위해 개발되었습니다:

| 구분 | 목표 | 성과지표 |
|------|------|----------|
| 정량목표 | 전문가 평가 자동화율 80% 이상 | 수동 검토 대비 처리시간 50% 단축 |
| 정성목표 | 객관적/공정한 전문가 선정 | 평가위원 만족도 4.0/5.0 이상 |
| 운영목표 | 전문가-기업 매칭 정확도 향상 | 매칭 성공률 85% 이상 |

### 1.2 프로젝트 범위

```
[Scope-In]
  ├─ [A] 전문가 자격요건 자동 검증
  │     ├─ 학위/경력 조건 충족 여부 판정
  │     └─ 해당분야(ML, DL, CV, 데이터인텔리전스) 매칭
  │
  ├─ [B] AX 기능별 질의응답 시스템
  │     ├─ 분야별 평가 문항 DB 설계/구축
  │     └─ 응답 수집 및 자동 채점
  │
  ├─ [C] 평가 점수 산정 및 리포트
  │     ├─ 가중치 기반 종합 점수 산출
  │     └─ 평가 결과 보고서 자동 생성
  │
  └─ [D] 수요기업 매칭 지원
        ├─ 전문가-기업 적합도 분석
        └─ 최적 매칭 추천 알고리즘
```

### 1.3 이해관계자

| 역할 | 조직 | 책임 |
|------|------|------|
| 발주처 | 중소벤처기업부 | 사업 총괄, 정책 결정 |
| 추진기관 | 스마트제조혁신추진단 | 사업 운영, 성과 관리 |
| 운영기관 | (지정기관) | 시스템 운영, 전문가 관리 |
| 평가위원 | 산학연 전문가 | 전문가 선정 평가 수행 |
| 신청자 | AX 전문가 후보 | 등록 신청, 평가 응시 |
| 수요기업 | 중소/중견 제조기업 | 컨설팅 수혜, 만족도 평가 |

---

## 2. 기술 스택

### 2.1 Backend

| 기술 | 버전 | 용도 |
|------|------|------|
| Python | 3.11+ | 런타임 환경 |
| FastAPI | Latest | 웹 프레임워크 |
| PostgreSQL | 15+ | 메인 데이터베이스 |
| Redis | 7+ | 캐시 및 세션 저장소 |
| SQLAlchemy | 2.0 | ORM (비동기 지원) |
| Alembic | Latest | 데이터베이스 마이그레이션 |
| Pydantic | v2 | 데이터 검증 및 직렬화 |
| Poetry | Latest | 패키지 관리 |
| bcrypt | Latest | 비밀번호 해싱 |
| PyJWT | Latest | JWT 토큰 관리 |

### 2.2 Frontend

| 기술 | 버전 | 용도 |
|------|------|------|
| Next.js | 14.1.0 | React 프레임워크 (App Router) |
| React | 18.2.0 | UI 라이브러리 |
| TypeScript | 5.x | 타입 안정성 |
| Tailwind CSS | 3.4.1 | 유틸리티 CSS 프레임워크 |
| Zustand | 4.5.0 | 상태 관리 |
| TanStack Query | 5.17.9 | 서버 상태 관리 |
| React Hook Form | 7.49.3 | 폼 관리 |
| Zod | 3.22.4 | 스키마 검증 |
| Recharts | 2.10.3 | 차트 라이브러리 |
| Axios | 1.6.5 | HTTP 클라이언트 |

### 2.3 Infrastructure

| 기술 | 용도 |
|------|------|
| Docker | 컨테이너화 |
| Docker Compose | 로컬 개발 환경 오케스트레이션 |
| GitHub Actions | CI/CD 파이프라인 |

---

## 3. 시스템 아키텍처

### 3.1 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Next.js 14 Frontend                     │    │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐           │    │
│  │   │ Admin   │  │Evaluator│  │Applicant│           │    │
│  │   │ Portal  │  │ Portal  │  │ Portal  │           │    │
│  │   └─────────┘  └─────────┘  └─────────┘           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              FastAPI Backend (Port 8000)             │    │
│  │   ┌───────┐ ┌────────┐ ┌─────────┐ ┌─────────┐     │    │
│  │   │ Auth  │ │Experts │ │Questions│ │Matching │     │    │
│  │   │ API   │ │  API   │ │   API   │ │   API   │     │    │
│  │   └───────┘ └────────┘ └─────────┘ └─────────┘     │    │
│  │   ┌─────────┐ ┌────────┐ ┌─────────┐ ┌────────┐   │    │
│  │   │Evaluate │ │Company │ │ Reports │ │ Admin  │   │    │
│  │   │  API    │ │  API   │ │   API   │ │  API   │   │    │
│  │   └─────────┘ └────────┘ └─────────┘ └────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│  ┌─────────────────────┐    ┌─────────────────────┐        │
│  │   PostgreSQL 15     │    │      Redis 7        │        │
│  │   (Primary DB)      │    │   (Cache/Session)   │        │
│  │   ┌─────────────┐   │    │                     │        │
│  │   │ users       │   │    │   - JWT Tokens      │        │
│  │   │ experts     │   │    │   - Rate Limiting   │        │
│  │   │ questions   │   │    │   - Session Data    │        │
│  │   │ answers     │   │    │                     │        │
│  │   │ companies   │   │    └─────────────────────┘        │
│  │   │ matchings   │   │                                    │
│  │   └─────────────┘   │                                    │
│  └─────────────────────┘                                    │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 프로젝트 디렉토리 구조

```
ax-coaching-eval-system/
├── backend/                    # FastAPI Backend
│   ├── src/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── v1/
│   │   │   │   │   ├── api.py           # Router 통합
│   │   │   │   │   ├── auth.py          # 인증 API
│   │   │   │   │   ├── experts.py       # 전문가 API
│   │   │   │   │   ├── questions.py     # 문항 API
│   │   │   │   │   ├── evaluation.py    # 평가 API
│   │   │   │   │   ├── applications.py  # 신청 API
│   │   │   │   │   ├── companies.py     # 기업 API
│   │   │   │   │   ├── matchings.py     # 매칭 API
│   │   │   │   │   ├── admin.py         # 관리자 API
│   │   │   │   │   └── reports.py       # 리포트 API
│   │   │   │   └── deps.py              # 의존성 주입
│   │   │   ├── core/
│   │   │   │   ├── security.py          # 보안 설정
│   │   │   │   ├── rate_limiter.py      # 레이트 리미터
│   │   │   │   └── captcha.py           # CAPTCHA
│   │   │   ├── db/
│   │   │   │   ├── base.py              # Base 모델
│   │   │   │   └── session.py           # DB 세션
│   │   │   ├── models/
│   │   │   │   ├── __init__.py          # 모델 export
│   │   │   │   ├── user.py              # User 모델
│   │   │   │   ├── expert.py            # Expert 모델
│   │   │   │   ├── question.py          # Question 모델
│   │   │   │   ├── answer.py            # Answer 모델
│   │   │   │   ├── application.py       # Application 모델
│   │   │   │   ├── company.py           # Company 모델
│   │   │   │   └── matching.py          # Matching 모델
│   │   │   ├── schemas/
│   │   │   │   ├── user.py              # User 스키마
│   │   │   │   ├── expert.py            # Expert 스키마
│   │   │   │   ├── question.py          # Question 스키마
│   │   │   │   ├── answer.py            # Answer 스키마
│   │   │   │   ├── application.py       # Application 스키마
│   │   │   │   ├── company.py           # Company 스키마
│   │   │   │   └── matching.py          # Matching 스키마
│   │   │   └── services/
│   │   │       ├── question_service.py  # 문항 서비스
│   │   │       ├── grading_service.py   # 채점 서비스
│   │   │       └── email_service.py     # 이메일 서비스
│   │   ├── alembic/
│   │   │   ├── env.py                   # Alembic 환경
│   │   │   └── versions/                # 마이그레이션 파일
│   │   ├── main.py                      # 애플리케이션 진입점
│   │   └── config.py                    # 설정 관리
│   ├── tests/
│   │   ├── conftest.py                  # 테스트 픽스처
│   │   ├── test_question_service.py     # 문항 서비스 테스트
│   │   ├── test_grading_service.py      # 채점 서비스 테스트
│   │   ├── test_questions_api.py        # 문항 API 테스트
│   │   ├── test_evaluation_api.py       # 평가 API 테스트
│   │   └── test_qualification.py        # 자격검증 테스트
│   ├── scripts/
│   │   └── generate_password_hash.py    # 비밀번호 해시 유틸
│   └── pyproject.toml                   # Poetry 의존성
│
├── frontend/                   # Next.js Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx               # 루트 레이아웃
│   │   │   ├── page.tsx                 # 메인 페이지
│   │   │   ├── providers.tsx            # 프로바이더 설정
│   │   │   ├── auth/
│   │   │   │   ├── login/page.tsx       # 로그인
│   │   │   │   ├── register/page.tsx    # 회원가입
│   │   │   │   ├── forgot-password/     # 비밀번호 찾기
│   │   │   │   └── reset-password/      # 비밀번호 재설정
│   │   │   ├── admin/
│   │   │   │   ├── layout.tsx           # 관리자 레이아웃
│   │   │   │   ├── dashboard/page.tsx   # 대시보드
│   │   │   │   ├── experts/page.tsx     # 전문가 관리
│   │   │   │   ├── questions/page.tsx   # 문항 관리
│   │   │   │   ├── matching/page.tsx    # 매칭 관리
│   │   │   │   └── reports/page.tsx     # 리포트
│   │   │   ├── evaluator/
│   │   │   │   ├── layout.tsx           # 평가위원 레이아웃
│   │   │   │   ├── dashboard/page.tsx   # 대시보드
│   │   │   │   ├── pending/page.tsx     # 대기 평가
│   │   │   │   └── history/page.tsx     # 평가 이력
│   │   │   └── applicant/
│   │   │       ├── layout.tsx           # 신청자 레이아웃
│   │   │       ├── dashboard/page.tsx   # 대시보드
│   │   │       ├── application/page.tsx # 신청서
│   │   │       ├── evaluation/page.tsx  # 평가 응시
│   │   │       └── results/page.tsx     # 결과 조회
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   ├── Button.tsx           # 버튼
│   │   │   │   ├── Input.tsx            # 입력 필드
│   │   │   │   ├── Select.tsx           # 셀렉트박스
│   │   │   │   ├── Textarea.tsx         # 텍스트영역
│   │   │   │   ├── Card.tsx             # 카드
│   │   │   │   ├── Modal.tsx            # 모달
│   │   │   │   ├── Table.tsx            # 테이블
│   │   │   │   ├── Badge.tsx            # 뱃지
│   │   │   │   ├── Alert.tsx            # 알림
│   │   │   │   └── index.ts             # UI export
│   │   │   └── layout/
│   │   │       ├── Header.tsx           # 헤더
│   │   │       ├── Sidebar.tsx          # 사이드바
│   │   │       └── index.ts             # 레이아웃 export
│   │   ├── hooks/
│   │   │   ├── useAuth.ts               # 인증 훅
│   │   │   ├── useAuthApi.ts            # 인증 API 훅
│   │   │   ├── useExpert.ts             # 전문가 훅
│   │   │   ├── useEvaluation.ts         # 평가 훅
│   │   │   ├── useApplication.ts        # 신청 훅
│   │   │   └── index.ts                 # 훅 export
│   │   ├── lib/
│   │   │   ├── axios.ts                 # Axios 설정
│   │   │   ├── utils.ts                 # 유틸리티
│   │   │   ├── constants.ts             # 상수 정의
│   │   │   ├── api/
│   │   │   │   ├── auth.ts              # 인증 API
│   │   │   │   ├── expert.ts            # 전문가 API
│   │   │   │   ├── questions.ts         # 문항 API
│   │   │   │   ├── evaluation.ts        # 평가 API
│   │   │   │   ├── application.ts       # 신청 API
│   │   │   │   ├── companies.ts         # 기업 API
│   │   │   │   ├── matching.ts          # 매칭 API
│   │   │   │   ├── matchings.ts         # 매칭 관리 API
│   │   │   │   ├── admin.ts             # 관리자 API
│   │   │   │   ├── reports.ts           # 리포트 API
│   │   │   │   └── index.ts             # API export
│   │   │   └── validations/
│   │   │       ├── auth.ts              # 인증 검증
│   │   │       ├── expert.ts            # 전문가 검증
│   │   │       └── index.ts             # 검증 export
│   │   ├── store/
│   │   │   ├── authStore.ts             # 인증 상태
│   │   │   ├── expertStore.ts           # 전문가 상태
│   │   │   └── index.ts                 # 스토어 export
│   │   └── types/
│   │       ├── user.ts                  # 사용자 타입
│   │       ├── expert.ts                # 전문가 타입
│   │       ├── evaluation.ts            # 평가 타입
│   │       ├── application.ts           # 신청 타입
│   │       ├── matching.ts              # 매칭 타입
│   │       ├── common.ts                # 공통 타입
│   │       └── index.ts                 # 타입 export
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
│
├── docker/                     # Docker 설정
│   └── docker-compose.yml
│
├── docs/                       # 문서
│   ├── plan/
│   │   └── plan.md             # 개발 계획서
│   └── DEVELOPMENT_PROGRESS.md # 본 문서
│
├── README.md                   # 프로젝트 소개
├── SPRINT3_README.md           # Sprint 3 완료 보고
└── .gitignore
```

---

## 4. 개발 진행 현황

### 4.1 스프린트 일정 개요

| 스프린트 | 기간 | 목표 | 상태 |
|----------|------|------|------|
| Sprint 1 | W5-W6 | 기반 구축 | ✅ 완료 |
| Sprint 2 | W7-W8 | 자격검증 시스템 | ✅ 완료 |
| Sprint 3 | W9-W10 | 질의응답 시스템 | ✅ 완료 |
| Sprint 4 | W11-W12 | 채점 시스템 | ⏳ 대기 |
| Sprint 5 | W13-W14 | 리포트 시스템 | ⏳ 대기 |
| Sprint 6 | W15-W16 | 매칭 시스템 | ⏳ 대기 |

### 4.2 Sprint 1: 기반 구축 (✅ 완료)

**기간:** W5-W6
**상태:** 완료

#### 구현 내용

1. **프로젝트 초기 설정**
   - Backend: FastAPI + Poetry 프로젝트 생성
   - Frontend: Next.js 14 App Router 프로젝트 생성
   - Docker Compose 개발 환경 구성

2. **데이터베이스 설계**
   - PostgreSQL 스키마 설계
   - SQLAlchemy 2.0 비동기 모델 구현
   - Alembic 마이그레이션 환경 구성

3. **인증 시스템**
   - JWT 기반 인증 구현
   - 회원가입/로그인/로그아웃 API
   - 비밀번호 해싱 (bcrypt)
   - 레이트 리미터 구현

4. **기본 UI 컴포넌트**
   - Button, Input, Select, Card 등 UI 컴포넌트
   - 인증 페이지 (로그인, 회원가입, 비밀번호 재설정)
   - 레이아웃 (Header, Sidebar)

5. **상태 관리**
   - Zustand 스토어 설정 (authStore, expertStore)
   - React Query 설정

### 4.3 Sprint 2: 자격검증 시스템 (✅ 완료)

**기간:** W7-W8
**상태:** 완료

#### 구현 내용

1. **전문가 데이터 모델**
   - Expert 모델 (학위, 경력, 자격증, 전문분야)
   - Application 모델 (신청 정보)
   - DegreeType, OrgType, QualificationStatus Enum

2. **자격요건 검증 로직**
   ```python
   IF (박사학위 AND 관련분야 AND 경력>=3년) THEN 적합
   ELSE IF (석사학위 AND 관련분야 AND 경력>=5년) THEN 적합
   ELSE IF (학사학위 AND 관련분야 AND 경력>=7년) THEN 적합
   ELSE IF (부장급이상 OR 전임강사이상 OR 특급기술자이상) THEN 적합
   ELSE 부적합
   ```

3. **전문가 관리 API**
   - 전문가 CRUD 엔드포인트
   - 자격검증 API
   - 신청서 관리 API

4. **관리자 대시보드**
   - 전문가 목록 조회/검색
   - 자격 상태 필터링
   - 상세 정보 모달

### 4.4 Sprint 3: 질의응답 시스템 (✅ 완료)

**기간:** W9-W10
**상태:** 완료
**구현일:** 2025-01-10

#### 구현 내용

1. **평가 문항 데이터 모델**
   - Question 모델
     - 문항 유형: 객관식(단일/다중), 주관식(단답/서술), 파일첨부
     - 난이도: EASY, MEDIUM, HARD
     - 전문분야별 타겟팅
   - QuestionCategory 모델 (평가 영역)

2. **응답 수집 시스템**
   - Answer 모델
     - 버전 관리 지원
     - 상태: DRAFT, SUBMITTED, GRADED
   - 응답 제출 API
   - 일괄 제출 지원

3. **자동 채점 시스템**
   - 객관식 단일 선택 정답 매칭
   - 다중 선택 부분 점수 계산
   - 자동 채점 API

4. **서비스 레이어**
   - QuestionService: 문항 비즈니스 로직
   - GradingService: 채점 비즈니스 로직

#### Sprint 3 파일 목록

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
│       └── evaluation.py        # Evaluation API
└── tests/
    ├── test_question_service.py # 15 unit tests
    ├── test_grading_service.py  # 12 unit tests
    ├── test_questions_api.py    # 13 integration tests
    └── test_evaluation_api.py   # 14 integration tests
```

---

## 5. 구현 완료 기능

### 5.1 기능 매트릭스

| 기능 영역 | 기능 | Backend | Frontend | 테스트 |
|-----------|------|---------|----------|--------|
| **인증** | 로그인 | ✅ | ✅ | ✅ |
| | 회원가입 | ✅ | ✅ | ✅ |
| | 비밀번호 재설정 | ✅ | ✅ | - |
| | JWT 토큰 관리 | ✅ | ✅ | ✅ |
| **전문가 관리** | 전문가 등록 | ✅ | ✅ | ✅ |
| | 전문가 조회 | ✅ | ✅ | ✅ |
| | 자격 검증 | ✅ | ✅ | ✅ |
| | 전문분야 관리 | ✅ | ✅ | - |
| **평가 문항** | 카테고리 관리 | ✅ | ✅ | ✅ |
| | 문항 CRUD | ✅ | ✅ | ✅ |
| | 전문분야별 필터링 | ✅ | ✅ | ✅ |
| **응답/채점** | 응답 제출 | ✅ | ✅ | ✅ |
| | 일괄 제출 | ✅ | ✅ | ✅ |
| | 객관식 자동 채점 | ✅ | - | ✅ |
| | 수동 채점 | ✅ | ✅ | ✅ |
| **신청 관리** | 신청서 작성 | ✅ | ✅ | - |
| | 신청서 조회 | ✅ | ✅ | - |
| | 상태 변경 | ✅ | ✅ | - |
| **기업 관리** | 기업 등록 | ✅ | - | - |
| | 수요 등록 | ✅ | - | - |
| **매칭** | 매칭 생성 | ✅ | ✅ | - |
| | 매칭 조회 | ✅ | ✅ | - |
| **리포트** | 통계 조회 | ✅ | - | - |

### 5.2 API 엔드포인트 현황

#### 인증 API (`/api/v1/auth`)
- `POST /login` - 사용자 로그인
- `POST /register` - 사용자 회원가입
- `POST /refresh` - 토큰 갱신
- `POST /logout` - 로그아웃
- `POST /forgot-password` - 비밀번호 찾기
- `POST /reset-password` - 비밀번호 재설정

#### 전문가 API (`/api/v1/experts`)
- `GET /` - 전문가 목록 조회
- `POST /` - 전문가 등록
- `GET /{id}` - 전문가 상세 조회
- `PUT /{id}` - 전문가 정보 수정
- `POST /qualification/verify` - 자격 검증

#### 문항 API (`/api/v1/questions`)
- `POST /categories` - 카테고리 생성
- `GET /categories` - 카테고리 목록
- `POST /` - 문항 생성
- `GET /` - 문항 목록 (필터링 지원)
- `GET /{id}` - 문항 상세
- `PUT /{id}` - 문항 수정
- `DELETE /{id}` - 문항 삭제
- `GET /by-specialties/{specialties}` - 전문분야별 문항

#### 평가 API (`/api/v1/evaluation`)
- `POST /answers` - 응답 생성
- `POST /submit` - 일괄 제출
- `POST /grade/auto` - 자동 채점
- `POST /grade/{id}/manual` - 수동 채점
- `POST /grade/batch/{expert_id}` - 일괄 채점

#### 신청 API (`/api/v1/applications`)
- `GET /` - 신청 목록
- `POST /` - 신청서 생성
- `GET /{id}` - 신청 상세
- `PUT /{id}` - 신청 수정
- `PATCH /{id}/status` - 상태 변경

#### 기업 API (`/api/v1/companies`)
- `GET /` - 기업 목록
- `POST /` - 기업 등록
- `GET /{id}` - 기업 상세
- `PUT /{id}` - 기업 수정

#### 수요 API (`/api/v1/demands`)
- `GET /` - 수요 목록
- `POST /` - 수요 등록
- `GET /{id}` - 수요 상세

#### 매칭 API (`/api/v1/matchings`)
- `GET /` - 매칭 목록
- `POST /` - 매칭 생성
- `GET /{id}` - 매칭 상세
- `PUT /{id}` - 매칭 수정
- `PATCH /{id}/status` - 상태 변경

#### 관리자 API (`/api/v1/admin`)
- `GET /users` - 사용자 목록
- `GET /statistics` - 통계 데이터
- `POST /settings` - 설정 변경

#### 리포트 API (`/api/v1/reports`)
- `GET /overview` - 전체 현황
- `GET /experts/{id}` - 전문가 리포트
- `GET /evaluation/{id}` - 평가 리포트

---

## 6. 데이터 모델

### 6.1 핵심 모델 다이어그램

```
┌──────────────┐      ┌───────────────┐      ┌────────────────┐
│    User      │      │    Expert     │      │  Application   │
├──────────────┤      ├───────────────┤      ├────────────────┤
│ id (PK)      │◄────►│ id (PK)       │◄────►│ id (PK)        │
│ email        │      │ user_id (FK)  │      │ expert_id (FK) │
│ password_hash│      │ degree_type   │      │ status         │
│ name         │      │ career_years  │      │ type           │
│ role         │      │ specialties   │      │ submitted_at   │
│ status       │      │ qual_status   │      │                │
└──────────────┘      └───────────────┘      └────────────────┘
                             │
                             ▼
┌───────────────────────────────────────────────────────────────┐
│                                                               │
▼                                                               ▼
┌────────────────┐      ┌───────────────┐      ┌────────────────┐
│   Question     │      │    Answer     │      │   Matching     │
├────────────────┤      ├───────────────┤      ├────────────────┤
│ id (PK)        │◄────►│ id (PK)       │      │ id (PK)        │
│ category_id    │      │ question_id   │      │ expert_id (FK) │
│ q_type         │      │ expert_id     │      │ company_id (FK)│
│ content        │      │ answer_data   │      │ demand_id (FK) │
│ options        │      │ score         │      │ status         │
│ correct_answer │      │ status        │      │ type           │
│ max_score      │      │ version       │      │ score          │
│ difficulty     │      │               │      │                │
└────────────────┘      └───────────────┘      └────────────────┘
        │                                              │
        ▼                                              ▼
┌────────────────┐                        ┌────────────────┐
│QuestionCategory│                        │    Company     │
├────────────────┤                        ├────────────────┤
│ id (PK)        │                        │ id (PK)        │
│ name           │                        │ name           │
│ code           │                        │ size           │
│ description    │                        │ industry_type  │
│ weight         │                        │ demands[]      │
└────────────────┘                        └────────────────┘
```

### 6.2 주요 Enum 정의

#### UserRole (사용자 역할)
```python
class UserRole(str, Enum):
    APPLICANT = "applicant"    # 신청자
    EVALUATOR = "evaluator"    # 평가위원
    OPERATOR = "operator"      # 운영자
    ADMIN = "admin"            # 관리자
```

#### DegreeType (학위 유형)
```python
class DegreeType(str, Enum):
    PHD = "phd"           # 박사
    MASTER = "master"     # 석사
    BACHELOR = "bachelor" # 학사
```

#### QuestionType (문항 유형)
```python
class QuestionType(str, Enum):
    SINGLE = "single"       # 단일 선택
    MULTIPLE = "multiple"   # 다중 선택
    SHORT = "short"         # 단답형
    ESSAY = "essay"         # 서술형
    FILE = "file"           # 파일 첨부
```

#### Difficulty (난이도)
```python
class Difficulty(str, Enum):
    EASY = "easy"       # 쉬움
    MEDIUM = "medium"   # 보통
    HARD = "hard"       # 어려움
```

#### Specialty (전문분야)
```python
class Specialty(str, Enum):
    ML = "ml"                            # 머신러닝
    DL = "dl"                            # 딥러닝
    CV = "cv"                            # 컴퓨터 비전
    NLP = "nlp"                          # 자연어 처리
    COMPUTING_PLATFORM = "computing"     # 컴퓨팅 플랫폼
    DATA_INTELLIGENCE = "data_intel"     # 데이터 인텔리전스
```

#### AnswerStatus (응답 상태)
```python
class AnswerStatus(str, Enum):
    DRAFT = "draft"         # 작성 중
    SUBMITTED = "submitted" # 제출됨
    GRADED = "graded"       # 채점됨
```

---

## 7. API 명세

### 7.1 인증 API

#### POST /api/v1/auth/login

사용자 로그인

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "홍길동",
    "role": "applicant"
  }
}
```

### 7.2 문항 API

#### POST /api/v1/questions

문항 생성

**Request Body:**
```json
{
  "category_id": "uuid",
  "q_type": "single",
  "content": "AI 모델 학습에서 과적합을 방지하기 위한 방법으로 적절하지 않은 것은?",
  "options": [
    {"key": "A", "value": "드롭아웃(Dropout) 적용"},
    {"key": "B", "value": "조기 종료(Early Stopping)"},
    {"key": "C", "value": "배치 크기 증가"},
    {"key": "D", "value": "데이터 증강(Data Augmentation)"}
  ],
  "correct_answer": ["C"],
  "max_score": 5,
  "difficulty": "medium",
  "target_specialties": ["ml", "dl"]
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "category_id": "uuid",
  "q_type": "single",
  "content": "AI 모델 학습에서 과적합을...",
  "options": [...],
  "correct_answer": ["C"],
  "max_score": 5,
  "difficulty": "medium",
  "target_specialties": ["ml", "dl"],
  "is_active": true,
  "created_at": "2025-01-10T00:00:00Z"
}
```

### 7.3 평가 API

#### POST /api/v1/evaluation/grade/auto

자동 채점 수행

**Request Body:**
```json
{
  "answer_id": "uuid"
}
```

**Response (200):**
```json
{
  "answer_id": "uuid",
  "question_id": "uuid",
  "score": 5,
  "max_score": 5,
  "is_correct": true,
  "grading_type": "auto",
  "graded_at": "2025-01-10T00:00:00Z"
}
```

---

## 8. 프론트엔드 구조

### 8.1 페이지 라우팅

```
/                           # 메인 페이지 (로그인 리다이렉트)
/auth/login                 # 로그인
/auth/register              # 회원가입
/auth/forgot-password       # 비밀번호 찾기
/auth/reset-password        # 비밀번호 재설정

/admin/dashboard            # 관리자 대시보드
/admin/experts              # 전문가 관리
/admin/questions            # 문항 관리
/admin/matching             # 매칭 관리
/admin/reports              # 리포트

/evaluator/dashboard        # 평가위원 대시보드
/evaluator/pending          # 대기 중 평가
/evaluator/history          # 평가 이력

/applicant/dashboard        # 신청자 대시보드
/applicant/application      # 신청서 작성
/applicant/evaluation       # 평가 응시
/applicant/results          # 결과 조회
```

### 8.2 UI 컴포넌트

#### 기본 컴포넌트 (src/components/ui/)

| 컴포넌트 | 설명 | Props |
|----------|------|-------|
| Button | 버튼 | variant, size, loading, disabled |
| Input | 입력 필드 | type, label, error, placeholder |
| Select | 셀렉트박스 | options, value, onChange |
| Textarea | 텍스트영역 | rows, maxLength |
| Card | 카드 컨테이너 | title, description, actions |
| Modal | 모달 다이얼로그 | open, onClose, title |
| Table | 테이블 | columns, data, pagination |
| Badge | 상태 뱃지 | variant, text |
| Alert | 알림 메시지 | type, title, message |

#### 레이아웃 컴포넌트 (src/components/layout/)

| 컴포넌트 | 설명 |
|----------|------|
| Header | 상단 네비게이션 바 (로고, 사용자 메뉴) |
| Sidebar | 사이드 네비게이션 (역할별 메뉴) |

### 8.3 상태 관리

#### authStore (인증 상태)
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
}
```

#### expertStore (전문가 상태)
```typescript
interface ExpertState {
  experts: Expert[];
  selectedExpert: Expert | null;
  filters: ExpertFilters;
  isLoading: boolean;
  fetchExperts: () => Promise<void>;
  selectExpert: (id: string) => void;
  setFilters: (filters: ExpertFilters) => void;
}
```

### 8.4 API 클라이언트

```typescript
// lib/axios.ts
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 인터셉터: 토큰 자동 첨부
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 인터셉터: 401 에러 처리
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // 토큰 갱신 또는 로그아웃
    }
    return Promise.reject(error);
  }
);
```

---

## 9. 테스트 현황

### 9.1 테스트 커버리지

| 영역 | 단위 테스트 | 통합 테스트 | 합계 |
|------|-------------|-------------|------|
| 문항 서비스 | 15 | - | 15 |
| 채점 서비스 | 12 | - | 12 |
| 문항 API | - | 13 | 13 |
| 평가 API | - | 14 | 14 |
| **합계** | **27** | **27** | **54** |

### 9.2 테스트 실행 방법

```bash
cd backend

# 전체 테스트
pytest

# 특정 테스트 파일
pytest tests/test_question_service.py
pytest tests/test_grading_service.py
pytest tests/test_questions_api.py
pytest tests/test_evaluation_api.py

# 커버리지 포함
pytest --cov=src/app --cov-report=html

# 상세 출력
pytest -v
```

### 9.3 주요 테스트 케이스

#### 문항 서비스 테스트
- 카테고리 생성/조회/수정/삭제
- 문항 생성 (모든 유형)
- 문항 필터링 (전문분야, 난이도)
- 문항 활성화/비활성화

#### 채점 서비스 테스트
- 단일 선택 채점 (정답/오답)
- 다중 선택 부분 점수 계산
- 수동 채점 저장
- 일괄 채점

#### API 통합 테스트
- 인증 필수 엔드포인트 검증
- 권한 검증 (역할별 접근 제어)
- 입력 검증 오류 응답
- 페이지네이션

---

## 10. 배포 환경

### 10.1 Docker Compose 설정

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/ax_eval
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ax_eval
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 10.2 실행 방법

```bash
# 서비스 시작
cd docker
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down

# 볼륨 포함 삭제
docker-compose down -v
```

### 10.3 서비스 포트

| 서비스 | 포트 | 설명 |
|--------|------|------|
| Frontend | 3000 | Next.js 웹 애플리케이션 |
| Backend | 8000 | FastAPI REST API |
| PostgreSQL | 5432 | 데이터베이스 |
| Redis | 6379 | 캐시/세션 |

### 10.4 API 문서 접속

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 11. 향후 개발 계획

### 11.1 Sprint 4: 채점 시스템 고도화

| 기능 | 우선순위 | 설명 |
|------|----------|------|
| 주관식 AI 보조 채점 | 높음 | 키워드 추출, 유사도 분석 기반 예비 점수 |
| 평가위원 채점 UI | 높음 | 주관식 수동 채점, 코멘트 작성 인터페이스 |
| 채점 결과 대시보드 | 중간 | 채점 현황, 진행률 시각화 |
| 채점자 간 신뢰도 분석 | 낮음 | Inter-rater reliability 계산 |

### 11.2 Sprint 5: 리포트 시스템

| 기능 | 우선순위 | 설명 |
|------|----------|------|
| 개인별 평가 리포트 | 높음 | 영역별 점수, 강점/약점 분석 |
| 종합 통계 리포트 | 높음 | 전체 응시자 분포, 합격선 분석 |
| PDF 출력 | 높음 | 공식 양식 기반 PDF 자동 생성 |
| 데이터 시각화 | 중간 | 차트, 그래프 컴포넌트 |

### 11.3 Sprint 6: 매칭 시스템

| 기능 | 우선순위 | 설명 |
|------|----------|------|
| 기업 프로파일 관리 | 높음 | 업종, 규모, AI 도입 목적 등록 |
| 적합도 점수 산출 | 높음 | 기업 요구-전문가 역량 매칭 점수 |
| 추천 알고리즘 | 높음 | sentence-transformers 기반 유사도 분석 |
| 매칭 이력 관리 | 중간 | 매칭 결과, 컨설팅 수행 이력 |
| 만족도 피드백 반영 | 낮음 | 만족도 점수 기반 추천 가중치 조정 |

---

## 부록

### A. 환경 변수

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ax_eval

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Server
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### B. 데이터베이스 마이그레이션

```bash
cd backend

# 새 마이그레이션 생성
poetry run alembic revision --autogenerate -m "migration message"

# 마이그레이션 적용
poetry run alembic upgrade head

# 마이그레이션 롤백
poetry run alembic downgrade -1

# 마이그레이션 이력 조회
poetry run alembic history
```

### C. 개발 서버 실행

#### Backend
```bash
cd backend
poetry install
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

**문서 작성:** Claude Code (Anthropic)
**프로젝트:** 스마트공장 AX 코칭단 평가 시스템
**최종 수정일:** 2026-01-10
