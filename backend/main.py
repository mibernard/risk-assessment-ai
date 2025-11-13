"""
AI Risk Assessment & Compliance Assistant API
IBM SkillsBuild AI Experiential Learning Lab 2025

FastAPI backend with watsonx.ai integration.
"""

from datetime import datetime, timedelta
from typing import List
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from schemas import (
    CaseResponse,
    ExplanationRequest,
    ExplanationResponse,
    HealthResponse,
    ReportRequest,
    ReportResponse,
    TokenUsageResponse,
    ErrorResponse,
    StatusDistribution,
)
from services.watsonx_service import WatsonXService

# Initialize FastAPI app
app = FastAPI(
    title="Risk Assessment AI API",
    description="AI-powered banking transaction risk assessment using IBM watsonx.ai",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Load settings
settings = get_settings()

# Initialize watsonx.ai service
watsonx_service = WatsonXService()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================================
# In-Memory Data Store (Phase 1)
# ===================================

# Sample cases for MVP (will be replaced with database in Phase 3)
CASES_DB = {
    "550e8400-e29b-41d4-a716-446655440000": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "customer_name": "Alice Johnson",
        "amount": 5300.00,
        "country": "SG",
        "risk_score": 0.82,
        "status": "new",
        "created_at": datetime.now() - timedelta(hours=2),
        "explanation_generated": False,
    },
    "660e8400-e29b-41d4-a716-446655440001": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "customer_name": "Robert Chen",
        "amount": 12000.00,
        "country": "US",
        "risk_score": 0.54,
        "status": "reviewing",
        "created_at": datetime.now() - timedelta(hours=5),
        "explanation_generated": True,
        "model_version": "granite-3-2-8b-instruct",
        "tokens_used": 287,
    },
    "770e8400-e29b-41d4-a716-446655440002": {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "customer_name": "Maria Gonzalez",
        "amount": 450.00,
        "country": "US",
        "risk_score": 0.18,
        "status": "resolved",
        "created_at": datetime.now() - timedelta(days=1),
        "explanation_generated": True,
        "model_version": "granite-3-2-8b-instruct",
        "tokens_used": 245,
    },
    "880e8400-e29b-41d4-a716-446655440003": {
        "id": "880e8400-e29b-41d4-a716-446655440003",
        "customer_name": "John Smith",
        "amount": 9800.00,
        "country": "US",
        "risk_score": 0.94,
        "status": "new",
        "created_at": datetime.now() - timedelta(hours=1),
        "explanation_generated": False,
    },
    "990e8400-e29b-41d4-a716-446655440004": {
        "id": "990e8400-e29b-41d4-a716-446655440004",
        "customer_name": "Sarah Williams",
        "amount": 7500.00,
        "country": "GB",
        "risk_score": 0.65,
        "status": "reviewing",
        "created_at": datetime.now() - timedelta(hours=8),
        "explanation_generated": True,
        "model_version": "granite-3-2-8b-instruct",
        "tokens_used": 312,
    },
    "aa0e8400-e29b-41d4-a716-446655440005": {
        "id": "aa0e8400-e29b-41d4-a716-446655440005",
        "customer_name": "David Lee",
        "amount": 3200.00,
        "country": "KR",
        "risk_score": 0.47,
        "status": "new",
        "created_at": datetime.now() - timedelta(hours=3),
        "explanation_generated": False,
    },
    "bb0e8400-e29b-41d4-a716-446655440006": {
        "id": "bb0e8400-e29b-41d4-a716-446655440006",
        "customer_name": "Emma Brown",
        "amount": 15000.00,
        "country": "AU",
        "risk_score": 0.71,
        "status": "reviewing",
        "created_at": datetime.now() - timedelta(hours=6),
        "explanation_generated": True,
        "model_version": "granite-3-2-8b-instruct",
        "tokens_used": 356,
    },
    "cc0e8400-e29b-41d4-a716-446655440007": {
        "id": "cc0e8400-e29b-41d4-a716-446655440007",
        "customer_name": "Michael Taylor",
        "amount": 890.00,
        "country": "US",
        "risk_score": 0.23,
        "status": "resolved",
        "created_at": datetime.now() - timedelta(days=2),
        "explanation_generated": True,
        "model_version": "granite-3-2-8b-instruct",
        "tokens_used": 198,
    },
    "dd0e8400-e29b-41d4-a716-446655440008": {
        "id": "dd0e8400-e29b-41d4-a716-446655440008",
        "customer_name": "Lisa Anderson",
        "amount": 22000.00,
        "country": "CH",
        "risk_score": 0.88,
        "status": "new",
        "created_at": datetime.now() - timedelta(minutes=45),
        "explanation_generated": False,
    },
    "ee0e8400-e29b-41d4-a716-446655440009": {
        "id": "ee0e8400-e29b-41d4-a716-446655440009",
        "customer_name": "James Wilson",
        "amount": 1250.00,
        "country": "CA",
        "risk_score": 0.31,
        "status": "resolved",
        "created_at": datetime.now() - timedelta(days=3),
        "explanation_generated": True,
        "model_version": "granite-3-2-8b-instruct",
        "tokens_used": 223,
    },
}

