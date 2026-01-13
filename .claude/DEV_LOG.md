# AX 코칭단 관리 시스템 - 개발 로그

## 프로젝트 개요
- **프로젝트명**: SmartFactory AX Support (AX 코칭단 관리 시스템)
- **저장소**: https://github.com/saintgo7/web-SF-AX-support.git
- **기술 스택**: Next.js 14, TypeScript, TailwindCSS, Supabase

---

## 최근 개발 이력

### 2026-01-13: PDF 내보내기 기능 구현
**커밋**: `7c1bfe5` - feat: PDF 내보내기 기능 구현

#### 구현 내용
1. **라이브러리 설치**
   - jspdf, html2canvas 추가
   - @types/html2canvas (타입 지원)

2. **신규 파일**
   - `src/lib/utils/pdf.ts`: PDF 생성 유틸리티
     - `generatePDF()`: HTML 요소를 PDF로 변환
     - `sanitizeFilename()`: 파일명 정규화
     - `generateReportFilename()`: 보고서 파일명 생성
   - `src/components/report/ReportPrintLayout.tsx`: A4 프린트 레이아웃
     - 컨설팅/평가/요약 보고서 유형별 렌더링
     - 헤더, 기본정보, 본문, 푸터 구성

3. **수정 파일**
   - `src/app/evaluator/reports/[id]/page.tsx`
     - PDF 다운로드 핸들러 (useCallback)
     - URL 쿼리 파라미터(`?action=pdf`) 자동 다운로드
   - `src/app/evaluator/reports/page.tsx`
     - 목록에서 PDF 버튼 클릭 시 상세 페이지로 이동

#### 동작 방식
- APPROVED 상태 보고서만 PDF 다운로드 가능
- 숨겨진 DOM에 프린트 레이아웃 렌더링 후 html2canvas로 캡처
- jsPDF로 A4 PDF 생성 및 다운로드

---

### 2026-01-12: 보고서 작성 상세 페이지 구현
**커밋**: `67c9546` - feat: 보고서 작성 상세 페이지 구현

#### 구현 내용
- 보고서 유형별 폼 (컨설팅/평가/요약)
- 편집/미리보기 탭
- 상태별 버튼 (임시저장, 제출, PDF 다운로드)
- Badge 컴포넌트 primary/secondary variant 추가

---

## 알려진 이슈

### Next.js 빌드 경고
- `/auth/login`, `/auth/reset-password` 페이지에서 `useSearchParams()` Suspense 바운더리 필요
- 해결: `dynamic = 'force-dynamic'` 또는 Suspense로 감싸기

### Auth 하이드레이션 타이밍
- Zustand persist가 localStorage 읽기 전 리다이렉트 발생 가능
- 해결 필요: 로딩 상태 추가 또는 하이드레이션 완료 대기

---

## 다음 개발 예정
- [ ] 보고서 API 연동 (Mock → 실제 API)
- [ ] Auth 페이지 Suspense 바운더리 적용
- [ ] 관리자 대시보드 기능 확장

---

## 주요 경로

| 경로 | 설명 |
|------|------|
| `/evaluator/reports` | 보고서 목록 |
| `/evaluator/reports/[id]` | 보고서 상세/편집 |
| `/evaluator/reports/new` | 새 보고서 작성 |
| `/admin/matching` | 매칭 관리 |

---

*마지막 업데이트: 2026-01-13*
