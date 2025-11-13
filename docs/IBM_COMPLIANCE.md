# IBM SkillsBuild Compliance & Requirements

## Overview

This document outlines all IBM SkillsBuild-specific requirements, data compliance guidelines, and evaluation criteria for the AI Experiential Learning Lab 2025.

---

## Critical Compliance Requirements

### ⚠️ Data Restrictions

**PROHIBITED DATA SOURCES**:
- ❌ Real customer banking data
- ❌ Personal information (PI) or PII
- ❌ Company confidential information
- ❌ Client data from any organization
- ❌ Social media data (Twitter, Facebook, etc.)
- ❌ Any data without proper usage rights

**ALLOWED DATA SOURCES**:
- ✅ Synthetic/mock data generated for this project
- ✅ Public domain datasets (with attribution)
- ✅ Data from websites with commercial use terms
- ✅ Self-created test data

**Required Actions**:
1. Document all data sources in `DATA_SOURCES.md`
2. Keep list of website URLs if using public data
3. Ensure all data is synthetic (no real customer names)
4. Get team approval before adding any external data

---

## watsonx.ai Service Limitations

### Approved Models

**✅ ALLOWED**:
- `ibm/granite-3-1-8b-instruct`
- `ibm/granite-3-2-8b-instruct`
- `ibm/granite-13b-chat-v2`
- `ibm/granite-20b-multilingual`
- `meta-llama/llama-3-70b-instruct`
- `meta-llama/llama-3-1-70b-instruct`
- `mistral-small-3-1-22b-instruct-2409`

**❌ PROHIBITED** (will negatively impact evaluation):
- `llama-3-405b-instruct`
- `mistral-large`
- `mistral-medium-2502`
- `mixtral-8x7b-instruct-v01`
- `mistral-small-3-1-24b-instruct-2503`
- `pixtral-12b`

**Recommended for this project**: `ibm/granite-3-2-8b-instruct`

### Budget & Token Management

**Allocation**: $250 USD credits per team

**Token Pricing**:
- Text generation: $0.0001 per 1,000 tokens (1 RU)
- Notebook runtime (CUH): $1.02 per Capacity Unit Hour

**Budget Alerts**:
- Email notifications at: 25%, 50%, 80%, 100% usage
- Account suspended at 100% (can appeal via form)
- Notifications sent hourly (may exhaust before alert)

**Best Practices**:
1. Monitor usage via `/admin/tokens` endpoint
2. Use lower token limits (`max_new_tokens=500`)
3. Cache responses to avoid duplicate calls
4. Avoid running Jupyter notebooks 24/7
5. Select lowest runtime environment for notebooks
6. Test prompts in Prompt Lab before deploying

### Out-of-Scope Features

**NOT AVAILABLE** for this lab:
- ❌ Agent Studio (Beta)
- ❌ Deployment spaces (deploy on IBM Cloud/watsonx.ai)
- ❌ Bring your own model (BYOM)
- ❌ Model fine-tuning
- ❌ AutoAI pipeline
- ❌ SPSS Modeler
- ❌ Federated Learning
- ❌ Cloud Object Storage service

**Allowed**: Prompt Lab, Python SDK, API calls, Jupyter notebooks (with caution)

---

## Evaluation Criteria

Your project will be scored by IBM evaluators on **20 points total** across 4 dimensions:

### 1. Completeness & Feasibility (5 points)

**What evaluators look for**:
- ✅ All planned features are functional (not just mock UI)
- ✅ watsonx.ai integration is real (not hardcoded responses)
- ✅ Proof-of-concept is complete and deployable
- ✅ Clear application of IBM technology (watsonx.ai)
- ✅ Technical implementation is realistic and feasible

**How to maximize score**:
- Show real watsonx.ai API calls in demo video
- Include `/admin/tokens` endpoint showing usage
- Document architecture clearly (ARCHITECTURE.md)
- Ensure all API endpoints work end-to-end
- Add token tracking dashboard in UI

### 2. Creativity & Innovation (5 points)

**What evaluators look for**:
- ✅ Unique approach to risk assessment problem
- ✅ Novel use of AI (not just basic text generation)
- ✅ Differentiated from existing solutions
- ✅ Original prompt engineering strategies
- ✅ Creative UI/UX for presenting AI insights

