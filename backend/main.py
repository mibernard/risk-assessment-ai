"""
AI Risk Assessment & Compliance Assistant API
IBM SkillsBuild AI Experiential Learning Lab 2025

FastAPI backend with watsonx.ai integration.
"""

from datetime import datetime, timedelta
from typing import List
from uuid import uuid4
from pathlib import Path

from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from schemas import (
    CaseResponse,
    ExplanationRequest,
    ExplanationResponse,
    RiskCategoryRequest,
    RiskCategoryResponse,
    RiskScoreRequest,
    RiskScoreResponse,
    HealthResponse,
    ReportRequest,
    ReportResponse,
    TokenUsageResponse,
    ErrorResponse,
    StatusDistribution,
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentMetadata,
    ComplianceAnalysisRequest,
    ComplianceAnalysisResponse,
)
from services.watsonx_service import WatsonXService
from services.document_service import document_service

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

# Startup event: Load sample compliance documents
@app.on_event("startup")
async def startup_event():
    """Load sample compliance documents on startup."""
    compliance_docs_dir = Path(__file__).parent / "compliance_documents"
    
    if compliance_docs_dir.exists():
        print("📄 Loading sample compliance documents...")
        for doc_file in compliance_docs_dir.glob("*.md"):
            try:
                document_service.process_document(
                    file_path=str(doc_file),
                    filename=doc_file.name,
                    file_type="MD",
                    size_bytes=doc_file.stat().st_size,
                )
                print(f"  ✓ Loaded: {doc_file.name}")
            except Exception as e:
                print(f"  ✗ Failed to load {doc_file.name}: {e}")
        
        print(f"✓ {len(document_service.list_documents())} compliance documents loaded")
    else:
        print("⚠️  No compliance documents directory found")

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
        "explanation_generated": False,
    },
    "770e8400-e29b-41d4-a716-446655440002": {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "customer_name": "Maria Gonzalez",
        "amount": 450.00,
        "country": "US",
        "risk_score": 0.18,
        "status": "resolved",
        "created_at": datetime.now() - timedelta(days=1),
        "explanation_generated": False,
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
        "explanation_generated": False,
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
        "explanation_generated": False,
    },
    "cc0e8400-e29b-41d4-a716-446655440007": {
        "id": "cc0e8400-e29b-41d4-a716-446655440007",
        "customer_name": "Michael Taylor",
        "amount": 890.00,
        "country": "US",
        "risk_score": 0.23,
        "status": "resolved",
        "created_at": datetime.now() - timedelta(days=2),
        "explanation_generated": False,
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
        "explanation_generated": False,
    },
}

# Store explanations separately (keyed by case_id)
EXPLANATIONS_DB = {}

# Store risk scores separately (keyed by case_id)
RISK_SCORES_DB = {}

# Store risk categories separately (keyed by case_id)
RISK_CATEGORIES_DB = {}

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
            
            # Store explanation for future retrieval
            EXPLANATIONS_DB[request.case_id] = explanation
            
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
    
    # Store explanation for future retrieval
    EXPLANATIONS_DB[request.case_id] = explanation
    
    return explanation


@app.get(
    "/cases/{case_id}/explanation",
    response_model=ExplanationResponse,
    tags=["AI"],
    summary="Get stored explanation",
    description="Retrieve previously generated AI explanation for a case.",
    responses={
        404: {"model": ErrorResponse, "description": "Explanation not found"},
    },
)
async def get_explanation(case_id: str):
    """
    Get the stored AI explanation for a case.
    
    Args:
        case_id: UUID of the case.
        
    Returns:
        Previously generated explanation.
        
    Raises:
        HTTPException: 404 if explanation not found.
    """
    if case_id not in EXPLANATIONS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No explanation found for case {case_id}",
        )
    
    return EXPLANATIONS_DB[case_id]


