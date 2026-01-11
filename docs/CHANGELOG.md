# Changelog

모든 주요 변경 사항이 이 파일에 기록됩니다.

---

## [2026-01-11] - Table 컴포넌트 버그 수정

### 커밋 정보
- **커밋 해시**: `cd818d8`
- **커밋 메시지**: `fix: Table 컴포넌트 사용 패턴 수정 (evaluator 페이지들)`

### 수정 내용
- 잘못된 Compound Component 패턴(`Table.Head`, `Table.Row` 등)을 올바른 props 기반 패턴으로 수정
- `columns`, `data`, `keyField` props 사용 패턴으로 통일
- `Column<T>` 타입 정의 추가

### 수정된 파일
- `frontend/src/app/evaluator/consultants/page.tsx`
- `frontend/src/app/evaluator/matching/page.tsx`
- `frontend/src/app/evaluator/reports/page.tsx`
- `frontend/src/app/evaluator/grading/page.tsx`

---

## [2026-01-11] - 컨설팅 위원 중심 UI/UX 개편

### 커밋 정보
- **커밋 해시**: `1c850dd`
- **커밋 메시지**: `refactor: 컨설팅 위원 중심 시스템으로 UI/UX 개편`
- **변경 파일**: 16개 (수정 12개, 신규 4개)
- **변경 라인**: +1,030 / -56

---

### 주요 변경 사항

#### 1. 시스템명 및 용어 변경

| 변경 전 | 변경 후 |
|---------|---------|
| AX Coaching Evaluation | **AX 코칭단 관리 시스템** |
| 전문가 (Expert) | **컨설턴트** |
| 평가위원 (Evaluator) | **컨설팅 위원** |
| 전문가 관리 | **컨설턴트 관리** |

#### 2. 컨설팅 위원 메뉴 재구성

**기존 메뉴 (3개)**
```
├── 대시보드
├── 채점 대기
└── 채점 완료
```

**신규 메뉴 (5개)**
```
├── 대시보드
├── 컨설턴트 현황  ← NEW
├── 매칭 현황      ← NEW
├── 보고서 작성    ← NEW (핵심 기능)
└── 평가 채점      ← NEW (대기/완료 통합)
```

#### 3. 신규 페이지 상세

| 페이지 경로 | 기능 설명 |
|------------|----------|
| `/evaluator/consultants` | AX 컨설턴트 현황 조회 (통계 카드, 필터, 테이블) |
| `/evaluator/matching` | 기업-컨설턴트 매칭 현황 (상태별 필터, 매칭점수 표시) |
| `/evaluator/reports` | **보고서 작성/관리** - 컨설팅/평가/요약 보고서 생성 |
| `/evaluator/grading` | 평가 채점 (대기/완료 탭 통합, 진행률 표시) |

---

### 수정된 파일 목록

#### 레이아웃 컴포넌트
- `frontend/src/components/layout/Header.tsx` - 시스템명, 메뉴 구조 변경
- `frontend/src/components/layout/Sidebar.tsx` - 컨설팅 위원 메뉴 재구성

#### 공통 페이지
- `frontend/src/app/layout.tsx` - 메타데이터 업데이트
- `frontend/src/app/page.tsx` - 홈 화면 시스템명 변경

#### Admin 페이지 (용어 변경: 전문가 → 컨설턴트)
- `frontend/src/app/admin/dashboard/page.tsx`
- `frontend/src/app/admin/experts/page.tsx`
- `frontend/src/app/admin/matching/page.tsx`
- `frontend/src/app/admin/reports/page.tsx`

#### Evaluator 페이지
- `frontend/src/app/evaluator/dashboard/page.tsx` - 제목/링크 업데이트
- `frontend/src/app/evaluator/pending/page.tsx` - 용어 변경

#### Applicant 페이지 (용어 변경)
- `frontend/src/app/applicant/dashboard/page.tsx`
- `frontend/src/app/applicant/application/page.tsx`

---

### 기술 노트

- **Mock 데이터 사용**: 신규 페이지들은 현재 Mock 데이터로 구현됨
- **백엔드 연동 필요**: 실제 API 연동 작업 추후 진행 필요
- **기존 pending/history 페이지**: 유지됨 (grading 페이지로 기능 통합 예정)

---

## [2026-01-11] - 기획 문서 추가

### 커밋 정보
- **커밋 해시**: `9ba63e0`
- **커밋 메시지**: `docs: Add comprehensive planning documents`

### 추가된 문서
- `docs/planning/01_PRD.md` - Product Requirements Document
- `docs/planning/02_TRD.md` - Technical Requirements Document
- `docs/planning/03_USER_FLOW.md` - 사용자 흐름 다이어그램
- `docs/planning/04_DATABASE_DESIGN.md` - 데이터베이스 설계
- `docs/planning/05_DESIGN_SYSTEM.md` - 디자인 시스템
- `docs/planning/06_TASKS.md` - 스프린트 진행 현황
- `docs/planning/07_CODING_CONVENTION.md` - 코딩 컨벤션

---

## [2026-01-10] - Sprint 4-6 기능 구현

### 커밋 정보
- **커밋 해시**: `f388896`
- **커밋 메시지**: `feat: Implement Sprint 4-6 features for AX Expert Evaluation System`

### 구현된 기능
- **Sprint 4**: Enhanced Scoring System (ExpertScore, AI 채점)
- **Sprint 5**: Reports & PDF Generation (WeasyPrint, 한글 지원)
- **Sprint 6**: Intelligent Matching Algorithm (가중치 기반 매칭, Sentence-Transformers)

---

## 다음 작업 (예정)

1. [ ] 신규 페이지 백엔드 API 연동
2. [ ] 보고서 작성 상세 페이지 구현
3. [ ] 컨설턴트 상세 정보 모달/페이지 구현
4. [ ] 매칭 상세 페이지 구현
5. [ ] 기존 pending/history 페이지 → grading 페이지로 마이그레이션
