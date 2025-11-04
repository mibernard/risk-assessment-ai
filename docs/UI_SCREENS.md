# UI Screens & Acceptance Criteria

## Design Principles

- **Clarity**: Compliance officers must quickly understand AI decisions
- **Trust**: Show confidence scores and model information
- **Efficiency**: Minimize clicks to key actions
- **Professionalism**: Banking-grade UI (not prototype-looking)

**Design System**: shadcn/ui components + Tailwind CSS  
**Color Scheme**:

- High risk: Red/Orange (`bg-red-50`, `text-red-700`)
- Medium risk: Yellow (`bg-yellow-50`, `text-yellow-700`)
- Low risk: Green (`bg-green-50`, `text-green-700`)

---

## 1. Dashboard (`/dashboard`)

### Purpose

Central hub for viewing all flagged transactions requiring review.

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Risk Assessment Dashboard            [Generate Report] [🔍] │
├─────────────────────────────────────────────────────────────┤
│  Filters:  [All Statuses ▾]  [Min Risk: 0.5]  [Clear]       │
├─────────────────────────────────────────────────────────────┤
│  Customer    │ Amount    │ Country │ Risk Score │ Status    │
├─────────────────────────────────────────────────────────────┤
│  Alice J.    │ $5,300    │ SG 🇸🇬   │ ⚠️  0.82   │ 🔴 New     │ ← Clickable
│  Robert C.   │ $12,000   │ US 🇺🇸   │ ⚠️  0.54   │ 🟡 Review  │
│  Maria G.    │ $450      │ US 🇺🇸   │ ✅ 0.18    │ 🟢 Resolved│
│  John S.     │ $9,800    │ US 🇺🇸   │ 🚨 0.94    │ 🔴 New     │
└─────────────────────────────────────────────────────────────┘
```

### Acceptance Criteria

**Data Display**:

- [ ] Table shows all cases from `GET /cases`
- [ ] Columns: customer_name, amount, country, risk_score, status
- [ ] Risk score color-coded: <0.4 green, 0.4-0.7 yellow, >0.7 red
- [ ] Amount formatted as currency (`$5,300.00`)
- [ ] Country shows flag emoji (optional)

**Interactions**:

- [ ] Clicking any row navigates to `/cases/[id]`
- [ ] Hover shows hand cursor on rows
- [ ] "Generate Report" button → `/report` page
- [ ] Search/filter inputs update table (optional for MVP)

**States**:

- [ ] Loading state: Skeleton placeholders
- [ ] Error state: Error message + retry button
- [ ] Empty state: "No cases found" message

**Performance**:

- [ ] Table renders in <1 second
- [ ] Supports 100+ rows without lag

---

## 2. Case Detail (`/cases/[id]`)

### Purpose

Deep-dive into individual case with AI-powered explanation.

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  ← Back to Dashboard          Case #550e8400                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📊 Transaction Details                                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Customer: Alice Johnson                             │   │
│  │  Amount: $5,300.00 USD                               │   │
│  │  Country: Singapore 🇸🇬                               │   │
│  │  Risk Score: 0.82 (High Risk)                        │   │
│  │  Status: 🔴 New                                       │   │
│  │  Created: Jan 15, 2025 10:30 AM                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  🤖 AI Explanation                    [Explain this case]    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  💡 Explanation                                       │   │
│  │  Transaction exhibits multiple high-risk indicators:  │   │
│  │  first-time international transfer to jurisdiction... │   │
│  │                                                       │   │
│  │  ✅ Recommended Action                                │   │
│  │  HOLD transaction for enhanced due diligence...      │   │
│  │                                                       │   │
│  │  📈 Confidence: 0.89 (89%)                            │   │
│  │  🤖 Model: granite-13b-instruct-v2                    │   │
│  │  🪙 Tokens: 342                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  [Mark as Reviewing]  [Resolve Case]                         │
└─────────────────────────────────────────────────────────────┘
```

### Acceptance Criteria

**Case Details Section**:

- [ ] Fetches case via `GET /cases/{id}`
- [ ] Shows all case fields clearly
- [ ] Risk score with visual indicator (badge color)
- [ ] Timestamp formatted human-readable
- [ ] Back button returns to `/dashboard`

**AI Explanation Section**:

- [ ] Initially shows "Explain this case" button
- [ ] Button click: `POST /explain` with `case_id`
- [ ] Loading state: Spinner + "Generating explanation..."
- [ ] Success: Renders explanation card with:
  - Rationale text (2-3 sentences)
  - Recommended action (clear, actionable)
  - Confidence score (progress bar or percentage)
  - Model name (`granite-13b-instruct-v2`)
  - Token count (transparency)
- [ ] Error state: Error message + retry button

**Caching**:

- [ ] If explanation already exists, show immediately
- [ ] Don't call API again if cached (<1 hour old)
- [ ] Show timestamp: "Explained 10 minutes ago"

