# Frontend (Next.js)

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `.env.local` file in `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production deployment (Vercel):

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### 3. Run Development Server

```bash
npm run dev
```

App runs at: http://localhost:3000

---

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Landing page (redirect to dashboard)
│   ├── dashboard/
│   │   └── page.tsx            # Case list view ⭐
│   ├── cases/
│   │   └── [id]/
│   │       └── page.tsx        # Case detail + AI explanation ⭐
│   └── report/
│       └── page.tsx            # Compliance report ⭐
├── components/
│   ├── ui/                     # shadcn/ui components
│   ├── CaseTable.tsx           # Reusable case table
│   ├── RiskBadge.tsx           # Risk score badge
│   ├── LoadingState.tsx        # Loading skeleton
│   └── ErrorState.tsx          # Error message
├── lib/
│   ├── api.ts                  # API client
│   └── utils.ts                # Utilities
├── public/                     # Static assets
├── .env.local                  # Environment vars (gitignored)
├── next.config.ts              # Next.js config
├── tailwind.config.ts          # Tailwind config
├── tsconfig.json               # TypeScript config
└── package.json                # Dependencies
```

---

## Implementation Tasks

### Phase 1: Setup & UI Components

**Goal**: Set up Next.js project with shadcn/ui and basic components

**Tasks**:

- [x] Initialize Next.js project
- [ ] Install shadcn/ui components:
  ```bash
  npx shadcn-ui@latest init
  npx shadcn-ui@latest add table
  npx shadcn-ui@latest add card
  npx shadcn-ui@latest add badge
  npx shadcn-ui@latest add button
  npx shadcn-ui@latest add skeleton
  npx shadcn-ui@latest add alert
  ```
- [ ] Create `lib/api.ts` API client
- [ ] Create reusable components:
  - `<RiskBadge />` - Color-coded risk score
  - `<LoadingState />` - Skeleton placeholders
  - `<ErrorState />` - Error message with retry
  - `<CaseTable />` - Table with clickable rows

**Success Criteria**:

- TypeScript strict mode enabled
- Tailwind CSS configured
- shadcn/ui components installed
- API client typed and ready

### Phase 2: Dashboard Page

**Goal**: Implement case list view

**Location**: `app/dashboard/page.tsx`

**Tasks**:

- [ ] Fetch cases from `GET /cases`
- [ ] Render `<CaseTable />` component
- [ ] Implement loading state (skeletons)
- [ ] Implement error state (error message + retry)
- [ ] Make rows clickable → navigate to `/cases/[id]`
- [ ] Add "Generate Report" button → navigate to `/report`
- [ ] Format amounts as currency ($5,300.00)
- [ ] Color-code risk scores (red/yellow/green)

**Acceptance Criteria**:

- See `docs/UI_SCREENS.md` section 1

### Phase 3: Case Detail Page

**Goal**: Implement case detail view with AI explanation

**Location**: `app/cases/[id]/page.tsx`

**Tasks**:

- [ ] Fetch case from `GET /cases/{id}`
- [ ] Display case details (customer, amount, country, risk, status)
- [ ] Add "Explain this case" button
- [ ] On button click:
  - Show loading spinner
  - Call `POST /explain` with case_id
  - Render explanation card
- [ ] Display explanation with:
  - Rationale (2-3 sentences)
  - Recommended action
  - Confidence score (progress bar)
  - Model name (transparency)
  - Token count
- [ ] Implement error handling (fallback message)
- [ ] Add "Back to Dashboard" link
- [ ] Optional: "Mark as Reviewing" / "Resolve" buttons

**Acceptance Criteria**:

- See `docs/UI_SCREENS.md` section 2

### Phase 4: Report Page

**Goal**: Implement compliance report view

**Location**: `app/report/page.tsx`

**Tasks**:

- [ ] Call `POST /report` (no body = all open cases)
- [ ] Display statistics:
  - Total cases
  - High/medium/low risk counts
  - Average risk score
  - Total amount
- [ ] Create visual status distribution (progress bars)
- [ ] Optional: Add "Generate AI Summary" button
  - Calls `POST /report` with `include_ai_summary: true`
  - Displays natural language summary
- [ ] Format numbers with commas (2,000 not 2000)
- [ ] Add "Back to Dashboard" link
- [ ] Optional: "Download PDF" button

**Acceptance Criteria**:

- See `docs/UI_SCREENS.md` section 3

---

## API Client (`lib/api.ts`)

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Case {
  id: string;
  customer_name: string;
  amount: number;
  country: string;
  risk_score: number;
  status: "new" | "reviewing" | "resolved";
  created_at: string;
  explanation_generated?: boolean;
  model_version?: string;
  tokens_used?: number;
}

export interface Explanation {
  case_id: string;
  confidence: number;
  rationale: string;
  recommended_action: string;
  model_used: string;
  tokens_consumed: number;
  generation_time_ms: number;
  created_at: string;
}

export interface Report {
  summary: string;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  avg_risk: number;
  total_cases: number;
  total_amount: number;
  status_distribution: {
    new: number;
    reviewing: number;
    resolved: number;
  };
  period_start: string;
  period_end: string;
}

// Fetch all cases
export async function getCases(): Promise<Case[]> {
  const response = await fetch(`${API_URL}/cases`);
  if (!response.ok) {
    throw new Error("Failed to fetch cases");
  }
  return response.json();
}

// Fetch single case
export async function getCase(id: string): Promise<Case> {
  const response = await fetch(`${API_URL}/cases/${id}`);
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Case not found");
    }
    throw new Error("Failed to fetch case");
  }
  return response.json();
}