**How to maximize score**:
- Show agentic reasoning (multi-step analysis)
- Implement confidence scoring visualization
- Add explainability features (why this risk score?)
- Use watsonx.ai for both explanation + summary
- Highlight unique features in demo video

### 3. Design & Usability (5 points)

**What evaluators look for**:
- ✅ Intuitive user interface (easy to navigate)
- ✅ Professional design (not prototype-looking)
- ✅ Clear presentation of AI explanations
- ✅ Fast, responsive interactions
- ✅ Ready for real-world use by compliance officers

**How to maximize score**:
- Use shadcn/ui for polished components
- Add loading states (skeletons, spinners)
- Show error handling gracefully
- Use color coding for risk levels (green/yellow/red)
- Include helpful tooltips and context

### 4. Effectiveness & Efficiency (5 points)

**What evaluators look for**:
- ✅ Solves the stated banking challenge
- ✅ Achieves measurable impact (time savings, accuracy)
- ✅ Efficient use of AI (not wasteful token usage)
- ✅ Scalable to more users/transactions
- ✅ Potential for production deployment

**How to maximize score**:
- Include metrics in report (X cases analyzed, Y% accuracy)
- Show token usage efficiency (<$200 of $250)
- Demonstrate response caching (reduces costs)
- Document scalability considerations
- Highlight future enhancement roadmap

---

## Required Deliverables

### 1. Video Demonstration (2 minutes)

**Must include**:
- Problem statement (15 seconds)
- Solution overview (30 seconds)
- Live demo of key features (60 seconds)
  - Dashboard with flagged cases
  - Click case → AI explanation
  - Generate report
- Key technologies used (15 seconds)

**Tips**:
- Show real watsonx.ai responses (not mock data)
- Highlight IBM Granite model usage
- Demonstrate token tracking
- Keep under 2 minutes (will be cut off)

**Tools**: Loom, Zoom recording, OBS, QuickTime

### 2. Written Problem & Solution Statement

**Structure**:
```markdown
# Problem Statement
Banking institutions process millions of transactions daily...
[2-3 paragraphs on the challenge]

# Proposed Solution
Our AI-powered risk assessment system uses IBM watsonx.ai...
[3-4 paragraphs on approach]

# Key Features
- Real-time risk scoring via Granite-13b-instruct-v2
- Explainable AI with compliance-ready rationales
- Automated report generation
[Bullet list of features]

# Technical Implementation
- Frontend: Next.js 14 + TypeScript
- Backend: FastAPI + Python
- AI: IBM watsonx.ai (Granite model)
- Database: Neon Postgres
[Architecture overview]
```

**Length**: 500-1000 words

### 3. Link to Working Prototype

**Options**:
- Deployed backend + frontend (recommended)
- Video showing localhost deployment
- Provide setup instructions if not deployed

**Deployment suggestions**:
- Frontend: Vercel (free)
- Backend: Render.com (free tier)
- Database: Neon (free tier)

### 4. Technology Documentation

**Must document**:
- watsonx.ai model used (`granite-3-2-8b-instruct`)
- Prompt engineering approach
- Token usage statistics
- Architecture diagram
- API contract

**Reference existing docs**:
- `docs/ARCHITECTURE.md`
- `docs/WATSONX_INTEGRATION.md`
- `docs/API_CONTRACT.md`

### 5. GitHub Repository (Optional but Recommended)

**Include**:
- Clean, organized code
- README with setup instructions
- All documentation files
- `.env.example` file
- No secrets committed

**Bonus points for**:
- CI/CD pipeline
- Unit tests
- Deployment scripts
- Contribution guidelines

---

## IBM Cloud Account Management

### Account Lifecycle

**Created**: Upon team formation  
**Expires**: November 28, 2025  
**Access**: All team members receive invite email

**Important**:
- Only ONE account per team (not per member)
- Account cannot be recovered after expiration
- Save all work before November 28

### Saving Your Work

**Before November 28, 2025**:

1. **Export Prompt Lab sessions**:
   - Go to project "Overview" tab
   - Click "Export or import project" dropdown
   - Select "Export project"
   - Download ZIP file