**Actions** (optional for MVP):

- [ ] "Mark as Reviewing" updates status via API
- [ ] "Resolve Case" updates status to resolved

**States**:

- [ ] Loading case: Skeleton placeholders
- [ ] Case not found: 404 page
- [ ] AI error: Fallback message + cached response

---

## 3. Report (`/report`)

### Purpose

Generate aggregated statistics and compliance summary.

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Compliance Report                    [Download PDF]         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📊 Statistics                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Total Cases: 2,000                                  │   │
│  │  High Risk (≥0.7): 48 cases                          │   │
│  │  Medium Risk (0.4-0.7): 127 cases                    │   │
│  │  Low Risk (<0.4): 1,825 cases                        │   │
│  │  Average Risk: 0.34                                  │   │
│  │  Total Amount: $8,450,000.00                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  📈 Status Distribution                                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  [====        ] New: 243 (12.2%)                     │   │
│  │  [============] Reviewing: 512 (25.6%)               │   │
│  │  [==========================] Resolved: 1,245 (62.2%)│   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  🤖 AI Summary (optional)                [Generate Summary]  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  48 high-risk transactions detected in the past 7    │   │
│  │  days, primarily from Southeast Asian regions.       │   │
│  │  Recommend increased monitoring of cross-border      │   │
│  │  transfers >$5000.                                    │   │
│  │                                                       │   │
│  │  🤖 Generated by granite-13b-instruct-v2              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  Period: Jan 8, 2025 - Jan 15, 2025                          │
└─────────────────────────────────────────────────────────────┘
```

### Acceptance Criteria

**Statistics Section**:

- [ ] Calls `POST /report` (no body = all open cases)
- [ ] Shows total count, risk breakdown, avg risk
- [ ] Total amount formatted as currency
- [ ] Numbers formatted with commas (2,000 not 2000)

**Status Distribution**:

- [ ] Visual bar chart or progress bars
- [ ] Shows count and percentage for each status
- [ ] Color-coded (red=new, yellow=reviewing, green=resolved)

**AI Summary** (optional feature):

- [ ] Button to generate summary
- [ ] Calls `POST /report` with `include_ai_summary: true`
- [ ] Renders natural language summary from watsonx.ai
- [ ] Shows model name for transparency

**Actions**:

- [ ] "Download PDF" button (optional for MVP)
- [ ] "Back to Dashboard" link

**States**:

- [ ] Loading: Skeleton placeholders
- [ ] Error: Error message + retry button
- [ ] Empty: "No cases to report" message

**Performance**:

- [ ] Report generates in <2 seconds
- [ ] Aggregations done in backend (not frontend)

---

## Component Library

### shadcn/ui Components Used

```bash
npx shadcn-ui@latest add table
npx shadcn-ui@latest add card
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add button
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add alert
```

### Shared Components

**`<RiskBadge />`**:

```tsx
interface RiskBadgeProps {
  score: number; // 0.0 - 1.0
}

// Usage: <RiskBadge score={0.82} />
// Renders: 🚨 0.82 High Risk (red badge)
```

**`<CaseTable />`**:

```tsx
interface CaseTableProps {
  cases: Case[];
  onRowClick: (caseId: string) => void;
}

// Usage: <CaseTable cases={cases} onRowClick={(id) => router.push(`/cases/${id}`)} />
```

**`<LoadingState />`**:

```tsx
// Usage: <LoadingState message="Generating explanation..." />
// Shows spinner + message
```

**`<ErrorState />`**:

```tsx
interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

// Usage: <ErrorState message="AI service unavailable" onRetry={refetch} />
```

---

## Responsive Design

**Desktop** (1280px+):

- Full table with all columns
- Side-by-side cards

**Tablet** (768px - 1279px):

- Table scrollable horizontally
- Cards stack vertically

**Mobile** (< 768px):

- Cards replace table view
- Simplified layout
- Larger touch targets

---

## Accessibility

- [ ] All buttons have `aria-label`
- [ ] Color not sole indicator (use icons + text)
- [ ] Keyboard navigation works (Tab, Enter)
- [ ] Screen reader friendly
- [ ] Sufficient color contrast (WCAG AA)

---

## Performance Targets

- Time to Interactive: <2 seconds
- API response time: <3 seconds
- Lighthouse Score: >90
- No layout shift (CLS < 0.1)

---

## Testing Checklist

**Dashboard**:

- [ ] Loads 100 cases without lag
- [ ] Clicking row navigates correctly
- [ ] Loading/error states work
- [ ] Filter updates table

**Case Detail**:

- [ ] Shows case details correctly
- [ ] "Explain" button calls API
- [ ] Explanation renders properly
- [ ] Back button works

**Report**:

- [ ] Statistics calculate correctly
- [ ] Chart/bars display properly
- [ ] AI summary generates (optional)
- [ ] Period dates correct
