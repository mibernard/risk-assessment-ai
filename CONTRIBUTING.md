# Contributing

## Development Guidelines

### Code Quality

**1. API Contract Adherence**
- Always follow `docs/API_CONTRACT.md` specifications
- Update contract BEFORE making endpoint changes
- Coordinate backend/frontend changes to maintain compatibility
- Version breaking changes properly (v1.0 → v2.0)

**2. Type Safety**
- Use TypeScript strict mode in frontend
- Use Python type hints in backend (PEP 484)
- Define Pydantic schemas for all API models
- Export TypeScript interfaces for shared types

**3. Minimal Dependencies**
- Justify every new library added
- Prefer standard library solutions
- Check bundle size impact for frontend deps
- Document why dependency is needed in PR

**4. Environment Configuration**
- Use `.env` files (gitignored)
- Never commit secrets or API keys
- Provide `.env.example` as template
- Document all required env vars

**5. Code Style**
- Backend: Follow PEP 8 (Python)
- Frontend: Follow Airbnb style guide (TypeScript/React)
- Use formatters: `black` (Python), `prettier` (TypeScript)
- Run linters before committing

---

## IBM SkillsBuild Compliance

### Data Requirements
✅ **ALLOWED**:
- Synthetic/mock data only
- Public domain datasets (with attribution)
- Self-generated test data

❌ **PROHIBITED**:
- Real customer banking data
- Personal information (PI/PII)
- Company confidential data
- Social media data
- Any data without proper usage rights

### watsonx.ai Usage
- Use approved Granite models only (see `docs/IBM_COMPLIANCE.md`)
- Track token usage to stay within $250 budget
- Implement response caching (1-hour TTL)
- Add fallback logic for API failures

### Code Practices
- Document all watsonx.ai integration points
- Log token consumption for transparency
- Handle errors gracefully (no crashes)
- Include model version in responses

---

## Git Workflow

### Branch Naming
```
feat/dashboard-ui          # New feature
fix/api-cors-error         # Bug fix
chore/update-deps          # Maintenance
docs/watsonx-integration   # Documentation
refactor/simplify-auth     # Code refactoring
```

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: add case detail page with AI explanation
fix: resolve CORS error for /explain endpoint
chore: update FastAPI to v0.120.1
docs: add watsonx.ai integration guide
refactor: simplify risk score calculation
```

**Format**:
```
<type>: <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `chore`: Maintenance (deps, config)
- `refactor`: Code restructuring (no behavior change)
- `test`: Adding/updating tests
- `perf`: Performance improvement

### Pull Request Process

**1. Before Creating PR**:
- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] No linter errors
- [ ] Updated documentation (if needed)
- [ ] No secrets committed
- [ ] Verified data compliance

**2. PR Title**:
Use conventional commit format:
```
feat: implement watsonx.ai explanation endpoint
```

**3. PR Description Template**:
```markdown
## Summary
Brief description of changes

## Changes
- Added `/explain` endpoint
- Integrated watsonx.ai SDK
- Updated API contract

## Testing
- Tested with 10 sample cases
- Verified token tracking works
- Confirmed error handling

## Compliance
- [ ] No real customer data used
- [ ] API keys in environment variables
- [ ] Token usage tracked

## Screenshots (if UI changes)
[Attach screenshots]
```

**4. Review Process**:
- Assign at least one team member
- Address all review comments
- Squash commits before merging (optional)

**5. Merging**:
- Ensure CI passes (if configured)
- Delete branch after merging
- Update project board/todo list

---

## Code Architecture

### Backend (FastAPI)

**File Organization**:
```python
# main.py - Keep routes thin, delegate to services
@app.post("/explain")
async def explain_case(request: ExplainRequest):
    return await watsonx_service.generate_explanation(request.case_id)

# services/watsonx_service.py - Business logic here
class WatsonXService:
    async def generate_explanation(self, case_id: str) -> Explanation:
        # Implementation here
        pass
```

**Best Practices**:
- Keep route handlers under 20 lines
- Extract business logic to service modules
- Use dependency injection for testability
- Add docstrings to all functions
- Type hint all parameters and returns

### Frontend (Next.js)

**Component Organization**:
```
components/
├── ui/              # shadcn/ui primitives
├── CaseTable.tsx    # Feature component
└── RiskBadge.tsx    # Shared utility component
```

**Best Practices**:
- Use server components by default
- Add 'use client' only when needed (interactivity)
- Keep components under 200 lines
- Extract hooks for complex state logic
- Use TypeScript interfaces for props

