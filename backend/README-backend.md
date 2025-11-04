# Backend (FastAPI)

## Quick Start

### 1. Setup Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=postgresql://user:pass@host/dbname  # Neon Postgres
# For local dev, use: sqlite:///./dev.db

# IBM watsonx.ai
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# CORS
FRONTEND_URL=http://localhost:3000
```

**Get watsonx.ai credentials**:

1. Log in to watsonx.ai: https://dataplatform.cloud.ibm.com/wx/home?context=wx
2. Scroll to "Developer access" section
3. Select "watsonx Challenge Sandbox" project
4. Copy Project ID
5. Create API key and copy

See `docs/WATSONX_INTEGRATION.md` for detailed setup.

### 3. Run Development Server

```bash
uvicorn main:app --reload --port 8000
```

Server runs at: http://localhost:8000  
API docs (Swagger): http://localhost:8000/docs

---

## Project Structure

```
backend/
├── main.py                 # FastAPI app + routes
├── config.py               # Environment configuration
├── database.py             # Database connection
├── models.py               # SQLAlchemy models
├── schemas.py              # Pydantic schemas
├── services/
│   ├── watsonx_service.py  # watsonx.ai integration ⭐
│   ├── prompt_builder.py   # Prompt templates
│   ├── token_tracker.py    # Budget management
│   └── report_generator.py # Report aggregation
├── requirements.txt        # Python dependencies
├── .env                    # Environment vars (gitignored)
└── README-backend.md       # This file
```

---

## Implementation Tasks

### Phase 1: Foundation (In-Memory)

**Goal**: Get API running with mock data before connecting to Postgres/watsonx.ai

**Tasks**:

- [x] Create FastAPI app with CORS
- [ ] Define Pydantic schemas (`schemas.py`)
  - CaseSchema, ExplanationSchema, ReportSchema
  - Match API_CONTRACT.md exactly
- [ ] Create in-memory data store
  - 10-15 sample cases with varied risk scores
  - Store in `CASES` dict with UUID keys
- [ ] Implement routes:
  - `GET /cases` → Return all cases
  - `GET /cases/{id}` → Return single case (404 if not found)
  - `GET /health` → Return {"status": "healthy"}

**Success Criteria**:

- http://localhost:8000/docs shows clean Swagger UI
- All endpoints return correct status codes
- Pydantic validation catches bad requests (422)

### Phase 2: watsonx.ai Integration

**Goal**: Replace mock AI responses with real watsonx.ai calls

**Tasks**:

- [ ] Install IBM SDK: `pip install ibm-watson-machine-learning ibm-cloud-sdk-core`
- [ ] Create `services/watsonx_service.py` (see `docs/WATSONX_INTEGRATION.md`)
- [ ] Create `services/prompt_builder.py` (see `docs/AI_PROMPTS.md`)
- [ ] Create `services/token_tracker.py` (budget management)
- [ ] Implement `POST /explain` endpoint:
  - Validate case_id exists
  - Call watsonx.ai API
  - Parse JSON response
  - Track token usage
  - Return explanation + metadata
- [ ] Add error handling:
  - Timeout (30s max)
  - Budget exceeded (429 error)
  - Malformed response (fallback)
- [ ] Implement response caching (1-hour TTL)

**Success Criteria**:

- `POST /explain` returns real AI responses
- Token usage tracked in `/admin/tokens` endpoint
- Fallback works if AI unavailable
- Response time <3 seconds

### Phase 3: Database Integration

**Goal**: Persist data to Neon Postgres

**Tasks**:

- [ ] Create Neon Postgres database (free tier)
- [ ] Update `DATABASE_URL` in `.env`
- [ ] Create SQLAlchemy models (`models.py`):

  ```python
  class Case(Base):
      __tablename__ = "cases"
      id = Column(UUID, primary_key=True)
      customer_name = Column(String(255))
      amount = Column(Numeric(10, 2))
      country = Column(String(100))
      risk_score = Column(Numeric(3, 2))
      status = Column(String(50))
      created_at = Column(DateTime)
      explanation_generated = Column(Boolean, default=False)
      model_version = Column(String(50), nullable=True)
      tokens_used = Column(Integer, nullable=True)

  class Explanation(Base):
      __tablename__ = "explanations"
      id = Column(UUID, primary_key=True)
      case_id = Column(UUID, ForeignKey("cases.id"))
      confidence = Column(Numeric(3, 2))
      rationale = Column(Text)
      recommended_action = Column(Text)
      model_used = Column(String(100))
      tokens_consumed = Column(Integer)
      created_at = Column(DateTime)
  ```

- [ ] Create database connection (`database.py`)
- [ ] Seed database with sample data
- [ ] Update routes to use database queries
- [ ] Implement `POST /report` endpoint with aggregation

**Success Criteria**:

- Database schema created
- All routes work with Postgres
- Data persists across server restarts

### Phase 4: Report Generation

**Goal**: Implement compliance report endpoint

**Tasks**:

- [ ] Create `services/report_generator.py`
- [ ] Implement SQL aggregation queries:
  - Count by risk level (high/medium/low)
  - Average risk score
  - Total amount
  - Status distribution
- [ ] Optional: Use watsonx.ai to generate summary text
- [ ] Implement `POST /report` endpoint

**Success Criteria**:

- Report generates correct statistics
- Optional AI summary works
- Response time <2 seconds

---

## API Routes

See `docs/API_CONTRACT.md` for full specifications.

**Core Endpoints**:

- `GET /cases` - List all cases
- `GET /cases/{id}` - Get case by ID
- `POST /explain` - Generate AI explanation ⭐
- `POST /report` - Generate compliance report

**Admin Endpoints**:

- `GET /health` - Health check
- `GET /admin/tokens` - Token usage stats

---

## Dependencies

```txt
# Web framework
fastapi==0.120.1
uvicorn==0.38.0

