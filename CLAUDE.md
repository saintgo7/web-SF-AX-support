# AX 코칭단 관리 시스템 (SmartFactory AX Support)

## 프로젝트 구조
```
/frontend          - Next.js 14 프론트엔드
/backend           - FastAPI 백엔드 (Python)
/.claude           - Claude 설정 및 개발 로그
```

## 세션 시작 시 필수 확인
**반드시 `.claude/DEV_LOG.md`를 읽고 최근 개발 이력을 사용자에게 알려주세요.**

개발 로그 경로: `/Users/saint/01_DEV/26-SmartFactotyAX_Support/.claude/DEV_LOG.md`

## 기술 스택
- **Frontend**: Next.js 14, TypeScript, TailwindCSS, Zustand
- **Backend**: FastAPI, SQLAlchemy, Supabase
- **Database**: PostgreSQL (Supabase)

## 주요 기능
- 평가 위원 관리
- 컨설턴트-기업 매칭
- 보고서 작성/관리 (컨설팅/평가/요약)
- PDF 내보내기

## 개발 서버
```bash
cd frontend && npm run dev  # http://localhost:3000
cd backend && uvicorn main:app --reload  # http://localhost:8000
```

## 코딩 컨벤션
- 한국어 주석 사용
- 컴포넌트는 `src/components/` 하위에 도메인별 폴더로 구성
- API 호출은 `src/lib/api/` 하위에 도메인별 파일로 구성
- 유틸리티는 `src/lib/utils/` 하위에 기능별 파일로 구성

## Git 워크플로우
- main 브랜치에 직접 커밋
- 커밋 메시지: `type: 한글 설명` 형식
- Co-Authored-By 태그 포함
