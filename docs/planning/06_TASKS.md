# TASKS: AX 코칭단 평가 시스템
## 개발 작업 목록 및 진행 현황

---

## 1. 프로젝트 개요

### 1.1 스프린트 구성
| 스프린트 | 기간 | 주요 목표 | 상태 |
|---------|------|----------|------|
| Sprint 1-3 | 완료 | 기본 시스템 구축 | ✅ 완료 |
| Sprint 4 | 완료 | Enhanced Scoring | ✅ 완료 |
| Sprint 5 | 완료 | Reports & PDF | ✅ 완료 |
| Sprint 6 | 완료 | Matching Algorithm | ✅ 완료 |
| Sprint 7+ | 예정 | 고도화 | ⏳ 계획중 |

---

## 2. 완료된 작업

### 2.1 Sprint 1-3: 기본 시스템 (✅ 완료)

#### Backend
- [x] FastAPI 프로젝트 구조 설정
- [x] PostgreSQL + SQLAlchemy 2.0 설정
- [x] User 모델 및 인증 API (JWT)
- [x] Expert 모델 및 CRUD API
- [x] Question/Category 모델 및 API
- [x] Answer 모델 및 API
- [x] Application 모델 및 API
- [x] Company/Demand 모델 및 API
- [x] Matching 기본 CRUD API

#### Frontend
- [x] Next.js 14 App Router 설정
- [x] TypeScript 구성
- [x] Tailwind CSS 설정
- [x] 인증 페이지 (Login/Register)
- [x] Admin 레이아웃 및 대시보드
- [x] 전문가 관리 페이지
- [x] 문항 관리 페이지
- [x] Evaluator 레이아웃
- [x] Applicant 레이아웃

### 2.2 Sprint 4: Enhanced Scoring (✅ 완료)

#### Backend
- [x] ExpertScore 모델 생성
  - `backend/src/app/models/expert_score.py`
- [x] Score 스키마 정의
  - `backend/src/app/schemas/score.py`
- [x] GradingService 개선
  - AI 채점 기능
  - 점수 집계 기능
- [x] Evaluation API 확장
  - `POST /grade/ai`
  - `GET /scores/{expert_id}`
  - `GET /statistics`
- [x] 마이그레이션: expert_scores 테이블

#### Frontend
- [x] Evaluator 대시보드
  - `frontend/src/app/evaluator/dashboard/page.tsx`
- [x] 채점 인터페이스 개선
  - AI 점수 추천 표시
  - 루브릭 가이드 패널
- [x] Score 타입 정의
  - `frontend/src/types/score.ts`
- [x] Score API 클라이언트
  - `frontend/src/lib/api/scores.ts`

### 2.3 Sprint 5: Reports & PDF (✅ 완료)

#### Backend
- [x] Report 모델 생성
  - `backend/src/app/models/report.py`
- [x] Report 스키마 정의
  - `backend/src/app/schemas/report.py`
- [x] PDF 서비스 구현
  - `backend/src/app/services/pdf_service.py`
  - WeasyPrint 기반
  - 한글 폰트 지원 (나눔고딕)
- [x] Reports API 확장
  - `POST /generate/expert/{expert_id}`
  - `POST /generate/summary`
  - `GET /download/{report_id}`
- [x] 마이그레이션: reports 테이블

#### Frontend
- [x] 보고서 관리 페이지 개선
  - `frontend/src/app/admin/reports/page.tsx`
- [x] 차트 컴포넌트
  - `frontend/src/components/charts/ScoreDistribution.tsx`
  - `frontend/src/components/charts/CategoryBreakdown.tsx`
  - `frontend/src/components/charts/TrendChart.tsx`
- [x] Report 타입 정의
  - `frontend/src/types/report.ts`
- [x] Reports API 확장

### 2.4 Sprint 6: Matching Algorithm (✅ 완료)

#### Backend
- [x] MatchingService 생성
  - `backend/src/app/services/matching_service.py`
  - 가중치 기반 점수 계산
    - 전문분야: 40%
    - 평가성과: 20%
    - 자격검증: 15%
    - 경력: 15%
    - 가용성: 10%
- [x] ML 모듈 생성
  - `backend/src/app/ml/similarity.py`
  - sentence-transformers 기반 의미 유사도
- [x] Matching 스키마 확장
  - MatchScoreBreakdown
  - RecommendedCandidate
  - MatchingAnalytics
- [x] Matchings API 확장
  - `POST /recommend`
  - `GET /compatibility/{expert_id}/{demand_id}`
  - `GET /analytics`

#### Frontend
- [x] Matching 타입 재정의
  - `frontend/src/types/matching.ts` (백엔드 정렬)
- [x] Matching API 확장
  - `frontend/src/lib/api/matchings.ts`
- [x] useMatching 훅 생성
  - `frontend/src/hooks/useMatching.ts`
- [x] RecommendationCard 컴포넌트
  - `frontend/src/components/matching/RecommendationCard.tsx`
