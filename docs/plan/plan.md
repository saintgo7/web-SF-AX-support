# 스마트공장 AX 코칭단 평가 시스템 개발 계획서

**문서번호:** AX-DEV-PLAN-2025-001
**버전:** 1.0
**작성일:** 2025-01-08
**프로젝트명:** 스마트공장 AX 코칭단 전문가 평가 및 매칭 시스템

---

## 목차

1. [프로젝트 개요서](#1-프로젝트-개요서)
2. [요구사항 정의서 (SRS)](#2-요구사항-정의서-srs)
3. [시스템 아키텍처 설계서](#3-시스템-아키텍처-설계서)
4. [데이터베이스 설계서](#4-데이터베이스-설계서)
5. [API 설계서](#5-api-설계서)
6. [UI/UX 설계서](#6-uiux-설계서)
7. [개발 일정 계획서](#7-개발-일정-계획서)
8. [테스트 계획서](#8-테스트-계획서)
9. [배포 및 운영 계획서](#9-배포-및-운영-계획서)

---

# 1. 프로젝트 개요서

## 1.1 프로젝트 배경

중소벤처기업부의 "제조DX멘토단 활용지원사업 AX기획지원"은 국내 중소/중견 제조기업의 AI 기반 스마트공장 도입을 지원하는 사업이다. 본 시스템은 AX 코칭단 전문가 100명 내외를 선정하고, 200개 내외의 수요기업과 효과적으로 매칭하기 위한 평가 및 관리 플랫폼이다.

## 1.2 프로젝트 목표

| 구분 | 목표 | 성과지표 |
|------|------|----------|
| 정량목표 | 전문가 평가 자동화율 80% 이상 | 수동 검토 대비 처리시간 50% 단축 |
| 정성목표 | 객관적/공정한 전문가 선정 | 평가위원 만족도 4.0/5.0 이상 |
| 운영목표 | 전문가-기업 매칭 정확도 향상 | 매칭 성공률 85% 이상 |

## 1.3 프로젝트 범위

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

[Scope-Out]
  ├─ 스마트공장 사업관리시스템(smart-factory.kr) 연동
  ├─ 결제/정산 시스템
  └─ 기존 레거시 시스템 마이그레이션
```

## 1.4 이해관계자

| 역할 | 조직 | 책임 |
|------|------|------|
| 발주처 | 중소벤처기업부 | 사업 총괄, 정책 결정 |
| 추진기관 | 스마트제조혁신추진단 | 사업 운영, 성과 관리 |
| 운영기관 | (지정기관) | 시스템 운영, 전문가 관리 |
| 평가위원 | 산학연 전문가 | 전문가 선정 평가 수행 |
| 신청자 | AX 전문가 후보 | 등록 신청, 평가 응시 |
| 수요기업 | 중소/중견 제조기업 | 컨설팅 수혜, 만족도 평가 |

## 1.5 기술 스택 개요

| 계층 | 기술 | 선정 사유 |
|------|------|-----------|
| Frontend | React 18 + TypeScript | 컴포넌트 재사용성, 타입 안정성 |
| Backend | FastAPI (Python 3.11) | 비동기 처리, AI/ML 라이브러리 연동 |
| Database | PostgreSQL 15 | JSONB 지원, 복잡한 쿼리 최적화 |
| Cache | Redis 7 | 세션 관리, 실시간 데이터 캐싱 |
| AI/ML | scikit-learn, sentence-transformers | 매칭 알고리즘, 텍스트 유사도 분석 |
| Infra | Docker + Kubernetes | 컨테이너화, 오토스케일링 |
| Cloud | AWS (EKS, RDS, S3) | 안정성, 확장성, 관리형 서비스 |

---

# 2. 요구사항 정의서 (SRS)

## 2.1 기능 요구사항

### 2.1.1 [A] 전문가 자격요건 자동 검증

| ID | 요구사항 | 우선순위 | 상세 설명 |
|----|----------|----------|-----------|
| FR-A01 | 학위 조건 검증 | 필수 | 박사/석사/학사 학위 보유 여부 및 해당분야 일치 확인 |
| FR-A02 | 경력 조건 검증 | 필수 | 학위별 필요 경력년수 충족 여부 (박사 3년, 석사 5년, 학사 7년) |
| FR-A03 | 직급 조건 검증 | 필수 | 부장급 이상 또는 대학 전임강사 이상 여부 확인 |
| FR-A04 | 기술자격 검증 | 선택 | 엔지니어링산업진흥법 특급기술자 이상 여부 |
| FR-A05 | 전문분야 매칭 | 필수 | ML/DL/CV/컴퓨팅플랫폼/데이터인텔리전스 분류 |
| FR-A06 | 자동 판정 결과 생성 | 필수 | 적합/부적합/검토필요 3단계 판정 |

**자격요건 판정 로직:**

```
IF (박사학위 AND 관련분야 AND 경력>=3년) THEN 적합
ELSE IF (석사학위 AND 관련분야 AND 경력>=5년) THEN 적합
ELSE IF (학사학위 AND 관련분야 AND 경력>=7년) THEN 적합
ELSE IF (부장급이상 OR 전임강사이상 OR 특급기술자이상) THEN 적합
ELSE 부적합
```

### 2.1.2 [B] AX 기능별 질의응답 시스템

| ID | 요구사항 | 우선순위 | 상세 설명 |
|----|----------|----------|-----------|
| FR-B01 | 분야별 문항 DB 관리 | 필수 | 6개 전문분야별 평가문항 CRUD |
| FR-B02 | 문항 유형 지원 | 필수 | 객관식(단일/다중), 주관식(단답/서술), 파일첨부 |
| FR-B03 | 동적 문항 출제 | 필수 | 신청자 전문분야 기반 문항 자동 구성 |
| FR-B04 | 응답 저장 및 이력관리 | 필수 | 응답 버전관리, 수정이력 추적 |
| FR-B05 | 객관식 자동채점 | 필수 | 정답 매칭 기반 즉시 점수 산출 |
| FR-B06 | 주관식 AI 보조채점 | 선택 | 키워드 추출, 유사도 분석 기반 예비점수 |
| FR-B07 | 평가위원 채점 인터페이스 | 필수 | 주관식 수동채점, 코멘트 작성 기능 |

### 2.1.3 [C] 평가 점수 산정 및 리포트

| ID | 요구사항 | 우선순위 | 상세 설명 |
|----|----------|----------|-----------|
| FR-C01 | 가중치 설정 관리 | 필수 | 평가항목별 가중치 동적 설정 |
| FR-C02 | 종합점수 산출 | 필수 | 가중치 적용 100점 만점 환산 |
| FR-C03 | 순위 산정 | 필수 | 동점자 처리 규칙 적용 순위 결정 |
| FR-C04 | 개인별 평가 리포트 | 필수 | 영역별 점수, 강점/약점 분석 |
| FR-C05 | 종합 통계 리포트 | 필수 | 전체 응시자 분포, 합격선 분석 |
| FR-C06 | 리포트 PDF 출력 | 필수 | 공식 양식 기반 PDF 자동 생성 |

**평가 가중치 기본값:**

| 평가항목 | 가중치 | 배점 |
|----------|--------|------|
| 학력/자격사항 | 15% | 15점 |
| 경력사항 | 20% | 20점 |
| 전문분야 역량 | 35% | 35점 |
| 컨설팅 수행계획 | 20% | 20점 |
| 연구/논문 실적 | 10% | 10점 |
| **합계** | **100%** | **100점** |

### 2.1.4 [D] 수요기업 매칭 지원

| ID | 요구사항 | 우선순위 | 상세 설명 |
|----|----------|----------|-----------|
| FR-D01 | 기업 프로파일 관리 | 필수 | 업종, 규모, AI도입목적, 현황 등록 |
| FR-D02 | 전문가 프로파일 관리 | 필수 | 전문분야, 경력, 컨설팅 이력 관리 |
| FR-D03 | 적합도 점수 산출 | 필수 | 기업요구-전문가역량 매칭 점수 |
| FR-D04 | 추천 전문가 리스트 | 필수 | 적합도 순위 기반 Top-N 추천 |
| FR-D05 | 매칭 이력 관리 | 필수 | 매칭 결과, 컨설팅 수행 이력 |
| FR-D06 | 만족도 피드백 반영 | 선택 | 만족도 점수 기반 추천 가중치 조정 |

---

# 3. 시스템 아키텍처 설계서

## 3.1 마이크로서비스 구성

| 서비스명 | 역할 | 기술 | 포트 |
|----------|------|------|------|
| api-gateway | 라우팅, 인증, 레이트리밋 | FastAPI + Redis | 8000 |
| auth-service | 인증/인가, 세션관리 | FastAPI + JWT | 8001 |
| evaluation-service | 평가문항, 채점, 점수산정 | FastAPI + scikit-learn | 8002 |
| matching-service | 전문가-기업 매칭 | FastAPI + sentence-transformers | 8003 |
| report-service | 리포트 생성, PDF 출력 | FastAPI + WeasyPrint | 8004 |
| notification-service | 이메일/SMS 알림 | FastAPI + Celery | 8005 |
| file-service | 파일 업로드/다운로드 | FastAPI + boto3 | 8006 |

## 3.2 Frontend 아키텍처

```
src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── (auth)/
│   │   ├── login/
│   │   └── register/
│   ├── (applicant)/
│   │   ├── application/
│   │   ├── evaluation/
│   │   └── result/
│   ├── (evaluator)/
│   │   ├── dashboard/
│   │   ├── scoring/
│   │   └── review/
│   ├── (admin)/
│   │   ├── questions/
│   │   ├── matching/
│   │   └── reports/
│   └── api/
├── components/
│   ├── ui/           # 기본 UI 컴포넌트
│   ├── forms/        # 폼 컴포넌트
│   ├── tables/       # 테이블 컴포넌트
│   └── charts/       # 차트 컴포넌트
├── hooks/
├── lib/
├── store/            # Zustand 상태관리
└── types/
```

---

# 4. 데이터베이스 설계서

## 4.1 주요 테이블 상세

### 4.1.1 users (사용자)

| 컬럼명 | 데이터타입 | 제약조건 | 설명 |
|--------|------------|----------|------|
| user_id | UUID | PK | 사용자 고유식별자 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 이메일 (로그인 ID) |
| password_hash | VARCHAR(255) | NOT NULL | 비밀번호 해시 (bcrypt) |
| name | VARCHAR(100) | NOT NULL | 성명 |
| phone | VARCHAR(20) | | 연락처 |
| role | ENUM | NOT NULL | APPLICANT, EVALUATOR, OPERATOR, ADMIN |
| status | ENUM | NOT NULL | ACTIVE, INACTIVE, SUSPENDED |
| created_at | TIMESTAMP | NOT NULL | 생성일시 |
| updated_at | TIMESTAMP | | 수정일시 |

### 4.1.2 experts (전문가)

| 컬럼명 | 데이터타입 | 제약조건 | 설명 |
|--------|------------|----------|------|
| expert_id | UUID | PK | 전문가 고유식별자 |
| user_id | UUID | FK, UNIQUE | 사용자 참조 |
| degree_type | ENUM | | PHD, MASTER, BACHELOR |
| degree_field | VARCHAR(100) | | 학위 전공분야 |
| career_years | INTEGER | | 관련분야 경력년수 |
| position | VARCHAR(100) | | 직급/직위 |
| org_name | VARCHAR(200) | | 소속기관명 |
| org_type | ENUM | | UNIVERSITY, COMPANY, RESEARCH, OTHER |
| specialties | JSONB | | 전문분야 배열 |
| certifications | JSONB | | 자격증 정보 |
| qualification_status | ENUM | | PENDING, QUALIFIED, DISQUALIFIED |
| qualification_note | TEXT | | 자격검증 비고 |

### 4.1.3 questions (평가문항)

| 컬럼명 | 데이터타입 | 제약조건 | 설명 |
|--------|------------|----------|------|
| question_id | UUID | PK | 문항 고유식별자 |
| category_id | UUID | FK | 평가영역 참조 |
| q_type | ENUM | NOT NULL | SINGLE, MULTIPLE, SHORT, ESSAY, FILE |
| content | TEXT | NOT NULL | 문항 내용 |
| options | JSONB | | 객관식 선택지 |
| correct_answer | JSONB | | 정답 (객관식용) |
| scoring_rubric | JSONB | | 채점 기준표 (주관식용) |
| max_score | INTEGER | NOT NULL | 배점 |
| difficulty | ENUM | | EASY, MEDIUM, HARD |
| target_specialties | JSONB | | 출제 대상 전문분야 |
| is_active | BOOLEAN | DEFAULT TRUE | 활성화 여부 |

---

# 5. API 설계서

## 5.1 API 개요

| 항목 | 내용 |
|------|------|
| Base URL | https://api.ax-eval.smartfactory.kr/v1 |
| 인증방식 | Bearer Token (JWT) |
| 응답형식 | application/json |
| 에러형식 | RFC 7807 Problem Details |

## 5.2 주요 API Endpoints

### 인증 API
- POST /auth/login - 사용자 로그인
- POST /auth/register - 사용자 회원가입
- POST /auth/refresh - 토큰 갱신
- POST /auth/logout - 로그아웃

### 전문가 관리 API
- GET /experts - 전문가 목록 조회
- POST /experts - 전문가 등록
- GET /experts/{id} - 전문가 상세 조회
- PUT /experts/{id} - 전문가 정보 수정
- POST /experts/qualification/verify - 자격검증

### 평가 API
- GET /evaluation/questions - 평가문항 조회
- POST /evaluation/answers - 응답 제출
- POST /evaluation/score - 채점 수행
- GET /evaluation/results/{id} - 결과 조회

### 매칭 API
- POST /matching/recommend - 전문가 추천
- POST /matching/assign - 매칭 확정
- GET /matching/{id} - 매칭 상세 조회

---

# 6. UI/UX 설계서

## 6.1 사용자 역할별 화면 구성

### 신청자 (Applicant)
- 대시보드
- 신청서 작성
- 평가응시
- 결과조회

### 평가위원 (Evaluator)
- 대시보드
- 채점수행
- 채점완료

### 운영자/관리자 (Operator/Admin)
- 대시보드
- 전문가관리
- 문항관리
- 매칭관리
- 리포트
- 시스템설정

---

# 7. 개발 일정 계획서

## 7.1 프로젝트 일정 개요

| 단계 | 기간 | 산출물 |
|------|------|--------|
| 1단계: 분석/설계 | 4주 | 요구사항명세서, 설계서 |
| 2단계: 개발 | 12주 | 소스코드, 단위테스트 |
| 3단계: 테스트 | 4주 | 테스트 결과서, 수정사항 |
| 4단계: 배포/안정화 | 2주 | 운영환경, 매뉴얼 |
| **총 기간** | **22주** | |

---

# 8. 테스트 계획서

## 8.1 테스트 전략

| 테스트 유형 | 목적 | 도구 | 기준 |
|-------------|------|------|------|
| 단위 테스트 | 개별 함수/모듈 검증 | pytest, Jest | 커버리지 80% 이상 |
| 통합 테스트 | 모듈간 연동 검증 | pytest, Postman | 주요 시나리오 100% |
| E2E 테스트 | 사용자 시나리오 검증 | Playwright | Critical Path 100% |
| 성능 테스트 | 부하/응답시간 검증 | k6, Locust | SLA 충족 |
| 보안 테스트 | 취약점 검증 | OWASP ZAP | Critical 0건 |

---

# 9. 배포 및 운영 계획서

## 9.1 배포 아키텍처

AWS 기반 클라우드 인프라 (EKS, RDS, S3, ElastiCache)

## 9.2 CI/CD 파이프라인

GitHub Actions → Build & Test → ECR Push → ArgoCD Deploy

---

**문서 끝**
