# AI Risk Assessment & Compliance Assistant

> **IBM SkillsBuild AI Experiential Learning Lab 2025** - Banking Track  
> AI-powered banking transaction risk assessment using IBM watsonx.ai Granite models

[![FastAPI](https://img.shields.io/badge/FastAPI-0.120-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?logo=next.js)](https://nextjs.org/)
[![IBM watsonx.ai](https://img.shields.io/badge/IBM-watsonx.ai-0f62fe?logo=ibm)](https://www.ibm.com/products/watsonx-ai)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

---

## 🎯 Project Overview

A proof-of-concept AI solution that analyzes banking transactions for fraud risk and provides explainable, compliance-ready assessments in real-time. Built for the IBM SkillsBuild AI Experiential Learning Lab 2025.

### Key Features

- 🏦 **Real-time Risk Assessment** - Analyze flagged banking transactions
- 🤖 **AI-Powered Explanations** - IBM watsonx.ai Granite models provide intelligent insights
- 📊 **Compliance Reports** - Generate aggregated statistics and summaries
- ⚡ **Fast & Modern Stack** - Next.js + FastAPI + Neon Postgres
- 🔒 **IBM Compliant** - Follows all IBM SkillsBuild data and evaluation requirements

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- Python 3.10+
- Node.js 18+
- IBM watsonx.ai account

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-team/risk-assessment-ai.git
cd risk-assessment-ai

# Backend setup
cd backend
python -m venv venv

For MacOS/Linux:
source venv/bin/activate
#install requirements
pip install -r requirements.txt

For Windows:
# Activate venv
.\venv\Scripts\Activate.ps1
# If activation is blocked, change execution policy and activate again:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
#install requirements
pip install -r requirements.txt


# Create .env file
DATABASE_URL=sqlite:///./dev.db
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
FRONTEND_URL=http://localhost:3000


# Frontend setup (in new terminal)
cd ../frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 2. Get watsonx.ai Credentials

1. Go to https://dataplatform.cloud.ibm.com/wx/home?context=wx
2. Navigate to "Developer access" section
3. Select project: **"AI Experimental Learning Labs Sandbox"**
4. Copy **Project ID** and create **API Key**
5. Update `backend/.env` with your credentials

### 3. Run the Application

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Access the app:**

- 🎨 Frontend: http://localhost:3000
- 🔧 API Docs: http://localhost:8000/docs
- ✅ Health Check: http://localhost:8000/health

---

## 📚 Documentation

### Getting Started

- 📖 **[Complete Setup Guide](docs/GETTING_STARTED.md)** - Comprehensive onboarding (start here!)
- 🏗️ **[Architecture Overview](docs/ARCHITECTURE.md)** - System design and data flow
- 📝 **[API Contract](docs/API_CONTRACT.md)** - Complete API specifications

### IBM SkillsBuild Specific

- ✅ **[IBM Compliance Guide](docs/IBM_COMPLIANCE.md)** - Requirements and evaluation criteria
- 🤖 **[watsonx.ai Integration](docs/WATSONX_INTEGRATION.md)** - AI setup and usage
- 💬 **[AI Prompt Templates](docs/AI_PROMPTS.md)** - Prompt engineering guide

### Development Guides

- 🐍 **[Backend README](backend/README-backend.md)** - FastAPI setup and implementation
- ⚛️ **[Frontend README](frontend/README-frontend.md)** - Next.js setup and implementation
- 🎨 **[UI Specifications](docs/UI_SCREENS.md)** - Design and acceptance criteria
- 🤝 **[Contributing Guide](CONTRIBUTING.md)** - Development guidelines

### Quick References

- 🎯 **[Project Brief](docs/PROJECT_BRIEF.md)** - Goals, tech stack, timeline

---

## 🏗️ Tech Stack

### Frontend

- **Next.js 14** (App Router) - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components

### Backend

- **FastAPI** - Python web framework
- **Pydantic v2** - Data validation
- **SQLAlchemy 2.0** - ORM
- **Uvicorn** - ASGI server

### AI/Database

- **IBM watsonx.ai** - Granite-13b-instruct-v2 model
- **Neon Postgres** - Serverless database
- **IBM Watson SDK** - AI integration

---

## 📁 Project Structure

```
risk-assessment-ai/
├── docs/                        # 📚 Comprehensive documentation
│   ├── GETTING_STARTED.md       # Start here for full setup
│   ├── PROJECT_BRIEF.md         # Project overview
│   ├── ARCHITECTURE.md          # System design
│   ├── API_CONTRACT.md          # API specifications
│   ├── WATSONX_INTEGRATION.md   # AI integration guide
│   ├── IBM_COMPLIANCE.md        # IBM requirements
│   ├── UI_SCREENS.md            # UI specifications
│   └── AI_PROMPTS.md            # Prompt templates
│
├── backend/                     # 🐍 FastAPI Backend
│   ├── main.py                  # API routes (6 endpoints)
│   ├── schemas.py               # Pydantic validation schemas
│   ├── config.py                # Environment configuration
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # Environment variables (create this!)
│   └── README-backend.md        # Backend setup guide
│
├── frontend/                    # ⚛️ Next.js Frontend
│   ├── app/
│   │   ├── page.tsx             # Landing page
│   │   ├── dashboard/page.tsx   # Main dashboard with case table
│   │   └── layout.tsx           # Root layout
│   ├── components/              # React components
│   │   ├── RiskBadge.tsx        # Risk score badge
│   │   ├── StatusBadge.tsx      # Status indicator
│   │   ├── LoadingState.tsx     # Loading UI
│   │   └── ErrorState.tsx       # Error handling
│   ├── lib/
│   │   └── api.ts               # API client with TypeScript types
│   ├── .env.local               # Frontend env vars (create this!)
│   └── README-frontend.md       # Frontend setup guide
│
├── CONTRIBUTING.md              # Development guidelines
└── README.md                    # This file
```

---


## 🧪 Testing the API

### Via Swagger UI

Open http://localhost:8000/docs and test interactively

### Via curl

```bash
# Get all cases
curl http://localhost:8000/cases

# Get specific case
curl http://localhost:8000/cases/550e8400-e29b-41d4-a716-446655440000

# Generate explanation
curl -X POST http://localhost:8000/explain \
  -H "Content-Type: application/json" \
  -d '{"case_id": "550e8400-e29b-41d4-a716-446655440000"}'

# Generate report
curl -X POST http://localhost:8000/report \
  -H "Content-Type: application/json" \
  -d '{}'

# Check health
curl http://localhost:8000/health
```

---

## 👥 Team Collaboration

### For New Team Members

1. **Start here:** Read [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
2. **Backend devs:** See [backend/README-backend.md](backend/README-backend.md)
3. **Frontend devs:** See [frontend/README-frontend.md](frontend/README-frontend.md)
4. **Everyone:** Review [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines

---

## 📊 Sample Data

The app comes with 10 pre-loaded sample cases covering different risk levels:

| Customer       | Amount  | Country     | Risk Score    | Status    |
| -------------- | ------- | ----------- | ------------- | --------- |
| Alice Johnson  | $5,300  | Singapore   | 0.82 (High)   | New       |
| John Smith     | $9,800  | USA         | 0.94 (High)   | New       |
| Lisa Anderson  | $22,000 | Switzerland | 0.88 (High)   | New       |
| Robert Chen    | $12,000 | USA         | 0.54 (Medium) | Reviewing |
| Sarah Williams | $7,500  | UK          | 0.65 (Medium) | Reviewing |
| ...            | ...     | ...         | ...           | ...       |

---

## 🎯 IBM SkillsBuild Requirements

This project fulfills IBM SkillsBuild evaluation criteria:

### ✅ Completeness (5 pts)

- All API endpoints functional
- watsonx.ai integration ready
- Complete proof-of-concept

### ✅ Creativity (5 pts)

- Agentic reasoning for risk assessment
- Multi-step analysis pipeline
- Explainable AI with confidence scores

### ✅ Design/UX (5 pts)

- Professional UI with shadcn/ui
- Intuitive navigation
- Clear risk visualizations

### ✅ Effectiveness (5 pts)

- Solves real banking problem
- Scalable architecture
- Token budget management

**See [docs/IBM_COMPLIANCE.md](docs/IBM_COMPLIANCE.md) for full requirements.**

---


### watsonx.ai issues

See [docs/WATSONX_INTEGRATION.md](docs/WATSONX_INTEGRATION.md) for:

- How to get API keys
- Token budget management
- Common error solutions

---

## 📞 Support & Resources

### IBM SkillsBuild Resources

- Weekly coaching sessions
- IBM mentor office hours
- Technical support via Slack

### Documentation

- [Complete Setup Guide](docs/GETTING_STARTED.md)
- [watsonx.ai Integration](docs/WATSONX_INTEGRATION.md)
- [IBM Compliance Requirements](docs/IBM_COMPLIANCE.md)

### External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [IBM watsonx.ai Documentation](https://www.ibm.com/products/watsonx-ai)
- [IBM Granite Models](https://www.ibm.com/granite)

---

## 📝 License

This project is created for the IBM SkillsBuild AI Experiential Learning Lab 2025.

---

## 🙏 Acknowledgments

- **IBM SkillsBuild** - AI Experiential Learning Lab 2025
- **IBM watsonx.ai** - Granite foundation models

