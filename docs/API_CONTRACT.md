# API Contract (v1.0)

**Base URL**: `http://localhost:8000`  
**Content-Type**: `application/json`  
**CORS**: Enabled for `http://localhost:3000` (Next.js dev server)

---

## Data Models

### Case

Represents a flagged banking transaction requiring risk assessment.

```typescript
interface Case {
  id: string; // UUID v4
  customer_name: string; // e.g., "Alice Johnson"
  amount: number; // Transaction amount (USD)
  country: string; // Origin country (ISO 3166-1 alpha-2)
  risk_score: number; // 0.0 - 1.0 (calculated by watsonx.ai)
  status: "new" | "reviewing" | "resolved";
  created_at: string; // ISO 8601 timestamp

  // watsonx.ai metadata (optional, populated after /explain)
  explanation_generated?: boolean;
  model_version?: string; // e.g., "granite-3-2-8b-instruct"
  tokens_used?: number;
}
```

**Validation Rules**:

- `amount`: Must be > 0, max 2 decimal places
- `risk_score`: Between 0.00 and 1.00
- `country`: Valid ISO country code
- `status`: One of enum values only

**Example**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_name": "Alice Johnson",
  "amount": 5300.0,
  "country": "SG",
  "risk_score": 0.82,
  "status": "new",
  "created_at": "2025-01-15T10:30:00Z",
  "explanation_generated": false
}
```

---

### Explanation

AI-generated risk assessment explanation from watsonx.ai.

```typescript
interface Explanation {
  case_id: string; // References Case.id
  confidence: number; // 0.0 - 1.0 (model confidence)
  rationale: string; // Human-readable explanation (2-3 sentences)
  recommended_action: string; // Action for compliance officer

  // watsonx.ai tracking
  model_used: string; // "ibm/granite-3-2-8b-instruct"
  tokens_consumed: number; // Token count for this request
  generation_time_ms: number; // Latency measurement
  created_at: string; // ISO 8601 timestamp
}
```

**Example**:

```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "confidence": 0.89,
  "rationale": "Transaction involves high-risk country with amount significantly above customer's typical domestic transfers. Pattern inconsistent with 6-month transaction history.",
  "recommended_action": "Hold transaction for 24h. Request ID verification, proof of address, and source of funds documentation.",
  "model_used": "ibm/granite-3-2-8b-instruct",
  "tokens_consumed": 342,
  "generation_time_ms": 1847,
  "created_at": "2025-01-15T10:31:00Z"
}
```

---

### Report

Aggregated statistics for compliance reporting.

```typescript
interface Report {
  summary: string; // Natural language summary (watsonx.ai optional)
  high_risk_count: number; // Cases with risk_score >= 0.7
  medium_risk_count: number; // Cases with 0.4 <= risk_score < 0.7
  low_risk_count: number; // Cases with risk_score < 0.4
  avg_risk: number; // Mean risk_score (0.0 - 1.0)
  total_cases: number;
  total_amount: number; // Sum of all case amounts (USD)

  // Status breakdown
  status_distribution: {
    new: number;
    reviewing: number;
    resolved: number;
  };

  // Time range
  period_start: string; // ISO 8601
  period_end: string; // ISO 8601
}
```

**Example**:

```json
{
  "summary": "48 high-risk transactions detected in the past 7 days, primarily from Southeast Asian regions. Recommend increased monitoring of cross-border transfers >$5000.",
  "high_risk_count": 48,
  "medium_risk_count": 127,
  "low_risk_count": 1825,
  "avg_risk": 0.34,
  "total_cases": 2000,
  "total_amount": 8450000.0,
  "status_distribution": {
    "new": 243,
    "reviewing": 512,
    "resolved": 1245
  },
  "period_start": "2025-01-08T00:00:00Z",
  "period_end": "2025-01-15T23:59:59Z"
}
```

---

## API Endpoints

### 1. List All Cases

**GET** `/cases`

Retrieve all flagged transactions (paginated in production).

**Query Parameters** (optional for MVP):

- `status`: Filter by status (`new`, `reviewing`, `resolved`)
- `min_risk`: Minimum risk_score (0.0 - 1.0)
- `limit`: Max results (default: 100)

**Response**: `200 OK`

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "customer_name": "Alice Johnson",
    "amount": 5300.0,
    "country": "SG",
    "risk_score": 0.82,
    "status": "new",
    "created_at": "2025-01-15T10:30:00Z"
  }
]
```