2. **Save code locally**:
   - Push to GitHub (private or public)
   - Download all files to local machine

3. **Document credentials**:
   - Copy API keys (for future personal account)
   - Screenshot token usage stats
   - Export project configuration

**What gets deleted**:
- All prompt sessions
- Notebook files
- Project configurations
- API keys
- Token budget data

---

## Team Roles & Collaboration

### Recommended Roles (1-5 members)

**Team Lead**:
- Coordinates meetings
- Manages timeline
- Ensures deliverables completed

**Research Lead**:
- Explores watsonx.ai capabilities
- Tests prompt strategies
- Documents best practices

**Solution Designer**:
- Designs UI/UX
- Creates architecture diagrams
- Plans user flows

**Technical Lead**:
- Implements watsonx.ai integration
- Manages backend development
- Handles deployment

**Communications Lead**:
- Records demo video
- Writes documentation
- Prepares presentation

**Note**: Small teams can combine roles

### Team Communication

**Required**:
- Weekly team meetings (minimum)
- Regular progress updates
- Task distribution

**Provided**:
- Slack channel for support
- Weekly coaching sessions
- IBM mentor office hours

**Use these resources**:
- Project coaching: 30min weekly (progress check)
- IBM SME mentoring: 60min on-demand (technical help)
- Office hours: 60min weekly (bug troubleshooting)

---

## Submission Checklist

Before submitting, verify:

**Technical Requirements**:
- [ ] watsonx.ai integration functional (not mock)
- [ ] All API endpoints working
- [ ] Frontend deployed and accessible
- [ ] Database persists data
- [ ] Token usage within budget (<$250)

**Data Compliance**:
- [ ] No real customer data
- [ ] No personal information (PI)
- [ ] All data sources documented
- [ ] Public data properly attributed

**Deliverables**:
- [ ] 2-minute video recorded
- [ ] Problem/solution statement written
- [ ] Prototype link provided
- [ ] Technology documentation complete
- [ ] GitHub repository shared (optional)

**Evaluation Readiness**:
- [ ] Demo shows real AI responses
- [ ] Unique features highlighted
- [ ] Professional UI design
- [ ] Measurable impact demonstrated
- [ ] Scalability considerations documented

---

## Support Resources

### IBM SkillsBuild Platform
- Weekly coaching sessions
- IBM mentor bookings
- Technical office hours
- Slack support channel

### watsonx.ai Resources
- [Prompt Lab](https://dataplatform.cloud.ibm.com/wx/home?context=wx)
- [Granite Model Docs](https://www.ibm.com/products/watsonx-ai/foundation-models)
- [Python SDK Reference](https://ibm.github.io/watson-machine-learning-sdk/)
- [Prompt Tips](https://www.ibm.com/docs/en/watsonx-as-a-service?topic=lab-prompt-tips)

### Project Documentation
- `docs/PROJECT_BRIEF.md` - Project overview
- `docs/ARCHITECTURE.md` - System design
- `docs/WATSONX_INTEGRATION.md` - Technical guide
- `docs/API_CONTRACT.md` - API specifications
- `docs/AI_PROMPTS.md` - Prompt templates

---

## Frequently Asked Questions

### Q: Can I use my personal IBM Cloud account?
**A**: No, you must use the provided team account for evaluation purposes. Personal accounts won't have the required credits.

### Q: What happens if we exceed $250 budget?
**A**: Account will be suspended. You can appeal via form in suspension email, but approval not guaranteed. Plan usage carefully.

### Q: Can we deploy the final solution?
**A**: Yes! Deploy frontend/backend for easier evaluation. Just don't deploy to IBM Cloud (not available).

### Q: Is it okay to have mock data initially?
**A**: Yes, start with mocks. But final submission MUST use real watsonx.ai calls. Evaluators will check.

### Q: Can we use other AI models (OpenAI, Anthropic)?
**A**: No, you must use IBM watsonx.ai models. This is a core requirement.

### Q: What if our team loses access to the account?
**A**: Contact IBM SkillsBuild support immediately via Slack channel or coach.

---

## Version History

- **v1.0** (2025-01-15): Initial documentation for AI Experiential Learning Lab 2025

