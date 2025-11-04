# Getting Started

Welcome to the AI Risk Assessment & Compliance Assistant project for IBM SkillsBuild AI Experiential Learning Lab 2025!

This guide will help you understand the project structure and get started with development.

---

## 📚 Documentation Overview

### Essential Reading (Start Here)

1. **[PROJECT_BRIEF.md](./PROJECT_BRIEF.md)** - Project overview, goals, tech stack, and timeline
2. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design, data flow, and component details
3. **[API_CONTRACT.md](./API_CONTRACT.md)** - Complete API specifications with examples
4. **[WATSONX_INTEGRATION.md](./WATSONX_INTEGRATION.md)** - IBM watsonx.ai integration guide
5. **[IBM_COMPLIANCE.md](./IBM_COMPLIANCE.md)** - IBM SkillsBuild requirements and evaluation criteria

### Feature Specifications

6. **[UI_SCREENS.md](./UI_SCREENS.md)** - UI acceptance criteria and design guidelines
7. **[AI_PROMPTS.md](./AI_PROMPTS.md)** - Prompt engineering templates and examples

### Development Guides

8. **[backend/README-backend.md](../backend/README-backend.md)** - Backend setup and implementation tasks
9. **[frontend/README-frontend.md](../frontend/README-frontend.md)** - Frontend setup and implementation tasks
10. **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Development guidelines and best practices

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 18+** (for frontend)
- **Git** (for version control)
- **VS Code** (recommended) or your preferred IDE
- **IBM Cloud account** (team account from IBM SkillsBuild)

### Step 1: Get watsonx.ai Credentials

1. Log in to watsonx.ai: https://dataplatform.cloud.ibm.com/wx/home?context=wx
2. Scroll to "Developer access" section
3. Select project: "watsonx Challenge Sandbox"
4. Copy **Project ID**
5. Click "Create API key" → Name it → Copy **API Key**
6. Save these for Step 3

### Step 2: Clone Repository

```bash
git clone https://github.com/your-team/risk-assessment-ai.git
cd risk-assessment-ai
```

### Step 3: Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=sqlite:///./dev.db
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
FRONTEND_URL=http://localhost:3000
EOF

# Edit .env and add your actual credentials
# (Open .env in text editor and replace placeholders)

# Run server
uvicorn main:app --reload
```

Backend should now be running at http://localhost:8000  
Check API docs at http://localhost:8000/docs

### Step 4: Setup Frontend

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run dev server
npm run dev
```

Frontend should now be running at http://localhost:3000

---

## 📋 Implementation Roadmap

### Week 1-2: Foundation

**Backend**:
- [ ] Define Pydantic schemas (`schemas.py`)
- [ ] Create in-memory data store with 10-15 sample cases
- [ ] Implement `GET /cases` endpoint
- [ ] Implement `GET /cases/{id}` endpoint
- [ ] Verify Swagger docs at `/docs`

**Frontend**:
- [ ] Install shadcn/ui components
- [ ] Create API client (`lib/api.ts`)
- [ ] Build reusable components (RiskBadge, LoadingState, ErrorState)
- [ ] Implement dashboard page (`/dashboard`)

### Week 3-4: watsonx.ai Integration

**Backend**:
- [ ] Create `services/watsonx_service.py`
- [ ] Create `services/prompt_builder.py`
- [ ] Create `services/token_tracker.py`
- [ ] Implement `POST /explain` endpoint
- [ ] Test in Prompt Lab first
- [ ] Add error handling and fallbacks

**Frontend**:
- [ ] Implement case detail page (`/cases/[id]`)
- [ ] Add "Explain this case" button
- [ ] Display AI explanations
- [ ] Show loading/error states

### Week 5-6: Database & Polish

**Backend**:
- [ ] Create Neon Postgres database
- [ ] Define SQLAlchemy models (`models.py`)
- [ ] Implement database connection (`database.py`)
- [ ] Migrate in-memory data to Postgres
- [ ] Implement `POST /report` endpoint
- [ ] Add token usage tracking endpoint

**Frontend**:
- [ ] Implement report page (`/report`)
- [ ] Add statistics visualizations
- [ ] Polish UI/UX (loading states, error handling)
- [ ] Add responsive design

### Week 7-8: Documentation & Demo

**Both**:
- [ ] Deploy backend (Render/Railway)
- [ ] Deploy frontend (Vercel)
- [ ] Final testing and bug fixes
- [ ] Record 2-minute demo video
- [ ] Write problem/solution statement
- [ ] Prepare presentation materials
- [ ] Submit to IBM SkillsBuild

---

## 🏗️ Project Structure

```
risk-assessment-ai/
├── docs/                          # 📚 Documentation
│   ├── PROJECT_BRIEF.md           # Project overview
│   ├── ARCHITECTURE.md            # System design
│   ├── API_CONTRACT.md            # API specifications
│   ├── WATSONX_INTEGRATION.md     # AI integration guide
│   ├── IBM_COMPLIANCE.md          # IBM requirements
│   ├── UI_SCREENS.md              # UI specifications
│   ├── AI_PROMPTS.md              # Prompt templates
│   └── GETTING_STARTED.md         # This file
│
├── backend/                       # 🐍 FastAPI Backend
│   ├── main.py                    # FastAPI app + routes
│   ├── config.py                  # Environment config
│   ├── database.py                # Database connection
│   ├── models.py                  # SQLAlchemy models
│   ├── schemas.py                 # Pydantic schemas
│   ├── services/                  # Business logic
│   │   ├── watsonx_service.py     # watsonx.ai integration ⭐
│   │   ├── prompt_builder.py      # Prompt templates
│   │   ├── token_tracker.py       # Budget management
│   │   └── report_generator.py    # Report aggregation
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Environment vars (gitignored)
│   └── README-backend.md          # Backend guide
│
├── frontend/                      # ⚛️ Next.js Frontend
│   ├── app/                       # Pages (App Router)
│   │   ├── dashboard/page.tsx     # Case list ⭐
│   │   ├── cases/[id]/page.tsx    # Case detail ⭐
│   │   └── report/page.tsx        # Compliance report ⭐
│   ├── components/                # React components
│   │   ├── ui/                    # shadcn/ui primitives
│   │   ├── CaseTable.tsx          # Case table
│   │   ├── RiskBadge.tsx          # Risk score badge
│   │   ├── LoadingState.tsx       # Loading skeleton
│   │   └── ErrorState.tsx         # Error message
│   ├── lib/
│   │   └── api.ts                 # API client
│   ├── .env.local                 # Environment vars (gitignored)
│   └── README-frontend.md         # Frontend guide
│
├── .env.example                   # Environment template
├── CONTRIBUTING.md                # Development guidelines
└── README.md                      # Project README
```

