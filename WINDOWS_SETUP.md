# Windows Setup Guide

Quick guide for Windows users setting up the backend.

## ⚠️ Important: Python Version

**Windows users MUST use Python 3.10, 3.11, or 3.12**

Python 3.13+ will fail with compile errors because required packages (pandas, numpy) don't have pre-built Windows binaries yet.

## Step-by-Step Setup

### 1. Check Your Python Version

```powershell
python --version
python3.10 --version
python3.11 --version
python3.12 --version
```

### 2. Install Python 3.10-3.12 (If Needed)

If you only have Python 3.13+, download and install Python 3.11:

**Download:** https://www.python.org/downloads/

- Choose Python 3.11.x or 3.12.x
- During installation, check "Add Python to PATH"
- After installation, verify: `python3.11 --version`

### 3. Create Virtual Environment

```powershell
cd backend

# Use one of these (whichever version you have)
python3.11 -m venv venv
# OR
python3.10 -m venv venv
# OR
python3.12 -m venv venv
```

### 4. Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

**If you get an error about execution policy:**

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

### 5. Install Requirements

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**If this fails with database errors, use minimal:**

```powershell
pip install -r requirements-minimal.txt
```

### 6. Create .env File

Create a file named `.env` in the `backend` folder:

```env
DATABASE_URL=sqlite:///./dev.db
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
FRONTEND_URL=http://localhost:3000
```

### 7. Run Backend

```powershell
uvicorn main:app --reload --port 8000
```

Visit http://localhost:8000/docs to see the API documentation.

## Common Windows Errors

### Error: "Unknown compiler(s)"

**Cause:** Using Python 3.13+ on Windows  
**Fix:** Delete venv and recreate with Python 3.10-3.12

```powershell
Remove-Item -Recurse -Force venv
python3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Error: "Execution of scripts is disabled"

**Fix:**

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### Error: "command not found: python3.11"

**Fix:** Install Python 3.11 from python.org and make sure "Add to PATH" was checked during installation.

### Port 8000 Already in Use

```powershell
# Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

## Verify Setup

```powershell
# Check Python version in venv (should be 3.10-3.12)
python --version

# Test watsonx.ai SDK
python -c "from ibm_watson_machine_learning.foundation_models import Model; print('✅ watsonx.ai SDK ready!')"

# Test backend
uvicorn main:app --reload --port 8000
# In another terminal:
curl http://localhost:8000/health
```

## Quick Troubleshooting

| Issue                      | Solution                          |
| -------------------------- | --------------------------------- |
| Python 3.13 compile errors | Use Python 3.10-3.12              |
| Can't activate venv        | Run `Set-ExecutionPolicy` command |
| Missing Python             | Install from python.org           |
| Port 8000 in use           | Kill process with `taskkill`      |
| watsonx.ai import fails    | Check Python version is 3.10+     |

## Need Help?

See the main [Backend README](README-backend.md) for detailed documentation.
