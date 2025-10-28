# Risk Assessment AI

## 🛠️ Tech Stack

### Backend

- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Database (via psycopg2-binary)
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server implementation

### Frontend

- **Next.js 16** - React framework for production
- **React 19** - UI library
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS 4** - Utility-first CSS framework
- **ESLint** - Code quality and consistency

## 📁 Project Structure

```
risk-assessment-ai/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── requirements.txt     # Python dependencies
│   └── venv/               # Python virtual environment
├── frontend/
│   ├── app/                # Next.js app directory
│   │   ├── page.tsx        # Home page
│   │   ├── layout.tsx      # Root layout
│   │   └── globals.css     # Global styles
│   ├── public/             # Static assets
│   ├── package.json        # Node dependencies
│   └── tsconfig.json       # TypeScript configuration
└── README.md
```

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - For the backend
- **Node.js 18+** - For the frontend
- **npm** or **yarn** - Package manager
- **PostgreSQL** (optional) - If using database features

## 🔧 Installation

### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
# or
yarn install
```

## 🚀 Running the Application

### Start the Backend

From the `backend` directory with the virtual environment activated:

```bash
uvicorn main:app --reload
```

The API will be available at:

- **API**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### Start the Frontend

From the `frontend` directory:

```bash
npm run dev
# or
yarn dev
```

The application will be available at:

- **Frontend**: http://localhost:3000
