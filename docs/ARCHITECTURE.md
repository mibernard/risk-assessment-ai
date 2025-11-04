# Architecture

## System Overview

```
┌─────────────┐      HTTP/REST      ┌─────────────┐      SDK      ┌──────────────┐
│   Next.js   │ ←─────────────────→ │   FastAPI   │ ←───────────→ │ watsonx.ai   │
│  (Frontend) │     JSON/CORS       │  (Backend)  │   API calls   │  (Granite)   │
└─────────────┘                     └─────────────┘               └──────────────┘
                                           ↓
                                      SQL/ORM
                                           ↓
                                    ┌─────────────┐
                                    │    Neon     │
                                    │ (Postgres)  │
                                    └─────────────┘
```

## Component Details

### Frontend (Next.js 14)

**Location**: `/frontend`

**Purpose**: User interface for risk assessment dashboard

**Tech Stack**:

- Next.js 14 with App Router
- TypeScript (strict mode)
- Tailwind CSS + shadcn/ui
- React Server Components where applicable

**Key Files**:

- `app/page.tsx` → Landing/redirect
- `app/dashboard/page.tsx` → Case list view
- `app/cases/[id]/page.tsx` → Case detail + AI explanation
- `app/report/page.tsx` → Aggregated reports
- `components/` → Reusable UI components
- `lib/api.ts` → API client (fetch wrapper)

**Environment Variables**:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (FastAPI)

**Location**: `/backend`

**Purpose**: REST API + watsonx.ai integration layer

**Tech Stack**:

- FastAPI (Python 3.9+)
- Pydantic v2 (validation)
- SQLAlchemy 2.0 (ORM)
- IBM watsonx.ai Python SDK
- Uvicorn (ASGI server)

**Key Modules**:

```
backend/
├── main.py                 # FastAPI app + routes
├── models.py               # SQLAlchemy models
├── schemas.py              # Pydantic schemas
├── database.py             # DB connection
├── services/
│   ├── watsonx_service.py  # watsonx.ai integration ⭐
│   ├── risk_analyzer.py    # Business logic
│   └── report_generator.py # Report aggregation
├── config.py               # Environment config
└── requirements.txt        # Dependencies
```

**Environment Variables**:

```env
DATABASE_URL=postgresql://user:pass@host/db
WATSONX_API_KEY=your_key_here
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

### Database (Neon Postgres)

**Purpose**: Persist case data, audit trail

**Schema** (simplified):

```sql
CREATE TABLE cases (
    id UUID PRIMARY KEY,
    customer_name VARCHAR(255),
    amount DECIMAL(10,2),
    country VARCHAR(100),
    risk_score DECIMAL(3,2),  -- 0.00 to 1.00
    status VARCHAR(50),
    created_at TIMESTAMP,
    -- Additional fields for watsonx.ai metadata
    explanation_generated BOOLEAN DEFAULT FALSE,
    model_version VARCHAR(50),
    tokens_used INTEGER
);

CREATE TABLE explanations (
    id UUID PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    confidence DECIMAL(3,2),
    rationale TEXT,
    recommended_action TEXT,
    model_used VARCHAR(100),
    tokens_consumed INTEGER,
    created_at TIMESTAMP
);
```

### AI Layer (IBM watsonx.ai)

**Integration Point**: `backend/services/watsonx_service.py`

**Model**: IBM Granite-13b-instruct-v2

**API Flow**:

1. FastAPI receives `/explain` request with `case_id`
2. Fetch case data from Postgres
3. Build prompt with case context
4. Call watsonx.ai SDK: `model.generate_text(prompt)`
5. Parse response (risk_score, rationale, action)
6. Store explanation in DB
7. Return to frontend

**Token Management**:

- Track usage per request
- Alert at 80% of $250 budget ($200)
- Fallback to cached responses if budget exceeded

## Core Data Flow

### 1. GET /cases → Dashboard List

```
User → Next.js → FastAPI /cases → Postgres SELECT → JSON response → Table UI
```

### 2. GET /cases/{id} → Case Details

```
User clicks row → Next.js → FastAPI /cases/{id} → Postgres → Case details UI
```

### 3. POST /explain → AI Explanation ⭐

```
User clicks "Explain" button
  ↓
Next.js POST /explain {case_id}
  ↓
FastAPI:
  1. Fetch case from Postgres
  2. Build prompt template
  3. Call watsonx.ai SDK
     POST https://us-south.ml.cloud.ibm.com/ml/v1/text/generation
     Body: {
       model_id: "ibm/granite-13b-instruct-v2",
       input: "<prompt>",
       parameters: { max_new_tokens: 500 }
     }
  4. Parse response
  5. Save explanation to Postgres
  6. Return JSON
  ↓
Next.js renders explanation UI
```

### 4. POST /report → Aggregated Summary

```
User clicks "Generate Report"
  ↓
Next.js POST /report {case_ids?: string[]}
  ↓
FastAPI:
  1. Query cases (filter by IDs or all open)
  2. Aggregate: count, avg_risk, status distribution
  3. Optional: Use watsonx.ai to summarize trends
  4. Return summary JSON
  ↓
Next.js renders report dashboard
```

## Error Handling

### Frontend

- Loading states (Suspense, skeletons)
- Error boundaries for crashes
- Toast notifications for API errors
- Retry logic for network failures

### Backend

- Pydantic validation errors → 422
- watsonx.ai timeout → fallback/cached response
- DB connection errors → 503
- Rate limiting → 429

### watsonx.ai Integration

- Timeout after 30 seconds
- Retry with exponential backoff (max 3 attempts)
- Cache responses by case_id (1 hour TTL)
- Budget exceeded → use last known explanation

## Non-Goals (MVP Scope)

❌ Authentication/Authorization (all endpoints public)  
❌ User roles/permissions  
❌ Complex data schemas (keep simple)  
❌ Background job processing  
❌ Real-time WebSocket updates  
❌ Multi-tenancy  
❌ Advanced caching layers

## Future Enhancements (Post-Submission)

### Multi-Agent Orchestration

Use **watsonx Orchestrate** to coordinate:

- **Agent 1**: Transaction analyzer (Granite model)
- **Agent 2**: Compliance checker (regulatory rules)
- **Agent 3**: Customer history analyzer
- **Orchestrator**: Combine insights into final decision

### Advanced Features

- Historical trend analysis with time-series models
- Configurable risk thresholds per institution
- Integration with banking core systems (via OpenAPI)
- Real-time transaction stream processing
- A/B testing different prompt strategies

## Security Notes

- ⚠️ No auth required for MVP (prototype only)
- API keys in environment variables (never commit)
- CORS enabled for Next.js origin only
- Input validation via Pydantic
- SQL injection prevention (SQLAlchemy ORM)

## Performance Targets

- API response time: <3 seconds (including watsonx.ai)
- Frontend load time: <2 seconds
- Database queries: <100ms
- watsonx.ai latency: <2 seconds
- Support: 10 concurrent users (MVP)