@app.get(
    "/cases/{case_id}/risk-score",
    response_model=RiskScoreResponse,
    tags=["AI"],
    summary="Get stored risk score",
    description="Retrieve previously calculated AI risk score for a case.",
    responses={
        404: {"model": ErrorResponse, "description": "Risk score not found"},
    },
)
async def get_risk_score(case_id: str):
    """
    Get the stored AI risk score for a case.
    
    Args:
        case_id: UUID of the case.
        
    Returns:
        Previously calculated risk score.
        
    Raises:
        HTTPException: 404 if risk score not found.
    """
    if case_id not in RISK_SCORES_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No risk score found for case {case_id}",
        )
    
    return RISK_SCORES_DB[case_id]

@app.get(
        "/risk-categorize/{case_id}",
        response_model=RiskCategoryResponse,
        tags=["AI"],
        summary="Categorize risk level",
        description="Categorize a case into risk categories like fraud, AML, sanctions.",
        responses={
            404: {"model": ErrorResponse, "description": "Case not found"},
        },
)
async def calculate_risk_category(case_id: str):
    """
    Categorize risk level for a transaction based on predefined criteria.
    
    Args:
        request: Risk score request with case_id.
    """

    # Check if case exists
    if case_id not in CASES_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found",
        )
    
    case = CASES_DB[case_id]
    if watsonx_service.is_available():
        try:
            # Generate risk category using watsonx.ai
            result = watsonx_service.generate_risk_category(
                customer_name=case["customer_name"],
                amount=case["amount"],
                country=case["country"],
                transaction_type="wire transfer",
            )
            
            response = RiskCategoryResponse(
                case_id=case_id,
                risk_category=result["risk_category"],
                reasoning=result["reasoning"],
                model_used=watsonx_service.MODEL_ID,
                tokens_consumed=result["tokens_consumed"],
                generation_time_ms=result["generation_time_ms"],
                created_at=datetime.now(),
            )
            
            # Store risk category for future retrieval
            RISK_CATEGORIES_DB[case_id] = response
            
            # Check if budget is getting low
            # token_status = watsonx_service.get_token_usage()
            #if token_status["percentage_used"] >= 90:
            #   print(f"⚠️  WARNING: {token_status['percentage_used']:.1f}% of token budget used!")
            
            return response
            
        except Exception as e:
            error_msg = str(e)
            if "budget exceeded" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Token budget exceeded. Cannot generate more AI responses.",
                )
            else:
                print(f"⚠️  watsonx.ai error: {error_msg}")
                print("   Falling back to mock risk categorization")
    
    return RiskCategoryResponse(
            case_id=case_id,
            risk_category="general-risk",
            reasoning="Mock risk categorization due to watsonx.ai unavailability.",
            model_used="mock-rule-based",
            tokens_consumed=0,
            generation_time_ms=10,
            created_at=datetime.now(),)

