"""
Pydantic schemas for API request/response validation.
Aligned with docs/API_CONTRACT.md
"""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class CaseBase(BaseModel):
    """Base schema for Case with common fields."""
    customer_name: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0, description="Transaction amount in USD")
    country: str = Field(..., min_length=2, max_length=100, description="ISO country code")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk score between 0 and 1")
    status: Literal["new", "reviewing", "resolved"]
    
    @field_validator("amount")
    @classmethod
    def validate_amount_decimals(cls, v: float) -> float:
        """Ensure amount has max 2 decimal places."""
        if round(v, 2) != v:
            raise ValueError("Amount must have at most 2 decimal places")
        return v


class CaseCreate(CaseBase):
    """Schema for creating a new case."""
    pass


class CaseResponse(CaseBase):
    """Schema for case response."""
    id: str
    created_at: datetime
    explanation_generated: Optional[bool] = False
    model_version: Optional[str] = None
    tokens_used: Optional[int] = None
    category: Optional[str] = None
    
    class Config:
        from_attributes = True


class ExplanationRequest(BaseModel):
    """Schema for requesting an AI explanation."""
    case_id: str = Field(..., description="UUID of the case to explain")
    
    @field_validator("case_id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate case_id is a valid UUID."""
        try:
            UUID(v)
        except ValueError:
            raise ValueError("case_id must be a valid UUID")
        return v


class ExplanationResponse(BaseModel):
    """Schema for AI explanation response."""
    case_id: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    rationale: str = Field(..., min_length=10, description="Explanation text")
    recommended_action: str = Field(..., min_length=10, description="Recommended action")
    model_used: str = Field(..., description="Model identifier")
    tokens_consumed: int = Field(..., ge=0, description="Tokens used")
    generation_time_ms: int = Field(..., ge=0, description="Generation latency in ms")
    created_at: datetime
    
    class Config:
        from_attributes = True

class RiskCategoryRequest(BaseModel):
    """Schema for requesting risk category."""
    case_id: str = Field(..., description="UUID of the case to categorize")
    
    @field_validator("case_id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        try:
            UUID(v)
        except ValueError:
            raise ValueError("case_id must be a valid UUID")
        return v

class RiskCategoryResponse(BaseModel):
    """Schema for AI risk category response."""
    case_id: str
    risk_category: str = Field(..., description="AI-determined risk category")
    reasoning: str = Field(..., description="Explanation of the risk category")
    model_used: str = Field(..., description="Model identifier")
    tokens_consumed: int = Field(..., ge=0, description="Tokens used")
    generation_time_ms: int = Field(..., ge=0, description="Generation latency in ms")
    created_at: datetime
    
    class Config:
        from_attributes = True


class RiskScoreRequest(BaseModel):
    """Schema for AI risk score calculation request."""
    case_id: str = Field(..., description="UUID of the case to score")
    
    @field_validator("case_id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        try:
            UUID(v)
        except ValueError:
            raise ValueError("case_id must be a valid UUID")
        return v


class RiskScoreResponse(BaseModel):
    """Schema for AI risk score calculation response."""
    case_id: str
    risk_score: float = Field(..., ge=0.0, le=1.0, description="AI-calculated risk score")
    risk_level: str = Field(..., description="LOW/MEDIUM/HIGH risk level")
    reasoning: str = Field(..., description="Explanation of the risk score")
    model_used: str = Field(..., description="Model identifier")
    tokens_consumed: int = Field(..., ge=0, description="Tokens used")
    generation_time_ms: int = Field(..., ge=0, description="Generation latency in ms")
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReportRequest(BaseModel):
    """Schema for report generation request."""
    case_ids: Optional[list[str]] = Field(
        None, 
        description="Optional list of case IDs to include. If None, includes all open cases."
    )
    include_ai_summary: bool = Field(
        False, 
        description="Whether to generate AI summary (costs tokens)"
    )


class StatusDistribution(BaseModel):
    """Status distribution breakdown."""
    new: int = Field(..., ge=0)
    reviewing: int = Field(..., ge=0)
    resolved: int = Field(..., ge=0)


class ReportResponse(BaseModel):
    """Schema for compliance report response."""
    summary: str
    high_risk_count: int = Field(..., ge=0, description="Cases with risk_score >= 0.7")
    medium_risk_count: int = Field(..., ge=0, description="Cases with 0.4 <= risk_score < 0.7")
    low_risk_count: int = Field(..., ge=0, description="Cases with risk_score < 0.4")
    avg_risk: float = Field(..., ge=0.0, le=1.0, description="Average risk score")
    total_cases: int = Field(..., ge=0)
    total_amount: float = Field(..., ge=0.0, description="Sum of all amounts")
    status_distribution: StatusDistribution
    period_start: datetime
    period_end: datetime


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: Literal["healthy", "unhealthy"]
    database: Literal["connected", "disconnected"]
    watsonx_api: Literal["available", "unavailable"]
    token_budget_remaining: float = Field(..., description="Remaining budget in USD")


class TokenUsageResponse(BaseModel):
    """Schema for token usage tracking response."""
    total_budget_usd: float
    spent_usd: float
    remaining_usd: float
    tokens_used: int
    requests_count: int
    percentage_used: float = Field(..., ge=0.0, le=100.0)


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    error_code: str
    timestamp: datetime


class DocumentMetadata(BaseModel):
    """Schema for document metadata."""
    id: str
    filename: str
    file_type: str = Field(..., description="PDF, DOCX, TXT, etc.")
    size_bytes: int = Field(..., ge=0)
    uploaded_at: datetime
    processed: bool = False
    chunk_count: int = Field(0, ge=0, description="Number of text chunks extracted")
    
    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response."""
    document_id: str
    filename: str
    status: str = Field(..., description="uploaded|processing|processed|failed")
    chunks_extracted: int = Field(..., ge=0)
    message: str


class ComplianceAnalysisRequest(BaseModel):
    """Schema for compliance analysis request."""
    case_id: str = Field(..., description="UUID of the case to analyze")
    use_documents: bool = Field(True, description="Use uploaded compliance docs for RAG")
    
    @field_validator("case_id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        try:
            UUID(v)
        except ValueError:
            raise ValueError("case_id must be a valid UUID")
        return v


class ComplianceAnalysisResponse(BaseModel):
    """Schema for compliance analysis response with RAG."""
    case_id: str
    compliance_status: str = Field(..., description="COMPLIANT|NON_COMPLIANT|REVIEW_REQUIRED")
    violations: list[str] = Field(default_factory=list, description="List of potential violations")
    relevant_regulations: list[str] = Field(default_factory=list, description="Applicable regulations")
    recommendation: str = Field(..., description="Compliance recommendation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence")
    documents_used: list[str] = Field(default_factory=list, description="Source documents")
    model_used: str
    tokens_consumed: int = Field(..., ge=0)
    generation_time_ms: int = Field(..., ge=0)
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for listing documents."""
    documents: list[DocumentMetadata]
    total_count: int = Field(..., ge=0)

