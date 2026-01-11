# Design System: AX 코칭단 평가 시스템

---

## 1. 디자인 원칙

### 1.1 핵심 원칙
1. **명확성**: 정보가 한눈에 파악되어야 함
2. **일관성**: 동일한 패턴과 컴포넌트 재사용
3. **효율성**: 최소한의 클릭으로 목표 달성
4. **접근성**: WCAG 2.1 AA 기준 준수

### 1.2 디자인 목표
- 전문적이고 신뢰감 있는 UI
- 한국어 최적화 타이포그래피
- 데이터 시각화 중심의 대시보드

---

## 2. 컬러 시스템

### 2.1 Primary Colors
```css
/* Blue (주요 액션, 링크) */
--primary-50:  #eff6ff;
--primary-100: #dbeafe;
--primary-200: #bfdbfe;
--primary-300: #93c5fd;
--primary-400: #60a5fa;
--primary-500: #3b82f6;  /* 기본 */
--primary-600: #2563eb;  /* 호버 */
--primary-700: #1d4ed8;
--primary-800: #1e40af;
--primary-900: #1e3a8a;
```

### 2.2 Semantic Colors
```css
/* Success (성공, 인증) */
--success-50:  #f0fdf4;
--success-500: #22c55e;
--success-600: #16a34a;

/* Warning (주의, 대기) */
--warning-50:  #fffbeb;
--warning-500: #f59e0b;
--warning-600: #d97706;

/* Error (오류, 실패) */
--error-50:  #fef2f2;
--error-500: #ef4444;
--error-600: #dc2626;

/* Info (정보) */
--info-50:  #eff6ff;
--info-500: #3b82f6;
--info-600: #2563eb;
```

### 2.3 Neutral Colors
```css
/* Gray Scale */
--gray-50:  #f9fafb;  /* 배경 */
--gray-100: #f3f4f6;  /* 카드 배경 */
--gray-200: #e5e7eb;  /* 구분선 */
--gray-300: #d1d5db;  /* 비활성 */
--gray-400: #9ca3af;  /* 플레이스홀더 */
--gray-500: #6b7280;  /* 보조 텍스트 */
--gray-600: #4b5563;  /* 아이콘 */
--gray-700: #374151;  /* 본문 */
--gray-800: #1f2937;  /* 제목 */
--gray-900: #111827;  /* 강조 */
```

### 2.4 스코어 컬러
```css
/* 점수 등급별 색상 */
--score-excellent: #22c55e;  /* 80점 이상 */
--score-good:      #3b82f6;  /* 60-79점 */
--score-fair:      #f59e0b;  /* 40-59점 */
--score-poor:      #ef4444;  /* 40점 미만 */
```

---

## 3. 타이포그래피

### 3.1 폰트 패밀리
```css
/* 시스템 폰트 스택 (한글 최적화) */
font-family:
    'Pretendard',           /* 1순위: 웹폰트 */
    -apple-system,          /* macOS/iOS */
    BlinkMacSystemFont,
    'Malgun Gothic',        /* Windows */
    '맑은 고딕',
    sans-serif;

/* 숫자/코드 */
font-family:
    'JetBrains Mono',
    'D2Coding',
    monospace;
```

### 3.2 폰트 크기
```css
/* Heading */
--text-4xl: 2.25rem;   /* 36px - 페이지 제목 */
--text-3xl: 1.875rem;  /* 30px - 섹션 제목 */
--text-2xl: 1.5rem;    /* 24px - 카드 제목 */
--text-xl:  1.25rem;   /* 20px - 서브 제목 */
--text-lg:  1.125rem;  /* 18px - 강조 본문 */

/* Body */
--text-base: 1rem;     /* 16px - 기본 본문 */
--text-sm:   0.875rem; /* 14px - 보조 텍스트 */
--text-xs:   0.75rem;  /* 12px - 캡션 */
```

### 3.3 폰트 굵기
```css
--font-normal:   400;  /* 본문 */
--font-medium:   500;  /* 강조 본문 */
--font-semibold: 600;  /* 제목, 버튼 */
--font-bold:     700;  /* 페이지 제목 */
```

### 3.4 줄 간격
```css
--leading-tight:  1.25;  /* 제목 */
--leading-normal: 1.5;   /* 본문 */
--leading-relaxed: 1.75; /* 긴 텍스트 */
```

---

## 4. 레이아웃

