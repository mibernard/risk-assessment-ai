# Project Brief

## Challenge

**AI-powered Risk Assessment & Compliance Assistant**  
IBM SkillsBuild AI Experiential Learning Lab 2025 - Banking Track (Challenge 2)

## Goal

Build a proof-of-concept AI solution that uses IBM watsonx.ai to analyze banking transactions for fraud risk and provide explainable, compliance-ready assessments in real-time.

## Scope

**MVP Features** (8-week timeline):

- Dashboard: View all flagged transactions
- Case Details: Deep-dive into individual cases
- AI Explanation: Real-time risk analysis via watsonx.ai Granite models
- Report Generation: Aggregated insights and compliance summaries

**Future Enhancements** (post-submission):

- Multi-agent orchestration with watsonx Orchestrate
- Historical trend analysis
- Configurable risk thresholds
- Integration with banking systems

## Tech Stack

### Frontend

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **State**: React hooks + fetch API

### Backend

- **Framework**: FastAPI (Python 3.9+)
- **Validation**: Pydantic v2
- **ORM**: SQLAlchemy 2.0
- **AI Integration**: IBM watsonx.ai Python SDK

### Database

- **Provider**: Neon (Serverless Postgres)
- **Schema**: SQLAlchemy models
- **Migrations**: Alembic (optional for MVP)

### AI/ML

- **Platform**: IBM watsonx.ai
- **Model**: IBM Granite-13b-instruct-v2 (approved for SkillsBuild)
- **Integration**: Python SDK + Prompt Lab for development
- **Budget**: $250 USD credits (monitor token usage)

## IBM SkillsBuild Requirements

### Data Compliance

✅ Synthetic/mock data only (no real customer data)  
✅ No personal information (PI)  
✅ No social media data  
✅ Public domain sources with attribution

### Evaluation Criteria (20 points total)

- **Completeness** (5pts): Full watsonx.ai integration, working prototype
- **Creativity** (5pts): Agentic reasoning, multi-step analysis
- **Design/UX** (5pts): Intuitive interface, clear explanations
- **Effectiveness** (5pts): Solves real banking problem, scalable

### Required Deliverables

1. 2-minute video demonstration
2. Written problem/solution statement
3. Link to working prototype
4. Technology documentation
5. GitHub repository (optional but recommended)

## Constraints

### Development

- Prefer simple, typed code (Python type hints, TypeScript strict mode)
- Minimal dependencies (justify each new library)
- Environment-configured URLs (no hardcoded secrets)
- API-first design (keep frontend/backend decoupled)

### IBM-Specific

- Use approved Granite models only (see docs/WATSONX_INTEGRATION.md)
- Track token/CUH consumption to stay within $250 budget
- Save work regularly (account closes Nov 28, 2025)
- Follow watsonx.ai best practices (see IBM documentation)

## Development Phases

**Phase 1: Foundation** (Week 1-2)

- Set up project structure
- Implement in-memory data layer
- Create basic UI with mock responses
- Test watsonx.ai integration in Prompt Lab

**Phase 2: watsonx.ai Integration** (Week 3-4)

- Implement real watsonx.ai SDK calls
- Build prompt engineering pipeline
- Add error handling and fallbacks
- Optimize token usage

**Phase 3: Database & Polish** (Week 5-6)

- Connect Neon Postgres
- Implement data persistence
- Refine UI/UX based on testing
- Add loading states and error handling

**Phase 4: Documentation & Demo** (Week 7-8)

- Record video demonstration
- Write technical documentation
- Prepare presentation materials
- Final testing and bug fixes

## Success Metrics

- ✅ All API endpoints functional
- ✅ Real watsonx.ai responses in <3 seconds
- ✅ UI loads in <2 seconds
- ✅ Token usage <$200 of $250 budget
- ✅ Zero data compliance violations
- ✅ Clean deployment (no errors in logs)