@app.post(
    "/calculate-risk",
    response_model=RiskScoreResponse,
    tags=["AI"],
    summary="Calculate AI risk score",
    description="Use watsonx.ai to calculate a dynamic risk score for a transaction.",
    responses={
        404: {"model": ErrorResponse, "description": "Case not found"},
        503: {"model": ErrorResponse, "description": "AI service unavailable"},
        429: {"model": ErrorResponse, "description": "Token budget exceeded"},
    },
)
async def calculate_risk_score(request: RiskScoreRequest):
    """
    Calculate AI-powered risk score for a transaction using watsonx.ai.
    
    Uses IBM Granite model to analyze transaction data and generate a risk score
    between 0.0 (no risk) and 1.0 (very high risk) based on:
    - Transaction amount
    - Country risk profile
    - Transaction patterns
    - AML/fraud indicators
    
    Args:
        request: Risk score request with case_id.
        
    Returns:
        AI-generated risk score with reasoning and risk level.
        
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
    
    # Try to use real watsonx.ai
    if watsonx_service.is_available():
        try:
            # Generate risk score using watsonx.ai
            result = watsonx_service.generate_risk_score(
                customer_name=case["customer_name"],
                amount=case["amount"],
                country=case["country"],
            )
            
            response = RiskScoreResponse(
                case_id=request.case_id,
                risk_score=result["risk_score"],
                risk_level=result["risk_level"],
                reasoning=result["reasoning"],
                model_used=watsonx_service.MODEL_ID,
                tokens_consumed=result["tokens_consumed"],
                generation_time_ms=result["generation_time_ms"],
                created_at=datetime.now(),
            )
            
            # Update case with new AI-calculated risk score
            CASES_DB[request.case_id]["risk_score"] = result["risk_score"]
            CASES_DB[request.case_id]["model_version"] = watsonx_service.MODEL_ID
            
            # Store risk score for future retrieval
            RISK_SCORES_DB[request.case_id] = response
            
            # Check if budget is getting low
            token_status = watsonx_service.get_token_usage()
            if token_status["percentage_used"] >= 90:
                print(f"⚠️  WARNING: {token_status['percentage_used']:.1f}% of token budget used!")
            
            return response
            
        except Exception as e:
            error_msg = str(e)
            if "budget exceeded" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Token budget exceeded. Cannot generate more AI responses.",
                )
            else:
                print(f"⚠️  watsonx.ai error: {error_msg}")
                print("   Falling back to mock risk scoring")
    
    # Fallback: Simple rule-based risk scoring
    # Calculate based on amount and country
    amount_risk = min(1.0, case["amount"] / 20000)  # $20k+ = high risk
    
    # Simple country risk mapping
    high_risk_countries = {"SG", "CN", "RU", "IR"}
    country_risk = 0.7 if case["country"] in high_risk_countries else 0.3
    
    # Weighted average
    calculated_score = (amount_risk * 0.6) + (country_risk * 0.4)
    calculated_score = round(calculated_score, 2)
    
    # Determine risk level
    if calculated_score >= 0.7:
        risk_level = "HIGH"
        reasoning = f"High risk due to large transaction amount (${case['amount']:,.2f}) and high-risk jurisdiction ({case['country']})."
    elif calculated_score >= 0.4:
        risk_level = "MEDIUM"
        reasoning = f"Moderate risk. Transaction amount (${case['amount']:,.2f}) from {case['country']} requires standard review."
    else:
        risk_level = "LOW"
        reasoning = f"Low risk. Transaction amount (${case['amount']:,.2f}) from {case['country']} is within normal parameters."
    
    # Mock response
    response = RiskScoreResponse(
        case_id=request.case_id,
        risk_score=calculated_score,
        risk_level=risk_level,
        reasoning=reasoning,
        model_used="mock-rule-based",
        tokens_consumed=0,
        generation_time_ms=10,
        created_at=datetime.now(),
    )
    
    # Update case with calculated risk score
    CASES_DB[request.case_id]["risk_score"] = calculated_score
    
    # Store risk score for future retrieval
    RISK_SCORES_DB[request.case_id] = response
    
    return response


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


# ============================================
# Document Management & Docling Integration
# ============================================

@app.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    tags=["Documents"],
    summary="Upload compliance document",
    description="Upload a compliance document (PDF/DOCX) for extraction using IBM Docling.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file type"},
        500: {"model": ErrorResponse, "description": "Processing failed"},
    },
)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a compliance document and extract text using IBM Docling.
    
    Supports PDF, DOCX, and MD files. Docling extracts structured text
    which is chunked and indexed for RAG (Retrieval Augmented Generation).
    
    Args:
        file: Uploaded document file
        
    Returns:
        Document metadata and processing status
        
    Raises:
        HTTPException: 400 if file type not supported, 500 if processing fails
    """
    # Validate file type
    allowed_extensions = {".pdf", ".docx", ".md", ".txt"}
    file_ext = Path(file.filename).suffix.lower() if file.filename else ""
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}",
        )
    
    # Save file temporarily
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / f"{uuid4()}{file_ext}"
    
    try:
        # Save uploaded file
        content = await file.read()
        file_path.write_bytes(content)
        
        # Process with Docling
        result = document_service.process_document(
            file_path=str(file_path),
            filename=file.filename or "unknown",
            file_type=file_ext[1:].upper(),  # Remove leading dot
            size_bytes=len(content),
        )
        
        return DocumentUploadResponse(
            document_id=result["document_id"],
            filename=file.filename or "unknown",
            status=result["status"],
            chunks_extracted=result["chunks_extracted"],
            message=f"Document processed successfully. {result['chunks_extracted']} text chunks extracted.",
        )
        
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}",
        )