---

## Testing

### Backend Tests

```python
import pytest
from fastapi.testclient import TestClient

def test_get_cases(client: TestClient):
    """Test GET /cases returns list of cases."""
    response = client.get("/cases")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_explain_case_not_found(client: TestClient):
    """Test POST /explain with invalid case_id returns 404."""
    response = client.post("/explain", json={"case_id": "invalid"})
    assert response.status_code == 404
```

Run tests:
```bash
cd backend
pytest -v
```

### Frontend Tests (Future)

```typescript
import { render, screen } from '@testing-library/react';
import { RiskBadge } from '@/components/RiskBadge';

test('renders high risk badge correctly', () => {
  render(<RiskBadge score={0.85} />);
  expect(screen.getByText(/High Risk/i)).toBeInTheDocument();
});
```

---

## Documentation

### When to Update Docs

Update documentation when:
- Adding new API endpoints → `docs/API_CONTRACT.md`
- Changing architecture → `docs/ARCHITECTURE.md`
- Adding UI screens → `docs/UI_SCREENS.md`
- Updating watsonx.ai integration → `docs/WATSONX_INTEGRATION.md`
- Changing prompts → `docs/AI_PROMPTS.md`

### Documentation Standards

- Use Markdown for all docs
- Include code examples
- Add diagrams for complex flows (ASCII art okay)
- Keep language clear and concise
- Update table of contents if adding sections

---

## Security

### Secrets Management
- Never commit `.env` files
- Use environment variables for all secrets
- Rotate API keys if accidentally committed
- Add `.env` to `.gitignore`

### API Security
- Validate all inputs with Pydantic
- Sanitize error messages (no stack traces to clients)
- Enable CORS only for trusted origins
- Rate limit endpoints (future)

### Data Privacy
- No real customer data in code or commits
- Use synthetic data for testing
- Anonymize any sample data
- Follow IBM compliance guidelines

---

## Performance

### Backend Optimization
- Use database indexes (when adding Postgres)
- Cache watsonx.ai responses (1-hour TTL)
- Implement pagination for large datasets
- Monitor token usage to avoid budget overruns

### Frontend Optimization
- Use Next.js Image component for images
- Implement code splitting (automatic with Next.js)
- Lazy load components when appropriate
- Optimize bundle size (<500KB initial)

---

## Monitoring & Debugging

### Logging
```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Case fetched: %s", case_id)
logger.info("Explanation generated for case %s", case_id)
logger.warning("Token budget at 80%: %s", token_usage)
logger.error("watsonx.ai API error: %s", error)
```

### Error Tracking
- Log all exceptions with context
- Include request IDs for debugging
- Track watsonx.ai failures separately
- Monitor token consumption trends

---

## Deployment Checklist

### Before Deploying

**Backend**:
- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] Health endpoint returns 200
- [ ] Swagger docs accessible
- [ ] CORS configured for frontend URL

**Frontend**:
- [ ] `NEXT_PUBLIC_API_URL` set correctly
- [ ] Build succeeds without errors
- [ ] No console errors in production build
- [ ] All images optimized

**watsonx.ai**:
- [ ] API key valid
- [ ] Token budget not exceeded
- [ ] Prompt Lab sessions exported
- [ ] Fallback logic tested

---

## Team Communication

### Code Reviews
- Be constructive and respectful
- Ask questions, don't make demands
- Approve if changes look good
- Suggest improvements, don't block on style

### Asking for Help
Use project channels:
- **Slack**: Technical questions
- **Coaching sessions**: Progress blockers
- **IBM mentors**: watsonx.ai specific issues
- **Office hours**: Bug troubleshooting

### Sharing Knowledge
- Document solutions in `docs/`
- Share useful resources in team chat
- Update READMEs with setup gotchas
- Create examples for common patterns

---

## Resources

### Project Documentation
- `docs/PROJECT_BRIEF.md` - Overview
- `docs/ARCHITECTURE.md` - System design
- `docs/API_CONTRACT.md` - API specs
- `docs/WATSONX_INTEGRATION.md` - AI integration
- `docs/IBM_COMPLIANCE.md` - Requirements

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [watsonx.ai Docs](https://www.ibm.com/products/watsonx-ai)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python PEP 8](https://pep8.org/)

---

## Questions?

If you're unsure about any guideline, ask in:
- Team Slack channel
- Weekly coaching sessions
- IBM mentor office hours

**Remember**: It's better to ask than to break something! 🙂

