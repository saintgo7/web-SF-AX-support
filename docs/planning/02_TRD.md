# TRD: AX 코칭단 평가 시스템
## Technical Requirements Document

---

## 1. 시스템 아키텍처

### 1.1 전체 구조
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend       │────▶│   Database      │
│   (Next.js 14)  │     │   (FastAPI)     │     │   (PostgreSQL)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌─────────────────┐
                        │   ML Service    │
                        │ (Sentence-Trans)│
                        └─────────────────┘
```

### 1.2 레이어 구조
```
Frontend (Next.js 14 + TypeScript)
├── App Router (/app)
├── Components (/components)
├── Hooks (/hooks) - React Query
├── Lib (/lib/api) - API 클라이언트
└── Types (/types) - TypeScript 타입

Backend (FastAPI + Python 3.11)
├── API Layer (/api/v1)
├── Services (/services)
├── Models (/models) - SQLAlchemy 2.0
├── Schemas (/schemas) - Pydantic v2
└── ML (/ml) - 머신러닝 모듈
```

---

## 2. 기술 스택

### 2.1 Backend
| 구분 | 기술 | 버전 | 용도 |
|------|------|------|------|
| Framework | FastAPI | 0.104+ | REST API |
| ORM | SQLAlchemy | 2.0+ | 비동기 DB 접근 |
| Validation | Pydantic | 2.0+ | 스키마 검증 |
| Auth | python-jose | 3.3+ | JWT 토큰 |
| Hash | bcrypt | 4.0+ | 비밀번호 해시 |
| PDF | WeasyPrint | 60+ | PDF 생성 |
| ML | sentence-transformers | 2.2+ | 의미 유사도 |
| Task | Celery | 5.3+ | 비동기 작업 |
| Cache | Redis | 4.5+ | 캐싱 |

### 2.2 Frontend
| 구분 | 기술 | 버전 | 용도 |
|------|------|------|------|
| Framework | Next.js | 14+ | React 프레임워크 |
| Language | TypeScript | 5.0+ | 타입 안전성 |
| State | React Query | 5.0+ | 서버 상태 관리 |
| Charts | Recharts | 2.8+ | 차트 시각화 |
| Styling | Tailwind CSS | 3.3+ | CSS 프레임워크 |
| Form | React Hook Form | 7.0+ | 폼 관리 |

### 2.3 Infrastructure
| 구분 | 기술 | 용도 |
|------|------|------|
| Database | PostgreSQL 14+ | 주 데이터베이스 |
| Cache | Redis 7+ | 세션/캐시 |
| Container | Docker | 컨테이너화 |
| Orchestration | Docker Compose | 로컬 개발 |

---

## 3. API 설계

### 3.1 인증 API (`/api/v1/auth`)
```
POST /login          - 로그인 (JWT 발급)
POST /register       - 회원가입
POST /refresh        - 토큰 갱신
POST /logout         - 로그아웃
POST /forgot-password - 비밀번호 찾기
POST /reset-password  - 비밀번호 재설정
```

### 3.2 전문가 API (`/api/v1/experts`)
```
GET    /             - 전문가 목록 조회
GET    /{id}         - 전문가 상세 조회
POST   /             - 전문가 등록
PUT    /{id}         - 전문가 수정
DELETE /{id}         - 전문가 삭제
PUT    /{id}/qualify - 자격 상태 변경
GET    /{id}/stats   - 전문가 통계
```

### 3.3 평가 API (`/api/v1/evaluation`)
```
GET  /questions              - 문항 목록
POST /questions              - 문항 생성
GET  /questions/{id}         - 문항 상세
PUT  /questions/{id}         - 문항 수정
GET  /answers                - 답변 목록
POST /answers                - 답변 제출
POST /answers/{id}/grade     - 채점
POST /grade/ai               - AI 채점
GET  /scores/{expert_id}     - 점수 조회
GET  /statistics             - 채점 통계
```

### 3.4 매칭 API (`/api/v1/matchings`)
```
GET    /                          - 매칭 목록
POST   /                          - 수동 매칭 생성
GET    /{id}                      - 매칭 상세
PUT    /{id}                      - 매칭 수정
DELETE /{id}                      - 매칭 삭제
POST   /{id}/respond              - 전문가 응답
POST   /{id}/feedback             - 기업 피드백
GET    /summary                   - 매칭 요약
POST   /auto-match                - 자동 매칭
POST   /recommend                 - AI 추천 (Sprint 6)
GET    /compatibility/{eid}/{did} - 호환성 검사
GET    /analytics                 - 매칭 분석
```

### 3.5 보고서 API (`/api/v1/reports`)
```
GET  /                            - 보고서 목록
POST /generate/expert/{expert_id} - 전문가 보고서 생성
POST /generate/summary            - 시스템 요약 보고서
GET  /download/{id}               - PDF 다운로드
```

---

## 4. 데이터 모델

### 4.1 주요 엔티티
```
User          - 시스템 사용자 (ADMIN, EVALUATOR, APPLICANT)
Expert        - 전문가 프로필
Question      - 평가 문항
Answer        - 답변 및 채점
ExpertScore   - 점수 집계
Company       - 기업 정보
Demand        - 기업 수요
Matching      - 매칭 기록
Report        - 생성된 보고서
```

### 4.2 관계도
```
User ──1:1──▶ Expert
Expert ──1:N──▶ Answer
Question ──1:N──▶ Answer
Expert ──1:1──▶ ExpertScore
Company ──1:N──▶ Demand
Expert ──N:M──▶ Demand (via Matching)
```

---

## 5. 보안 요구사항

### 5.1 인증/인가
- **JWT**: Access Token (15분) + Refresh Token (7일)
- **RBAC**: 역할별 API 접근 제어
- **비밀번호**: bcrypt 해시 (cost=12)

### 5.2 API 보안
```python
# 역할 기반 접근 제어 예시
@router.get("/admin-only")
async def admin_endpoint(
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    pass
```

### 5.3 데이터 보안
- 민감 정보 암호화 저장
- SQL Injection 방지 (ORM 사용)
- XSS 방지 (React 기본 이스케이핑)

---

## 6. 성능 요구사항

### 6.1 응답 시간
| 엔드포인트 | 목표 | 측정 기준 |
|-----------|------|----------|
| 단순 조회 | < 100ms | p95 |
| 목록 조회 | < 200ms | p95 |
| AI 추천 | < 2s | p95 |
| PDF 생성 | < 5s | p95 |

### 6.2 확장성
- 수평 확장: Docker 컨테이너 복제
- DB 연결 풀: 최대 20 연결
- 캐시: Redis (매칭 스코어 1시간)

---

## 7. ML 서비스

### 7.1 매칭 알고리즘
```python
매칭 점수 = (
    전문분야 일치도 × 0.40 +
    평가 성과     × 0.20 +
    자격 검증     × 0.15 +
    경력 연수     × 0.15 +
    가용성       × 0.10
)
```

### 7.2 의미 유사도
- 모델: `paraphrase-multilingual-MiniLM-L12-v2`
- 용도: 전문가 소개 ↔ 기업 수요 매칭
- 캐시: 임베딩 벡터 저장

---

## 8. 배포 구성

### 8.1 개발 환경
```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
  db:
    image: postgres:14
    ports: ["5432:5432"]
  redis:
    image: redis:7
    ports: ["6379:6379"]
```

### 8.2 환경 변수
```
# Backend
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=...
REDIS_URL=redis://localhost:6379

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 9. 모니터링

### 9.1 로깅
- 구조화된 JSON 로그
- 요청/응답 추적
- 에러 스택 트레이스

### 9.2 메트릭
- API 응답 시간
- 에러율
- 동시 접속자 수

---

## 부록

### A. API 응답 형식
```json
{
  "data": {...},
  "message": "성공",
  "success": true
}
```

### B. 에러 응답 형식
```json
{
  "detail": "에러 메시지",
  "code": "ERROR_CODE"
}
```