# ===================================
# API Routes
# ===================================

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to docs."""
    return {
        "message": "Risk Assessment AI API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint",
)
async def health_check():
    """
    Check API health status including database and watsonx.ai connectivity.
    """
    # Check watsonx.ai availability
    watsonx_status = "available" if watsonx_service.is_available() else "unavailable"
    
    # Get token budget remaining
    token_usage = watsonx_service.get_token_usage()
    
    return HealthResponse(
        status="healthy",
        database="connected",  # Will check real DB in Phase 3
        watsonx_api=watsonx_status,
        token_budget_remaining=token_usage["remaining_usd"],
    )


@app.get(
    "/cases",
    response_model=List[CaseResponse],
    tags=["Cases"],
    summary="List all cases",
    description="Retrieve all flagged banking transactions.",
)
async def get_cases():
    """
    Get all cases from the database.
    
    Returns:
        List of all cases with their details.
    """
    cases = list(CASES_DB.values())
    return cases


@app.get(
    "/cases/{case_id}",
    response_model=CaseResponse,
    tags=["Cases"],
    summary="Get case by ID",
    description="Retrieve detailed information for a specific case.",
    responses={
        404: {"model": ErrorResponse, "description": "Case not found"},
        422: {"model": ErrorResponse, "description": "Invalid UUID format"},
    },
)
async def get_case(case_id: str):
    """
    Get a specific case by ID.
    
    Args:
        case_id: UUID of the case to retrieve.
        
    Returns:
        Case details.
        
    Raises:
        HTTPException: 404 if case not found.
    """
    # Validate UUID format
    try:
        uuid4().hex  # Just to check uuid4 is importable
        # Simple validation - check if it's in our DB
        if case_id not in CASES_DB:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case with ID {case_id} not found",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid UUID format",
        )
    
    return CASES_DB[case_id]


@app.post(
    "/explain",
    response_model=ExplanationResponse,
    tags=["AI"],
    summary="Generate AI explanation",
    description="Request watsonx.ai to generate a risk assessment explanation.",
    responses={
        404: {"model": ErrorResponse, "description": "Case not found"},
        503: {"model": ErrorResponse, "description": "AI service unavailable"},
        429: {"model": ErrorResponse, "description": "Token budget exceeded"},
    },
)
async def explain_case(request: ExplanationRequest):
    """
    Generate AI explanation for a case using watsonx.ai.
    
    **Phase 2**: Integrated with IBM watsonx.ai Granite-13b-instruct-v2.
    Falls back to mock responses if watsonx.ai is unavailable.
    
    Args:
        request: Explanation request with case_id.
        
    Returns:
        AI-generated explanation with rationale and recommended action.
        
    Raises:
        HTTPException: 404 if case not found, 503 if AI unavailable, 429 if budget exceeded.
    """
    # Check if case exists
    if request.case_id not in CASES_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {request.case_id} not found",
        )
    
    case = CASES_DB[request.case_id]
    
    # Try to use real watsonx.ai (Phase 2)
    if watsonx_service.is_available():
        try:
            # Generate explanation using watsonx.ai
            result = watsonx_service.generate_explanation(
                customer_name=case["customer_name"],
                amount=case["amount"],
                country=case["country"],
                risk_score=case["risk_score"],
            )
            
            # Create response
            explanation = ExplanationResponse(
                case_id=request.case_id,
                confidence=result["confidence"],
                rationale=result["rationale"],
                recommended_action=result["recommended_action"],
                model_used=watsonx_service.MODEL_ID,
                tokens_consumed=result["tokens_consumed"],
                generation_time_ms=result["generation_time_ms"],
                created_at=datetime.now(),
            )
            
            # Update case metadata
            CASES_DB[request.case_id]["explanation_generated"] = True
            CASES_DB[request.case_id]["model_version"] = watsonx_service.MODEL_ID
            CASES_DB[request.case_id]["tokens_used"] = result["tokens_consumed"]
            
            # Check for budget warnings
            has_warning, warning_msg = watsonx_service.check_budget_status()
            if has_warning:
                print(warning_msg)
            
            return explanation
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle specific errors
            if "budget exceeded" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Token budget exceeded. Cannot generate more explanations.",
                )
            
            # For other errors, log and fall back to mock
            print(f"⚠️ watsonx.ai error (falling back to mock): {error_msg}")
    
    # Fallback: Mock response (Phase 1 behavior)
    if case["risk_score"] >= 0.8:
        rationale = (
            f"Transaction of ${case['amount']:,.2f} from {case['country']} "
            f"exhibits multiple high-risk indicators: unusual pattern, "
            f"amount significantly exceeds typical customer behavior, "
            f"and originates from jurisdiction requiring enhanced due diligence."
        )
        action = (
            "HOLD transaction for enhanced due diligence. Required: "
            "(1) Contact customer via verified phone, "
            "(2) Request supporting documentation, "
            "(3) Verify source of funds, "
            "(4) File SAR if unable to verify within 24 hours."
        )
        confidence = 0.91
    elif case["risk_score"] >= 0.5:
        rationale = (
            f"Transaction amount (${case['amount']:,.2f}) from {case['country']} "
            f"exceeds typical range but remains within reasonable bounds. "
            f"Moderate risk factors present requiring review."
        )
        action = (
            "APPROVE with enhanced monitoring. Recommended: "
            "(1) Flag account for 30-day surveillance, "
            "(2) Escalate if similar transactions repeat within 7 days, "
            "(3) Document approval rationale."
        )
        confidence = 0.76
    else:
        rationale = (
            f"Transaction of ${case['amount']:,.2f} from {case['country']} "
            f"aligns with established customer behavior pattern. "
            f"No unusual indicators present."
        )
        action = (
            "APPROVE immediately. No further action required. "
            "Continue standard automated monitoring."
        )
        confidence = 0.89
    
    # Mock response
    explanation = ExplanationResponse(
        case_id=request.case_id,
        confidence=confidence,
        rationale=rationale,
        recommended_action=action,
        model_used="mock-granite-13b-instruct-v2",
        tokens_consumed=0,
        generation_time_ms=50,
        created_at=datetime.now(),
    )
    
    # Update case metadata
    CASES_DB[request.case_id]["explanation_generated"] = True
    CASES_DB[request.case_id]["model_version"] = "mock-granite-13b-instruct-v2"
    
    return explanation


@app.post(
    "/report",
    response_model=ReportResponse,
    tags=["Reports"],
    summary="Generate compliance report",
    description="Generate aggregated statistics and optional AI summary.",
)
async def generate_report(request: ReportRequest = ReportRequest()):
    """
    Generate compliance report with aggregated statistics.
    
    Args:
        request: Optional report configuration (case_ids, include_ai_summary).
        
    Returns:
        Compliance report with statistics and status distribution.
    """
    # Filter cases
    if request.case_ids:
        cases = [CASES_DB[cid] for cid in request.case_ids if cid in CASES_DB]
    else:
        # Default: all cases with status != "resolved"
        cases = [c for c in CASES_DB.values() if c["status"] != "resolved"]
    
    if not cases:
        cases = list(CASES_DB.values())  # Fallback to all cases
    
    # Calculate statistics
    total_cases = len(cases)
    high_risk = sum(1 for c in cases if c["risk_score"] >= 0.7)
    medium_risk = sum(1 for c in cases if 0.4 <= c["risk_score"] < 0.7)
    low_risk = sum(1 for c in cases if c["risk_score"] < 0.4)
    avg_risk = sum(c["risk_score"] for c in cases) / total_cases if total_cases > 0 else 0.0
    total_amount = sum(c["amount"] for c in cases)
    
    # Status distribution
    status_dist = StatusDistribution(
        new=sum(1 for c in cases if c["status"] == "new"),
        reviewing=sum(1 for c in cases if c["status"] == "reviewing"),
        resolved=sum(1 for c in cases if c["status"] == "resolved"),
    )
    
    # Period (based on case timestamps)
    if cases:
        timestamps = [c["created_at"] for c in cases]
        period_start = min(timestamps)
        period_end = max(timestamps)
    else:
        period_start = datetime.now() - timedelta(days=7)
        period_end = datetime.now()
    
    # Generate summary
    if request.include_ai_summary and watsonx_service.is_available():
        try:
            # Phase 2: Use watsonx.ai for summary
            result = watsonx_service.generate_report_summary(
                total_cases=total_cases,
                high_risk_count=high_risk,
                medium_risk_count=medium_risk,
                low_risk_count=low_risk,
                avg_risk=avg_risk,
                total_amount=total_amount,
            )
            summary = result["summary"]
            
            # Check for budget warnings
            has_warning, warning_msg = watsonx_service.check_budget_status()
            if has_warning:
                print(warning_msg)
                
        except Exception as e:
            # Fallback to simple summary if AI fails
            print(f"⚠️ watsonx.ai report summary failed: {e}")
            summary = (
                f"{high_risk} high-risk transactions detected. "
                f"Primary concerns: international transfers and large amounts. "
                f"Recommend enhanced monitoring of cross-border transactions >${total_amount/total_cases:,.0f}."
            )
    elif request.include_ai_summary:
        # Fallback: Mock summary when watsonx.ai unavailable
        summary = (
            f"{high_risk} high-risk transactions detected. "
            f"Primary concerns: international transfers and large amounts. "
            f"Recommend enhanced monitoring of cross-border transactions >${total_amount/total_cases:,.0f}."
        )
    else:
        summary = (
            f"Compliance report for {total_cases} transactions. "
            f"Risk distribution: {high_risk} high, {medium_risk} medium, {low_risk} low."
        )
    
    return ReportResponse(
        summary=summary,
        high_risk_count=high_risk,
        medium_risk_count=medium_risk,
        low_risk_count=low_risk,
        avg_risk=round(avg_risk, 2),
        total_cases=total_cases,
        total_amount=round(total_amount, 2),
        status_distribution=status_dist,
        period_start=period_start,
        period_end=period_end,
    )


@app.get(
    "/admin/tokens",
    response_model=TokenUsageResponse,
    tags=["Admin"],
    summary="Get token usage statistics",
    description="Track watsonx.ai token consumption against budget.",
)
async def get_token_usage():
    """
    Get current token usage and budget status.
    
    Returns:
        Token usage statistics including spent and remaining budget.
    """
    # Get real token usage from watsonx service
    usage = watsonx_service.get_token_usage()
    
    return TokenUsageResponse(
        total_budget_usd=usage["total_budget_usd"],
        spent_usd=usage["spent_usd"],
        remaining_usd=usage["remaining_usd"],
        tokens_used=usage["tokens_used"],
        requests_count=usage["requests_count"],
        percentage_used=usage["percentage_used"],
    )
