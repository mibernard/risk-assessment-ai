# watsonx.ai Integration Guide

## Overview

This guide covers the complete integration of IBM watsonx.ai into the Risk Assessment application, including SDK setup, API usage, token management, and best practices.

---

## Prerequisites

### 1. IBM Cloud Account
- Team account provisioned through IBM SkillsBuild
- Access to watsonx.ai service in Dallas region
- $250 USD credit allocation

### 2. Required Credentials
Obtain from watsonx.ai Developer Access section:

```env
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

⚠️ **Never commit credentials to Git**. Use `.env` file (gitignored).

### 3. Python Environment
- Python 3.9+
- Virtual environment activated
- Install SDK: `pip install ibm-watson-machine-learning ibm-cloud-sdk-core`

---

## Quick Start

### Step 1: Create API Key

1. Log in to watsonx.ai: https://dataplatform.cloud.ibm.com/wx/home?context=wx
2. Scroll to "Developer access" section
3. Select project: **watsonx Challenge Sandbox**
4. Click "Create API key"
5. Name: `risk-assessment-api-key`
6. Enable "Disable the leaked key" option
7. Copy key and save securely

### Step 2: Get Project ID

In the same "Developer access" section:
- Project ID displayed below project dropdown
- Copy and save for `.env` file

### Step 3: Test Connection

```python
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams

# Initialize credentials
credentials = {
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": "YOUR_API_KEY"
}

# Initialize model
model = Model(
    model_id="ibm/granite-13b-instruct-v2",
    params={
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MAX_NEW_TOKENS: 100
    },
    credentials=credentials,
    project_id="YOUR_PROJECT_ID"
)

# Test generation
response = model.generate_text("Hello, watsonx!")
print(response)
```

---

## Backend Integration

### File Structure

```
backend/
├── services/
│   ├── watsonx_service.py    # Main integration ⭐
│   ├── prompt_builder.py     # Prompt templates
│   └── token_tracker.py      # Budget management
├── config.py                 # Environment config
└── .env                      # Credentials (gitignored)
```

### watsonx_service.py

```python
"""
IBM watsonx.ai service integration for risk assessment.
"""

import os
import json
from typing import Dict, Optional
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from .prompt_builder import build_risk_prompt
from .token_tracker import TokenTracker