- [x] 매칭 페이지 개선 (3탭)
  - 목록 / AI 추천 / 분석

---

## 3. 진행 예정 작업

### 3.1 Sprint 7: 알림 시스템 (⏳ 계획중)

#### Backend
- [ ] Notification 모델 생성
- [ ] 이메일 서비스 구현
- [ ] WebSocket 실시간 알림
- [ ] 알림 설정 API

#### Frontend
- [ ] 알림 드롭다운 컴포넌트
- [ ] 알림 설정 페이지
- [ ] 토스트 알림 시스템

### 3.2 Sprint 8: 모바일 최적화 (⏳ 계획중)

#### Frontend
- [ ] 반응형 레이아웃 개선
- [ ] 모바일 네비게이션
- [ ] 터치 인터랙션 최적화
- [ ] PWA 설정

### 3.3 Sprint 9: 성능 최적화 (⏳ 계획중)

#### Backend
- [ ] Redis 캐싱 적용
- [ ] 쿼리 최적화
- [ ] 페이지네이션 개선
- [ ] 인덱스 튜닝

#### Frontend
- [ ] 코드 스플리팅
- [ ] 이미지 최적화
- [ ] 가상 스크롤 적용
- [ ] 번들 사이즈 최적화

---

## 4. 기술 부채

### 4.1 우선순위 높음
- [ ] 단위 테스트 커버리지 확대 (현재 ~30%)
- [ ] API 문서화 개선 (OpenAPI)
- [ ] 에러 핸들링 통일

### 4.2 우선순위 중간
- [ ] 로깅 시스템 고도화
- [ ] 환경변수 관리 개선
- [ ] CI/CD 파이프라인 구축

### 4.3 우선순위 낮음
- [ ] 코드 리팩토링
- [ ] 레거시 코드 정리
- [ ] 문서화 업데이트

---

## 5. 버그 트래킹

### 5.1 알려진 이슈
| ID | 제목 | 우선순위 | 상태 |
|----|------|---------|------|
| - | 현재 알려진 버그 없음 | - | - |

### 5.2 해결된 이슈
| ID | 제목 | 해결일 |
|----|------|--------|
| #001 | 타입 불일치 (matching.ts) | 2026-01-10 |
| #002 | PDF 한글 깨짐 | 2026-01-10 |

---

## 6. 마일스톤

### 6.1 MVP (✅ 완료)
- 기본 인증 시스템
- 전문가/문항 관리
- 평가 시스템

### 6.2 Phase 2 (✅ 완료)
- AI 채점 지원
- 보고서 생성
- 지능형 매칭

### 6.3 Phase 3 (⏳ 계획중)
- 실시간 알림
- 모바일 최적화
- 외부 연동 API

---

## 7. 파일 구조 (현재)

### 7.1 Backend
```
backend/src/app/
├── api/v1/
│   ├── auth.py
│   ├── users.py
│   ├── experts.py
│   ├── evaluation.py
│   ├── matchings.py      # Sprint 6 확장
│   └── reports.py        # Sprint 5 확장
├── models/
│   ├── user.py
│   ├── expert.py
│   ├── question.py
│   ├── answer.py
│   ├── company.py
│   ├── matching.py
│   ├── expert_score.py   # Sprint 4
│   └── report.py         # Sprint 5
├── schemas/
│   ├── matching.py       # Sprint 6 확장
│   ├── score.py          # Sprint 4
│   └── report.py         # Sprint 5
├── services/
│   ├── grading_service.py
│   ├── matching_service.py  # Sprint 6
│   └── pdf_service.py       # Sprint 5
└── ml/
    └── similarity.py        # Sprint 6
```

### 7.2 Frontend
```
frontend/src/
├── app/
│   ├── admin/
│   │   ├── dashboard/
│   │   ├── experts/
│   │   ├── questions/
│   │   ├── matching/     # Sprint 6 개선
│   │   └── reports/      # Sprint 5 개선
│   ├── evaluator/
│   │   ├── dashboard/    # Sprint 4
│   │   ├── pending/
│   │   └── history/
│   └── applicant/
├── components/
│   ├── charts/           # Sprint 5
│   └── matching/         # Sprint 6
├── hooks/
│   └── useMatching.ts    # Sprint 6
├── lib/api/
│   ├── matchings.ts      # Sprint 6 확장
│   ├── scores.ts         # Sprint 4
│   └── reports.ts        # Sprint 5 확장
└── types/
    ├── matching.ts       # Sprint 6 재정의
    ├── score.ts          # Sprint 4
    └── report.ts         # Sprint 5
```

---

## 8. 다음 단계

### 8.1 즉시 진행 가능
1. 테스트 커버리지 확대
2. API 문서 개선
3. 사용자 가이드 작성

### 8.2 계획 필요
1. 알림 시스템 설계
2. 모바일 UI 설계
3. 외부 연동 API 설계

### 8.3 결정 필요
1. 배포 환경 (AWS/GCP/On-premise)
2. 모니터링 도구 선정
3. 백업 정책 수립
