"""
Quick test script to verify .env configuration
"""

from config import get_settings

settings = get_settings()

print("=" * 50)
print("Environment Configuration Check")
print("=" * 50)
print(f"✓ DATABASE_URL: {settings.database_url}")
print(f"✓ WATSONX_URL: {settings.watsonx_url}")
print(f"✓ FRONTEND_URL: {settings.frontend_url}")
print()

if settings.watsonx_api_key:
    print(f"✓ WATSONX_API_KEY: Set (length: {len(settings.watsonx_api_key)} characters)")
else:
    print("✗ WATSONX_API_KEY: NOT SET (optional for Phase 1)")

if settings.watsonx_project_id:
    print(f"✓ WATSONX_PROJECT_ID: Set ({settings.watsonx_project_id[:8]}...)")
else:
    print("✗ WATSONX_PROJECT_ID: NOT SET (optional for Phase 1)")

print("=" * 50)
print("\nConfiguration looks good! Ready to start server.")
print("\nTo start the backend, run:")
print("  cd backend")
print("  source venv/bin/activate")
print("  uvicorn main:app --reload --port 8000")