class WatsonXService:
    """Service for interacting with IBM watsonx.ai."""
    
    def __init__(self):
        self.credentials = {
            "url": os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
            "apikey": os.getenv("WATSONX_API_KEY")
        }
        self.project_id = os.getenv("WATSONX_PROJECT_ID")
        self.model_id = "ibm/granite-13b-instruct-v2"
        self.token_tracker = TokenTracker(budget_usd=250.0)
        
        # Validate credentials
        if not self.credentials["apikey"]:
            raise ValueError("WATSONX_API_KEY not set in environment")
        if not self.project_id:
            raise ValueError("WATSONX_PROJECT_ID not set in environment")
    
    def _get_model(self) -> Model:
        """Initialize watsonx.ai model with optimal parameters."""
        params = {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 500,
            GenParams.MIN_NEW_TOKENS: 50,
            GenParams.TEMPERATURE: 0.3,
            GenParams.TOP_P: 0.85,
            GenParams.TOP_K: 50,
            GenParams.REPETITION_PENALTY: 1.1,
            GenParams.STOP_SEQUENCES: ["\n\n\n"]
        }
        
        return Model(
            model_id=self.model_id,
            params=params,
            credentials=self.credentials,
            project_id=self.project_id
        )
    
    async def generate_explanation(
        self,
        case_id: str,
        customer_name: str,
        amount: float,
        country: str,
        risk_score: float
    ) -> Dict:
        """
        Generate AI explanation for a risk case.
        
        Args:
            case_id: Unique case identifier
            customer_name: Customer name
            amount: Transaction amount (USD)
            country: Origin country
            risk_score: Preliminary risk score (0.0-1.0)
        
        Returns:
            Dict with explanation details
        
        Raises:
            BudgetExceededError: If token budget exhausted
            WatsonXAPIError: If API call fails
        """
        # Check budget
        if self.token_tracker.is_budget_exceeded():
            raise BudgetExceededError("Token budget exhausted ($250 limit)")
        
        # Build prompt
        prompt = build_risk_prompt(
            customer_name=customer_name,
            amount=amount,
            country=country,
            risk_score=risk_score
        )
        
        try:
            # Generate response
            model = self._get_model()
            response_text = model.generate_text(prompt=prompt)
            
            # Parse response (expecting JSON)
            response_data = self._parse_response(response_text)
            
            # Track token usage
            tokens_used = self._estimate_tokens(prompt, response_text)
            self.token_tracker.add_usage(tokens_used)
            
            # Add metadata
            response_data["case_id"] = case_id
            response_data["model_used"] = self.model_id
            response_data["tokens_consumed"] = tokens_used
            
            return response_data
        
        except Exception as e:
            # Log error and return fallback
            print(f"watsonx.ai error: {e}")
            return self._fallback_response(case_id, risk_score)
    
    def _parse_response(self, text: str) -> Dict:
        """Parse JSON response from model."""
        try:
            # Try to extract JSON from response
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = text[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            raise ValueError(f"Failed to parse model response: {e}")
    
    def _estimate_tokens(self, prompt: str, response: str) -> int:
        """Estimate token count (rough approximation)."""
        # Rule of thumb: 1 token ≈ 4 characters
        total_chars = len(prompt) + len(response)
        return total_chars // 4
    
    def _fallback_response(self, case_id: str, risk_score: float) -> Dict:
        """Return rule-based response if AI fails."""
        if risk_score >= 0.8:
            return {
                "case_id": case_id,
                "confidence": 0.0,
                "rationale": "AI service unavailable. High-risk transaction requires manual review.",
                "recommended_action": "HOLD transaction and escalate to senior analyst.",
                "model_used": "fallback-rule-based",
                "tokens_consumed": 0
            }
        elif risk_score >= 0.5:
            return {
                "case_id": case_id,
                "confidence": 0.0,
                "rationale": "AI service unavailable. Medium-risk transaction detected.",
                "recommended_action": "Review transaction details and customer history.",
                "model_used": "fallback-rule-based",
                "tokens_consumed": 0
            }
        else:
            return {
                "case_id": case_id,
                "confidence": 0.0,
                "rationale": "AI service unavailable. Low-risk transaction.",
                "recommended_action": "Approve with standard monitoring.",
                "model_used": "fallback-rule-based",
                "tokens_consumed": 0
            }
    
    def get_budget_status(self) -> Dict:
        """Get current token budget status."""
        return self.token_tracker.get_status()


class BudgetExceededError(Exception):
    """Raised when token budget is exhausted."""
    pass


class WatsonXAPIError(Exception):
    """Raised when watsonx.ai API call fails."""
    pass
```

### prompt_builder.py

```python
"""
Prompt template builder for watsonx.ai.
"""

def build_risk_prompt(
    customer_name: str,
    amount: float,
    country: str,
    risk_score: float
) -> str:
    """
    Build risk assessment prompt for watsonx.ai.
    
    See docs/AI_PROMPTS.md for full template details.
    """
    return f"""You are an expert banking compliance analyst specializing in fraud detection and anti-money laundering (AML) compliance. Your role is to assess transaction risk, explain your reasoning clearly, and recommend appropriate actions following regulatory standards (FinCEN, BSA/AML).

Analyze this flagged banking transaction:

**Transaction Details:**
- Customer: {customer_name}
- Amount: ${amount:.2f} USD
- Origin Country: {country}
- Transaction Type: International Wire Transfer
- Customer History: Typical transactions: $200-800 domestic, USA only

**Current Risk Indicators:**
- Preliminary Risk Score: {risk_score:.2f}
- Flagged Reasons: Unusual pattern detected

**Your Task:**
1. Assess the fraud/AML risk on a scale of 0.0 (no risk) to 1.0 (critical risk)
2. Explain your reasoning in 2-3 clear sentences
3. Recommend specific next actions for the compliance officer

**Response Format (JSON):**
```json
{{
  "confidence": 0.XX,
  "rationale": "...",
  "recommended_action": "..."
}}
```

**Guidelines:**
- Be concise but thorough
- Reference specific red flags
- Consider regulatory compliance requirements
- Recommend proportional actions"""
```

### token_tracker.py

```python
"""
Track watsonx.ai token usage against budget.
"""

class TokenTracker:
    """Track token consumption and budget."""
    
    def __init__(self, budget_usd: float = 250.0):
        self.budget_usd = budget_usd
        self.tokens_used = 0
        self.requests_count = 0
        self.cost_per_1k_tokens = 0.0001  # $0.0001 per 1K tokens
    
    def add_usage(self, tokens: int):
        """Record token usage."""
        self.tokens_used += tokens
        self.requests_count += 1
    
    def get_spent_usd(self) -> float:
        """Calculate total spend."""
        return (self.tokens_used / 1000) * self.cost_per_1k_tokens
    
    def get_remaining_usd(self) -> float:
        """Calculate remaining budget."""
        return self.budget_usd - self.get_spent_usd()
    
    def is_budget_exceeded(self) -> bool:
        """Check if budget is exhausted."""
        return self.get_remaining_usd() <= 0
    
    def get_status(self) -> dict:
        """Get budget status summary."""
        spent = self.get_spent_usd()
        return {
            "total_budget_usd": self.budget_usd,
            "spent_usd": round(spent, 2),
            "remaining_usd": round(self.get_remaining_usd(), 2),
            "tokens_used": self.tokens_used,
            "requests_count": self.requests_count,
            "percentage_used": round((spent / self.budget_usd) * 100, 2)
        }
```

---

## API Endpoints Using watsonx.ai

### POST /explain

```python
from fastapi import APIRouter, HTTPException
from services.watsonx_service import WatsonXService, BudgetExceededError
from models import Case
from database import get_db

router = APIRouter()
watsonx = WatsonXService()

@router.post("/explain")
async def explain_case(request: dict):
    """Generate AI explanation for a case."""
    case_id = request.get("case_id")
    
    # Fetch case from database
    db = get_db()
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    try:
        # Generate explanation via watsonx.ai
        explanation = await watsonx.generate_explanation(
            case_id=case.id,
            customer_name=case.customer_name,
            amount=case.amount,
            country=case.country,
            risk_score=case.risk_score
        )
        
        return explanation
    
    except BudgetExceededError:
        raise HTTPException(status_code=429, detail="Token budget exhausted")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")
```

---

## Best Practices

### 1. Error Handling
- Always implement fallback responses
- Use try/except for all watsonx.ai calls
- Log errors for debugging

### 2. Token Management
- Monitor budget in real-time
- Alert at 80% usage ($200)
- Cache responses to reduce costs

### 3. Response Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

cache = {}

def get_cached_explanation(case_id: str):
    """Get cached explanation if within TTL."""
    if case_id in cache:
        cached_data, timestamp = cache[case_id]
        if datetime.now() - timestamp < timedelta(hours=1):
            return cached_data
    return None

def cache_explanation(case_id: str, explanation: dict):
    """Cache explanation for 1 hour."""
    cache[case_id] = (explanation, datetime.now())
```

### 4. Monitoring
- Track API latency
- Log all requests/responses
- Monitor error rates

---

## Testing

### Unit Tests

```python
import pytest
from services.watsonx_service import WatsonXService

@pytest.fixture
def watsonx():
    return WatsonXService()

def test_generate_explanation(watsonx):
    """Test explanation generation."""
    result = watsonx.generate_explanation(
        case_id="test-123",
        customer_name="Test User",
        amount=5000.0,
        country="US",
        risk_score=0.7
    )
    
    assert "confidence" in result
    assert "rationale" in result
    assert "recommended_action" in result
```

### Manual Testing in Prompt Lab

1. Open Prompt Lab: https://dataplatform.cloud.ibm.com/wx/home?context=wx
2. Select `ibm/granite-13b-instruct-v2`
3. Paste prompt from `docs/AI_PROMPTS.md`
4. Test with different risk scenarios
5. Validate response quality

---

## Troubleshooting

### Issue: "Invalid API key"
**Solution**: Regenerate API key in watsonx.ai Developer Access

### Issue: "Budget exceeded"
**Solution**: Request credit increase via IBM SkillsBuild support (requires justification)

### Issue: "Timeout after 30s"
**Solution**: 
- Reduce `max_new_tokens` to 300
- Implement retry logic with exponential backoff
- Use cached response

### Issue: "Malformed JSON response"
**Solution**: 
- Improve prompt with explicit JSON format example
- Add response parsing validation
- Use fallback if parsing fails

---

## Resources

- [IBM watsonx.ai Documentation](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models.html)
- [Granite Model Details](https://www.ibm.com/products/watsonx-ai/foundation-models)
- [Python SDK Reference](https://ibm.github.io/watson-machine-learning-sdk/)
- [Prompt Engineering Guide](https://www.ibm.com/docs/en/watsonx-as-a-service?topic=lab-prompt-tips)