---

## 🎯 Key Features to Implement

### 1. Dashboard (`/dashboard`)
- Display all flagged transactions in a table
- Color-coded risk scores (red/yellow/green)
- Clickable rows navigate to case detail
- "Generate Report" button

### 2. Case Detail (`/cases/[id]`)
- Show transaction details
- "Explain this case" button
- Display AI-generated explanation:
  - Rationale (2-3 sentences)
  - Recommended action
  - Confidence score
  - Model name + token count

### 3. Compliance Report (`/report`)
- Aggregate statistics:
  - Total cases
  - High/medium/low risk counts
  - Average risk score
  - Status distribution
- Optional: AI-generated summary

### 4. watsonx.ai Integration
- Real-time risk assessment explanations
- IBM Granite-13b-instruct-v2 model
- Token usage tracking (<$250 budget)
- Response caching (1-hour TTL)
- Fallback logic for errors

---

## 🛠️ Development Workflow

### Daily Development

1. **Pull latest changes**:
   ```bash
   git pull origin main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feat/your-feature-name
   ```

3. **Make changes and commit**:
   ```bash
   git add .
   git commit -m "feat: add dashboard page"
   ```

4. **Push and create PR**:
   ```bash
   git push origin feat/your-feature-name
   # Create PR on GitHub
   ```

5. **After PR approved, merge and delete branch**

### Testing Your Changes

**Backend**:
```bash
# Check Swagger docs
open http://localhost:8000/docs

# Test endpoint
curl http://localhost:8000/cases
```

**Frontend**:
```bash
# Check in browser
open http://localhost:3000/dashboard

# Check console for errors
# Check Network tab for API calls
```

### Before Committing

- [ ] Code follows style guidelines
- [ ] No linter errors
- [ ] API docs render correctly
- [ ] No secrets committed
- [ ] Updated documentation (if needed)

---

## 📞 Getting Help

### Team Resources

- **Slack Channel**: Technical questions and discussions
- **Weekly Coaching**: Progress check-ins and blockers
- **IBM Mentors**: Book 1-on-1 sessions for watsonx.ai help
- **Office Hours**: Weekly bug troubleshooting sessions

### Common Issues & Solutions

**Issue**: "WATSONX_API_KEY not set"  
**Solution**: Create `.env` file in backend/ with your credentials

**Issue**: "CORS error when calling API"  
**Solution**: Check FRONTEND_URL in backend/.env matches frontend port

**Issue**: "Module not found: @/components/ui/..."  
**Solution**: Run `npx shadcn-ui@latest add [component-name]`

**Issue**: "Token budget exceeded"  
**Solution**: Check usage at `/admin/tokens`, implement caching

### Documentation Index

- **Setup**: [backend/README-backend.md](../backend/README-backend.md), [frontend/README-frontend.md](../frontend/README-frontend.md)
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **API**: [API_CONTRACT.md](./API_CONTRACT.md)
- **watsonx.ai**: [WATSONX_INTEGRATION.md](./WATSONX_INTEGRATION.md)
- **IBM Requirements**: [IBM_COMPLIANCE.md](./IBM_COMPLIANCE.md)
- **UI Design**: [UI_SCREENS.md](./UI_SCREENS.md)
- **Prompts**: [AI_PROMPTS.md](./AI_PROMPTS.md)
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## ✅ Pre-Submission Checklist

8 weeks from now, before submitting to IBM:

### Technical
- [ ] All API endpoints functional
- [ ] Real watsonx.ai integration (not mock)
- [ ] Frontend deployed and accessible
- [ ] Database persists data
- [ ] Token usage <$250
- [ ] No console errors

### Data Compliance
- [ ] No real customer data
- [ ] No personal information
- [ ] All data sources documented
- [ ] Approved Granite models only

### Deliverables
- [ ] 2-minute video demonstration
- [ ] Problem/solution statement written
- [ ] Prototype link provided
- [ ] Technology documentation complete
- [ ] GitHub repository clean

### Quality
- [ ] Professional UI design
- [ ] Fast response times (<3s)
- [ ] Error handling works
- [ ] Mobile responsive
- [ ] Accessibility tested

---

## 🎉 Ready to Start?

1. Read [PROJECT_BRIEF.md](./PROJECT_BRIEF.md) for context
2. Review [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
3. Follow **Quick Start** above to set up your environment
4. Check [backend/README-backend.md](../backend/README-backend.md) for backend tasks
5. Check [frontend/README-frontend.md](../frontend/README-frontend.md) for frontend tasks

**Good luck, and let's build something amazing! 🚀**

---

## 📝 Revision History

- **v1.0** (2025-01-15): Initial documentation for IBM SkillsBuild 2025

