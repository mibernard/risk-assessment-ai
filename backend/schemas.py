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