### 4.1 그리드 시스템
```css
/* 12 컬럼 그리드 */
--container-max: 1280px;
--gutter: 24px;

/* 반응형 브레이크포인트 */
--screen-sm:  640px;   /* 모바일 */
--screen-md:  768px;   /* 태블릿 */
--screen-lg:  1024px;  /* 데스크톱 */
--screen-xl:  1280px;  /* 와이드 */
--screen-2xl: 1536px;  /* 울트라 와이드 */
```

### 4.2 여백
```css
/* Spacing Scale */
--space-1:  0.25rem;  /* 4px */
--space-2:  0.5rem;   /* 8px */
--space-3:  0.75rem;  /* 12px */
--space-4:  1rem;     /* 16px */
--space-5:  1.25rem;  /* 20px */
--space-6:  1.5rem;   /* 24px */
--space-8:  2rem;     /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

### 4.3 페이지 레이아웃
```
┌────────────────────────────────────────────────────────────┐
│ Header (h: 64px)                                           │
├────────────┬───────────────────────────────────────────────┤
│            │                                               │
│ Sidebar    │ Main Content                                  │
│ (w: 256px) │ (padding: 24px)                              │
│            │                                               │
│            │ ┌───────────────────────────────────────────┐ │
│            │ │ Page Title                                │ │
│            │ ├───────────────────────────────────────────┤ │
│            │ │ Content Cards                             │ │
│            │ │                                           │ │
│            │ └───────────────────────────────────────────┘ │
│            │                                               │
└────────────┴───────────────────────────────────────────────┘
```

---

## 5. 컴포넌트

### 5.1 버튼
```jsx
// Primary Button
<button className="px-4 py-2 bg-blue-600 text-white rounded-md
                   hover:bg-blue-700 font-medium transition-colors">
    버튼 텍스트
</button>

// Secondary Button
<button className="px-4 py-2 border border-gray-300 text-gray-700
                   rounded-md hover:bg-gray-100 font-medium">
    버튼 텍스트
</button>

// Danger Button
<button className="px-4 py-2 bg-red-600 text-white rounded-md
                   hover:bg-red-700 font-medium">
    삭제
</button>
```

**크기 변형:**
| 크기 | 패딩 | 폰트 |
|------|------|------|
| sm | px-3 py-1.5 | text-sm |
| md | px-4 py-2 | text-base |
| lg | px-6 py-3 | text-lg |

### 5.2 카드
```jsx
<div className="bg-white rounded-lg border border-gray-200
                shadow-sm hover:shadow-md transition-shadow">
    <div className="p-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">
            카드 제목
        </h3>
    </div>
    <div className="p-4">
        카드 내용
    </div>
</div>
```

### 5.3 뱃지
```jsx
// Status Badge
<span className="inline-flex items-center px-2 py-0.5 rounded-full
                 text-xs font-medium bg-green-100 text-green-800">
    인증됨
</span>

// 상태별 스타일
const badgeStyles = {
    qualified:    'bg-green-100 text-green-800',
    pending:      'bg-yellow-100 text-yellow-800',
    disqualified: 'bg-red-100 text-red-800',
};
```

### 5.4 입력 필드
```jsx
// Text Input
<input
    type="text"
    className="w-full px-3 py-2 border border-gray-300 rounded-md
               focus:outline-none focus:ring-2 focus:ring-blue-500
               focus:border-transparent"
    placeholder="입력하세요"
/>

// Error State
<input className="... border-red-500 focus:ring-red-500" />
<p className="mt-1 text-sm text-red-600">오류 메시지</p>
```

### 5.5 테이블
```jsx
<table className="min-w-full divide-y divide-gray-200">
    <thead className="bg-gray-50">
        <tr>
            <th className="px-6 py-3 text-left text-xs font-medium
                           text-gray-500 uppercase tracking-wider">
                컬럼명
            </th>
        </tr>
    </thead>
    <tbody className="bg-white divide-y divide-gray-200">
        <tr className="hover:bg-gray-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm
                           text-gray-900">
                데이터
            </td>
        </tr>
    </tbody>