@app.get(
    "/documents",
    response_model=DocumentListResponse,
    tags=["Documents"],
    summary="List uploaded documents",
    description="Get list of all uploaded compliance documents.",
)
async def list_documents():
    """
    List all uploaded compliance documents with metadata.
    
    Returns:
        List of document metadata including processing status
    """
    documents = document_service.list_documents()
    
    doc_metadata = [
        DocumentMetadata(
            id=doc["id"],
            filename=doc["filename"],
            file_type=doc["file_type"],
            size_bytes=doc["size_bytes"],
            uploaded_at=doc["uploaded_at"],
            processed=doc.get("processed", False),
            chunk_count=doc.get("chunk_count", 0),
        )
        for doc in documents
    ]
    
    return DocumentListResponse(
        documents=doc_metadata,
        total_count=len(doc_metadata),
    )


@app.delete(
    "/documents/{document_id}",
    tags=["Documents"],
    summary="Delete document",
    description="Delete an uploaded compliance document.",
    responses={
        404: {"model": ErrorResponse, "description": "Document not found"},
    },
)
async def delete_document(document_id: str):
    """
    Delete a compliance document and its extracted chunks.
    
    Args:
        document_id: UUID of the document to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if document not found
    """
    success = document_service.delete_document(document_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )
    
    return {"message": "Document deleted successfully"}