# Database
sqlalchemy==2.0.44
psycopg2-binary==2.9.11  # Postgres driver

# Data validation
pydantic==2.12.3
pydantic-settings==2.0.3

# IBM watsonx.ai
ibm-watson-machine-learning==1.0.355
ibm-cloud-sdk-core==3.16.7

# Utilities
python-dotenv==1.0.0
```

---

## Testing

### Manual Testing

1. **Test in-memory routes**:

```bash
curl http://localhost:8000/cases
curl http://localhost:8000/cases/{some-uuid}
```

2. **Test watsonx.ai integration**:

```bash
curl -X POST http://localhost:8000/explain \
  -H "Content-Type: application/json" \
  -d '{"case_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

3. **Check Swagger UI**:
   Visit http://localhost:8000/docs and test each endpoint interactively.

### Unit Tests (Future)

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_cases():
    response = client.get("/cases")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_explain_case():
    response = client.post("/explain", json={"case_id": "test-id"})
    assert response.status_code == 200
    assert "rationale" in response.json()
```

---

## Development Tips

### 1. Auto-reload on Changes

FastAPI auto-reloads when using `--reload` flag. Edit any Python file and server restarts automatically.

### 2. Swagger UI

Access http://localhost:8000/docs to:

- Test endpoints interactively
- View request/response schemas
- Generate API client code

### 3. Debugging

Add breakpoints and use Python debugger:

```python
import pdb; pdb.set_trace()
```

Or use print statements:

```python
print(f"Case ID: {case_id}, Risk: {risk_score}")
```

### 4. Logging

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Generating explanation for case %s", case_id)
```

### 5. Environment Variables

Never commit `.env` file. Use `.env.example` as template:

```bash
cp .env.example .env
# Edit .env with your credentials
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution**: Activate venv and reinstall dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "WATSONX_API_KEY not set"

**Solution**: Create `.env` file with credentials (see Setup section)

### Issue: "Port 8000 already in use"

**Solution**: Use different port or kill existing process

```bash
uvicorn main:app --reload --port 8001
# Or find and kill process: lsof -ti:8000 | xargs kill
```

### Issue: "Database connection refused"

**Solution**: Check DATABASE_URL in `.env` is correct

### Issue: "Token budget exceeded"

**Solution**: Check usage at http://localhost:8000/admin/tokens

- If near $250 limit, use cached responses
- Contact IBM SkillsBuild support for increase

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [IBM watsonx.ai Integration Guide](../docs/WATSONX_INTEGRATION.md)
- [API Contract](../docs/API_CONTRACT.md)
- [Architecture Diagram](../docs/ARCHITECTURE.md)