</table>
```

### 5.6 스코어 바
```jsx
function ScoreBar({ score, maxScore = 100 }) {
    const percentage = (score / maxScore) * 100;
    const getColor = (pct) => {
        if (pct >= 80) return 'bg-green-500';
        if (pct >= 60) return 'bg-blue-500';
        if (pct >= 40) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    return (
        <div className="w-full bg-gray-200 rounded-full h-2">
            <div
                className={`h-2 rounded-full ${getColor(percentage)}`}
                style={{ width: `${percentage}%` }}
            />
        </div>
    );
}
```

---

## 6. 아이콘

### 6.1 아이콘 라이브러리
- **Heroicons** (Tailwind 공식): 기본 UI 아이콘
- **Lucide React**: 추가 아이콘 필요시

### 6.2 아이콘 크기
```css
--icon-xs: 16px;  /* 인라인 */
--icon-sm: 20px;  /* 버튼 내 */
--icon-md: 24px;  /* 기본 */
--icon-lg: 32px;  /* 강조 */
--icon-xl: 48px;  /* 대형 */
```

### 6.3 주요 아이콘 사용처
| 용도 | 아이콘 | 사용처 |
|------|--------|--------|
| 확인/성공 | CheckCircle | 인증 상태, 완료 |
| 경고 | ExclamationTriangle | 주의사항 |
| 오류 | XCircle | 미인증, 실패 |
| 사용자 | UserCircle | 프로필 |
| 문서 | DocumentText | 보고서 |
| 검색 | MagnifyingGlass | 검색바 |
| 필터 | FunnelIcon | 필터 |
| 추가 | PlusIcon | 신규 등록 |

---

## 7. 상태 표시

### 7.1 자격 상태
```jsx
const qualificationBadge = {
    QUALIFIED: {
        color: 'bg-green-100 text-green-800',
        icon: CheckCircle,
        label: '인증됨'
    },
    PENDING: {
        color: 'bg-yellow-100 text-yellow-800',
        icon: Clock,
        label: '심사중'
    },
    DISQUALIFIED: {
        color: 'bg-red-100 text-red-800',
        icon: XCircle,
        label: '미인증'
    }
};
```

### 7.2 매칭 상태
```jsx
const matchingStatus = {
    PROPOSED:    { color: 'blue',   label: '제안됨' },
    ACCEPTED:    { color: 'green',  label: '수락됨' },
    REJECTED:    { color: 'red',    label: '거절됨' },
    IN_PROGRESS: { color: 'yellow', label: '진행중' },
    COMPLETED:   { color: 'gray',   label: '완료' },
    CANCELLED:   { color: 'gray',   label: '취소됨' }
};
```

---

## 8. 차트 스타일

### 8.1 Recharts 테마
```javascript
const chartTheme = {
    colors: [
        '#3b82f6', // Blue
        '#22c55e', // Green
        '#f59e0b', // Yellow
        '#ef4444', // Red
        '#8b5cf6', // Purple
    ],
    axis: {
        stroke: '#e5e7eb',
        fontSize: 12,
        fontFamily: 'Pretendard, sans-serif',
    },
    tooltip: {
        background: '#ffffff',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        shadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
    }
};
```

### 8.2 차트 유형별 가이드
| 차트 유형 | 용도 | 컴포넌트 |
|----------|------|----------|
| Bar Chart | 카테고리별 점수 비교 | ScoreDistribution |
| Pie Chart | 비율 표시 | CategoryBreakdown |
| Line Chart | 시간별 추이 | TrendChart |
| Radar Chart | 다차원 점수 | ScoreRadar |

---

## 9. 반응형 디자인

### 9.1 브레이크포인트별 레이아웃
```
Mobile (< 640px):
- 사이드바 숨김 (햄버거 메뉴)
- 단일 컬럼 레이아웃
- 테이블 → 카드 변환

Tablet (640-1024px):
- 축소된 사이드바
- 2컬럼 그리드

Desktop (1024px+):
- 전체 사이드바 표시
- 3-4컬럼 그리드
```

### 9.2 Tailwind 반응형 클래스
```jsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
    {/* 반응형 카드 그리드 */}
</div>
```

---

## 10. 접근성

### 10.1 색상 대비
- 텍스트: 최소 4.5:1 (WCAG AA)
- 대형 텍스트: 최소 3:1

### 10.2 키보드 네비게이션
- 모든 상호작용 요소 Tab 접근 가능
- Focus visible 스타일 적용

### 10.3 스크린 리더
- 의미 있는 alt 텍스트
- aria-label 적용
- 역할(role) 명시

---

## 부록: Tailwind 설정

```javascript
// tailwind.config.js
module.exports = {
    content: ['./src/**/*.{js,ts,jsx,tsx}'],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Pretendard', '-apple-system', 'sans-serif'],
                mono: ['JetBrains Mono', 'D2Coding', 'monospace'],
            },
            colors: {
                primary: {
                    50: '#eff6ff',
                    // ... 전체 팔레트
                    900: '#1e3a8a',
                },
            },
        },
    },
    plugins: [],
};
```