@app.post(
    "/analyze-compliance",
    response_model=ComplianceAnalysisResponse,
    tags=["AI"],
    summary="Analyze compliance with RAG",
    description="Analyze transaction compliance using watsonx.ai with Docling-extracted document context.",
    responses={
        404: {"model": ErrorResponse, "description": "Case not found"},
        503: {"model": ErrorResponse, "description": "AI service unavailable"},
        429: {"model": ErrorResponse, "description": "Token budget exceeded"},
    },
)
async def analyze_compliance(request: ComplianceAnalysisRequest):
    """
    Analyze transaction compliance using RAG (Retrieval Augmented Generation).
    
    Uses IBM Docling-extracted compliance documents to provide context-aware
    analysis. Identifies potential violations, relevant regulations, and
    provides recommendations based on actual compliance policies.
    
    This demonstrates:
    - **IBM Docling** document processing
    - **RAG** (Retrieval Augmented Generation) with watsonx.ai
    - **Explainable AI** with document citations
    
    Args:
        request: Compliance analysis request with case_id
        
    Returns:
        Detailed compliance analysis with violations, regulations, and recommendations
        
    Raises:
        HTTPException: 404 if case not found, 503 if AI unavailable, 429 if budget exceeded
    """
    # Check if case exists
    if request.case_id not in CASES_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {request.case_id} not found",
        )
    
    case = CASES_DB[request.case_id]
    
    # Get relevant document context (RAG)
    document_context = ""
    documents_used = []
    
    if request.use_documents:
        # Retrieve relevant chunks based on transaction data
        query = f"transaction {case['amount']} {case['country']} risk assessment compliance"
        relevant_chunks = document_service.retrieve_relevant_chunks(query, top_k=5)
        
        if relevant_chunks:
            document_context = "\n\n".join([chunk.text for chunk in relevant_chunks])
            # Get unique document filenames
            doc_ids = list(set([chunk.document_id for chunk in relevant_chunks]))
            for doc_id in doc_ids:
                doc = document_service.get_document_metadata(doc_id)
                if doc:
                    documents_used.append(doc["filename"])
        else:
            # Fallback: use all documents if no specific chunks retrieved
            document_context = document_service.get_all_chunks_text()
            all_docs = document_service.list_documents()
            documents_used = [doc["filename"] for doc in all_docs]
    
    # Try to use real watsonx.ai with RAG
    if watsonx_service.is_available() and document_context:
        try:
            # Generate compliance analysis using watsonx.ai + RAG
            result = watsonx_service.analyze_compliance_with_rag(
                customer_name=case["customer_name"],
                amount=case["amount"],
                country=case["country"],
                risk_score=case["risk_score"],
                document_context=document_context,
            )
            
            response = ComplianceAnalysisResponse(
                case_id=request.case_id,
                compliance_status=result["compliance_status"],
                violations=result["violations"],
                relevant_regulations=result["relevant_regulations"],
                recommendation=result["recommendation"],
                confidence=result["confidence"],
                documents_used=documents_used,
                model_used=watsonx_service.MODEL_ID,
                tokens_consumed=result["tokens_consumed"],
                generation_time_ms=result["generation_time_ms"],
                created_at=datetime.now(),
            )
            
            # Check if budget is getting low
            token_status = watsonx_service.get_token_usage()
            if token_status["percentage_used"] >= 90:
                print(f"⚠️  WARNING: {token_status['percentage_used']:.1f}% of token budget used!")
            
            return response
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n{'='*60}")
            print(f"⚠️  WATSONX.AI COMPLIANCE ANALYSIS ERROR")
            print(f"{'='*60}")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {error_msg}")
            print(f"Document Context Length: {len(document_context)} chars")
            print(f"Documents Found: {len(documents_used)}")
            print(f"{'='*60}\n")
            
            if "budget exceeded" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Token budget exceeded. Cannot generate more AI responses.",
                )
            else:
                print("   Falling back to rule-based compliance analysis")
    
    # Fallback: Rule-based compliance analysis
    violations = []
    relevant_regulations = []
    
    # Check amount threshold
    if case["amount"] >= 10000:
        violations.append("Transaction exceeds $10,000 threshold requiring Enhanced Due Diligence")
        relevant_regulations.append("AML Policy Section 2.1 - Enhanced Due Diligence Requirements")
    
    # Check high-risk country
    high_risk_countries = {"IR", "KP", "SY", "RU", "CN"}
    if case["country"] in high_risk_countries:
        violations.append(f"Transaction involves high-risk jurisdiction: {case['country']}")
        relevant_regulations.append("Sanctions Compliance Policy Section 4.1 - High-Risk Countries")
    
    # Determine status
    if not violations:
        compliance_status = "COMPLIANT"
        recommendation = "Transaction approved. No compliance concerns identified. Proceed with standard processing."
    elif len(violations) == 1:
        compliance_status = "REVIEW_REQUIRED"
        recommendation = "Conduct enhanced due diligence. Verify source of funds and customer background before processing."
    else:
        compliance_status = "NON_COMPLIANT"
        recommendation = "BLOCK transaction. Multiple compliance violations detected. Escalate to senior compliance officer for review."
    
    if not relevant_regulations:
        relevant_regulations.append("Standard Banking Compliance Procedures")
    
    response = ComplianceAnalysisResponse(
        case_id=request.case_id,
        compliance_status=compliance_status,
        violations=violations,
        relevant_regulations=relevant_regulations,
        recommendation=recommendation,
        confidence=0.75,
        documents_used=documents_used or ["Built-in Compliance Rules"],
        model_used="rule-based-fallback",
        tokens_consumed=0,
        generation_time_ms=10,
        created_at=datetime.now(),
    )
    
    return response