**Errors**:

- `500`: Database connection error

---

### 2. Get Case by ID

**GET** `/cases/{case_id}`

Retrieve detailed information for a specific case.

**Path Parameters**:

- `case_id` (string, UUID): The case identifier

**Response**: `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_name": "Alice Johnson",
  "amount": 5300.0,
  "country": "SG",
  "risk_score": 0.82,
  "status": "new",
  "created_at": "2025-01-15T10:30:00Z",
  "explanation_generated": true,
  "model_version": "granite-3-2-8b-instruct"
}
```

**Errors**:

- `404`: Case not found
- `422`: Invalid UUID format

---

### 3. Generate AI Explanation ⭐

**POST** `/explain`

Request watsonx.ai to generate a risk assessment explanation for a case.

**Request Body**:

```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response**: `200 OK`

```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "confidence": 0.89,
  "rationale": "Transaction involves high-risk country with amount significantly above customer's typical domestic transfers.",
  "recommended_action": "Hold transaction for 24h. Request ID verification.",
  "model_used": "ibm/granite-3-2-8b-instruct",
  "tokens_consumed": 342,
  "generation_time_ms": 1847,
  "created_at": "2025-01-15T10:31:00Z"
}
```

**Errors**:

- `404`: Case not found
- `422`: Invalid case_id format
- `503`: watsonx.ai service unavailable (fallback to cached)
- `429`: Rate limit exceeded (budget exhausted)

**Notes**:

- First call generates new explanation (calls watsonx.ai)
- Subsequent calls return cached explanation (1-hour TTL)
- Tracks token usage against $250 budget

---

### 4. Generate Report

**POST** `/report`

Generate aggregated statistics and optional AI summary.

**Request Body** (optional):

```json
{
  "case_ids": ["550e8400-...", "660e9500-..."], // Optional: specific cases
  "include_ai_summary": true // Optional: use watsonx.ai for summary
}
```

**Default Behavior**: If `case_ids` omitted, reports on all cases with `status != "resolved"`.

**Response**: `200 OK`

```json
{
  "summary": "48 high-risk transactions detected...",
  "high_risk_count": 48,
  "medium_risk_count": 127,
  "low_risk_count": 1825,
  "avg_risk": 0.34,
  "total_cases": 2000,
  "total_amount": 8450000.0,
  "status_distribution": {
    "new": 243,
    "reviewing": 512,
    "resolved": 1245
  },
  "period_start": "2025-01-08T00:00:00Z",
  "period_end": "2025-01-15T23:59:59Z"
}
```

**Errors**:

- `422`: Invalid case_ids format
- `500`: Database aggregation error

---

## Health & Monitoring

### Health Check

**GET** `/health`

**Response**: `200 OK`

```json
{
  "status": "healthy",
  "database": "connected",
  "watsonx_api": "available",
  "token_budget_remaining": 187.43
}
```

### Token Usage

**GET** `/admin/tokens`

**Response**: `200 OK`

```json
{
  "total_budget_usd": 250.0,
  "spent_usd": 62.57,
  "remaining_usd": 187.43,
  "tokens_used": 625700,
  "requests_count": 1834
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here",
  "error_code": "CASE_NOT_FOUND",
  "timestamp": "2025-01-15T10:31:00Z"
}
```

**Common Error Codes**:

- `CASE_NOT_FOUND`: Requested case_id doesn't exist
- `INVALID_UUID`: Malformed UUID in request
- `WATSONX_TIMEOUT`: AI service took >30s to respond
- `BUDGET_EXCEEDED`: $250 token budget exhausted
- `DB_CONNECTION_ERROR`: Postgres connection failed

---

## Rate Limiting (Future)

Current MVP: No rate limiting  
Production: 100 requests/minute per IP

---

## Versioning

Current version: **v1.0**  
All endpoints may include `/v1/` prefix in production deployment.

Breaking changes will increment major version (v2.0, etc.)