// Generate explanation
export async function explainCase(caseId: string): Promise<Explanation> {
  const response = await fetch(`${API_URL}/explain`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ case_id: caseId }),
  });

  if (!response.ok) {
    if (response.status === 429) {
      throw new Error("Token budget exceeded");
    }
    if (response.status === 503) {
      throw new Error("AI service unavailable");
    }
    throw new Error("Failed to generate explanation");
  }

  return response.json();
}

// Generate report
export async function generateReport(options?: {
  case_ids?: string[];
  include_ai_summary?: boolean;
}): Promise<Report> {
  const response = await fetch(`${API_URL}/report`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(options || {}),
  });

  if (!response.ok) {
    throw new Error("Failed to generate report");
  }

  return response.json();
}
```

---

## Reusable Components

### `<RiskBadge />` (`components/RiskBadge.tsx`)

```typescript
import { Badge } from "@/components/ui/badge";

interface RiskBadgeProps {
  score: number; // 0.0 - 1.0
}

export function RiskBadge({ score }: RiskBadgeProps) {
  const getRiskLevel = (score: number) => {
    if (score >= 0.7)
      return { label: "High Risk", color: "bg-red-100 text-red-700" };
    if (score >= 0.4)
      return { label: "Medium Risk", color: "bg-yellow-100 text-yellow-700" };
    return { label: "Low Risk", color: "bg-green-100 text-green-700" };
  };

  const { label, color } = getRiskLevel(score);

  return (
    <Badge className={color}>
      {score.toFixed(2)} {label}
    </Badge>
  );
}
```

### `<LoadingState />` (`components/LoadingState.tsx`)

```typescript
import { Skeleton } from "@/components/ui/skeleton";

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = "Loading..." }: LoadingStateProps) {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-full" />
      <Skeleton className="h-8 w-full" />
      <Skeleton className="h-8 w-full" />
      <p className="text-muted-foreground text-center">{message}</p>
    </div>
  );
}
```

### `<ErrorState />` (`components/ErrorState.tsx`)

```typescript
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { AlertCircle } from "lucide-react";

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Error</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
      {onRetry && (
        <Button onClick={onRetry} variant="outline" className="mt-2">
          Retry
        </Button>
      )}
    </Alert>
  );
}
```

---

## Styling Guidelines

### Color Scheme

**Risk Levels**:

- High (≥0.7): `bg-red-50 text-red-700 border-red-200`
- Medium (0.4-0.7): `bg-yellow-50 text-yellow-700 border-yellow-200`
- Low (<0.4): `bg-green-50 text-green-700 border-green-200`

**Status**:

- New: Red dot 🔴
- Reviewing: Yellow dot 🟡
- Resolved: Green dot 🟢

**Typography**:

- Headings: `text-2xl font-bold`
- Subheadings: `text-lg font-semibold`
- Body: `text-base`
- Muted: `text-muted-foreground`

---

## Testing

### Manual Testing Checklist

**Dashboard**:

- [ ] Load page at http://localhost:3000/dashboard
- [ ] Table shows all cases
- [ ] Risk scores color-coded correctly
- [ ] Clicking row navigates to case detail
- [ ] "Generate Report" button works

**Case Detail**:

- [ ] Load case detail page
- [ ] Case information displays correctly
- [ ] "Explain" button triggers API call
- [ ] Loading state shows spinner
- [ ] Explanation renders properly
- [ ] Error state shows message on failure

**Report**:

- [ ] Load report page
- [ ] Statistics calculate correctly
- [ ] Status distribution displays
- [ ] Optional AI summary works

---

## Development Tips

### 1. Hot Module Replacement

Next.js auto-reloads when you edit files. Changes reflect immediately in browser.

### 2. TypeScript IntelliSense

Use `Ctrl+Space` in VS Code to see available props and types.

### 3. Debugging

Use browser DevTools:

- Network tab: Check API calls
- Console: View errors and logs
- React DevTools: Inspect component state

### 4. Tailwind Autocomplete

Install VS Code extension: "Tailwind CSS IntelliSense"

### 5. Component Preview

Use React DevTools to preview component variations.

---

## Deployment

### Deploy to Vercel (Recommended)

1. **Push code to GitHub**:

```bash
git add .
git commit -m "feat: complete frontend implementation"
git push origin main
```

2. **Import to Vercel**:

- Go to https://vercel.com/new
- Import your GitHub repo
- Add environment variable: `NEXT_PUBLIC_API_URL`
- Deploy

3. **Update backend CORS**:
   Add Vercel URL to allowed origins in backend.

### Deploy to Netlify (Alternative)

1. **Build command**: `npm run build`
2. **Publish directory**: `.next`
3. **Environment variable**: `NEXT_PUBLIC_API_URL`

---

## Troubleshooting

### Issue: "Module not found: Can't resolve '@/components/ui/...'"

**Solution**: Run shadcn-ui installation:

```bash
npx shadcn-ui@latest add [component-name]
```

### Issue: "API calls failing with CORS error"

**Solution**: Check backend CORS configuration allows frontend origin

### Issue: "Environment variable undefined"

**Solution**:

- Ensure `.env.local` exists
- Restart dev server after adding env vars
- Use `NEXT_PUBLIC_` prefix for client-side vars

### Issue: "Tailwind styles not applying"

**Solution**: Check `tailwind.config.ts` includes correct paths:

```typescript
content: [
  "./app/**/*.{js,ts,jsx,tsx,mdx}",
  "./components/**/*.{js,ts,jsx,tsx,mdx}",
];
```

---

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [UI Screens Spec](../docs/UI_SCREENS.md)
- [API Contract](../docs/API_CONTRACT.md)
