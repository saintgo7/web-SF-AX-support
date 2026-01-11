# AX 코칭단 평가 시스템 - 기획 문서

## 개요
스마트팩토리 AX(AI Transformation) 전환을 위한 기업-전문가 매칭 및 코칭 관리 시스템의 종합 기획 문서입니다.

## 문서 목록

| 문서 | 설명 | 파일 |
|------|------|------|
| PRD | 제품 요구사항 정의서 | [01_PRD.md](01_PRD.md) |
| TRD | 기술 요구사항 정의서 | [02_TRD.md](02_TRD.md) |
| User Flow | 사용자 흐름도 | [03_USER_FLOW.md](03_USER_FLOW.md) |
| Database Design | 데이터베이스 설계 | [04_DATABASE_DESIGN.md](04_DATABASE_DESIGN.md) |
| Design System | 디자인 시스템 | [05_DESIGN_SYSTEM.md](05_DESIGN_SYSTEM.md) |
| TASKS | 작업 목록 및 진행현황 | [06_TASKS.md](06_TASKS.md) |
| Coding Convention | 코딩 컨벤션 | [07_CODING_CONVENTION.md](07_CODING_CONVENTION.md) |

## 핵심 기능

1. **전문가 평가 시스템**
   - 문항 관리 (객관식/주관식/서술형)
   - AI 채점 지원
   - 점수 집계 및 시각화

2. **기업-전문가 매칭**
   - AI 기반 추천 알고리즘
   - 가중치 기반 점수 (전문분야 40%, 평가 20%, 자격 15%, 경력 15%, 가용성 10%)
   - 매칭 이력 관리

3. **보고서 생성**
   - PDF 보고서 (한글 지원)
   - 전문가별 평가 보고서
   - 시스템 통계 보고서

## 기술 스택

- **Backend**: FastAPI, SQLAlchemy 2.0, PostgreSQL
- **Frontend**: Next.js 14, TypeScript, React Query
- **ML**: sentence-transformers (한국어 지원)
- **PDF**: WeasyPrint

## 생성일
2026-01-11
