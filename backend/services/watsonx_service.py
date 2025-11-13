"""
IBM watsonx.ai Service

Integrates with IBM watsonx.ai API using the Granite-13b-instruct-v2 model.
Handles authentication, request formatting, and response parsing.

NOTE: Requires Python 3.10+ for IBM Watson ML SDK.
Falls back to mock responses if SDK unavailable.
"""

from typing import Dict, Any, Optional
import time

from config import get_settings
from services.prompt_builder import PromptBuilder
from services.token_tracker import TokenTracker

# Try to import IBM Watson ML SDK (requires Python 3.10+)
try:
    from ibm_watson_machine_learning.foundation_models import Model
    from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
    WATSONX_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ IBM Watson ML SDK not available: {e}")
    print("   Requires Python 3.10+. Falling back to mock AI responses.")
    WATSONX_AVAILABLE = False
    Model = None
    GenParams = None


class WatsonXService:
    """Service for interacting with IBM watsonx.ai"""

    # Model configuration
    MODEL_ID = "ibm/granite-3-2-8b-instruct"
    
    # Generation parameters (see docs/AI_PROMPTS.md)
    # Note: Will be None if SDK not available
    DEFAULT_PARAMS = None
    
    @classmethod
    def _get_params(cls):
        """Get generation parameters (only if SDK available)"""
        if not WATSONX_AVAILABLE or GenParams is None:
            return None
        return {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 300,
            GenParams.MIN_NEW_TOKENS: 50,
            GenParams.TEMPERATURE: 0.3,
            GenParams.TOP_K: 50,
            GenParams.TOP_P: 0.9,
            GenParams.REPETITION_PENALTY: 1.1,
        }

    def __init__(self):
        """Initialize watsonx.ai service"""
        self.settings = get_settings()
        self.prompt_builder = PromptBuilder()
        self.token_tracker = TokenTracker(budget_usd=self.settings.token_budget_usd)
        
        # Initialize the model
        self._model: Optional[Model] = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the IBM watsonx.ai model"""
        # Check if SDK is available
        if not WATSONX_AVAILABLE:
            print("ℹ️  watsonx.ai SDK not available (requires Python 3.10+)")
            print("   Using mock AI responses instead")
            self._model = None
            return
            
        # Check if credentials are configured
        if not self.settings.watsonx_api_key or not self.settings.watsonx_project_id:
            print("ℹ️  watsonx.ai credentials not configured")
            print("   Using mock AI responses instead")
            self._model = None
            return
        
        try:
            credentials = {
                "url": self.settings.watsonx_url,
                "apikey": self.settings.watsonx_api_key,
            }

            self._model = Model(
                model_id=self.MODEL_ID,
                params=self._get_params(),
                credentials=credentials,
                project_id=self.settings.watsonx_project_id,
            )
            
            print(f"✓ watsonx.ai initialized: {self.MODEL_ID}")
        except Exception as e:
            print(f"✗ Failed to initialize watsonx.ai: {e}")
            print("   Using mock AI responses instead")
            self._model = None

    def is_available(self) -> bool:
        """Check if watsonx.ai is available"""
        return self._model is not None

    def generate_explanation(
        self,
        customer_name: str,
        amount: float,
        country: str,
        risk_score: float,
    ) -> Dict[str, Any]:
        """
        Generate risk explanation using watsonx.ai

        Args:
            customer_name: Customer name
            amount: Transaction amount
            country: Country code
            risk_score: Risk score (0.0-1.0)

        Returns:
            Dictionary with explanation data:
            - rationale: Explanation text
            - recommended_action: Action recommendation
            - confidence: Model confidence (0.0-1.0)
            - tokens_consumed: Number of tokens used
            - generation_time_ms: Generation time in milliseconds

        Raises:
            Exception: If watsonx.ai is unavailable or request fails
        """
        if not self.is_available():
            raise Exception("watsonx.ai service is not available")

        # Check budget before making request
        if not self.token_tracker.is_within_budget(estimated_tokens=500):
            raise Exception("Token budget exceeded")

        # Build prompt
        prompt = self.prompt_builder.build_explanation_prompt(
            customer_name=customer_name,
            amount=amount,
            country=country,
            risk_score=risk_score,
        )

        # Generate response
        start_time = time.time()
        
        try:
            response = self._model.generate_text(prompt=prompt)
            
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            # Parse response (watsonx.ai returns text directly)
            explanation_text = response.strip()
            
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            tokens_consumed = len(prompt + explanation_text) // 4
            
            # Track usage
            self.token_tracker.track_request(
                tokens_used=tokens_consumed,
                model=self.MODEL_ID,
                endpoint="/explain",
                metadata={
                    "customer": customer_name,
                    "amount": amount,
                    "risk_score": risk_score,
                },
            )
            
            # Parse explanation into sections
            rationale, recommended_action = self._parse_explanation(explanation_text)
            
            # Estimate confidence based on risk score and response
            confidence = self._estimate_confidence(risk_score, explanation_text)
            
            return {
                "rationale": rationale,
                "recommended_action": recommended_action,
                "confidence": confidence,
                "tokens_consumed": tokens_consumed,
                "generation_time_ms": generation_time_ms,
            }
            
        except Exception as e:
            print(f"✗ watsonx.ai generation failed: {e}")
            raise Exception(f"AI generation failed: {str(e)}")

    def generate_report_summary(
        self,
        total_cases: int,
        high_risk_count: int,
        medium_risk_count: int,
        low_risk_count: int,
        avg_risk: float,
        total_amount: float,
    ) -> Dict[str, Any]:
        """
        Generate report summary using watsonx.ai

        Args:
            total_cases: Total number of cases
            high_risk_count: Number of high-risk cases
            medium_risk_count: Number of medium-risk cases
            low_risk_count: Number of low-risk cases
            avg_risk: Average risk score
            total_amount: Total transaction volume

        Returns:
            Dictionary with summary data:
            - summary: Executive summary text
            - tokens_consumed: Number of tokens used
            - generation_time_ms: Generation time in milliseconds

        Raises:
            Exception: If watsonx.ai is unavailable or request fails
        """
        if not self.is_available():
            raise Exception("watsonx.ai service is not available")

        # Check budget
        if not self.token_tracker.is_within_budget(estimated_tokens=400):
            raise Exception("Token budget exceeded")

        # Build prompt
        prompt = self.prompt_builder.build_report_summary_prompt(
            total_cases=total_cases,
            high_risk_count=high_risk_count,
            medium_risk_count=medium_risk_count,
            low_risk_count=low_risk_count,
            avg_risk=avg_risk,
            total_amount=total_amount,
        )

        # Generate response
        start_time = time.time()
        
        try:
            response = self._model.generate_text(prompt=prompt)
            
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            summary_text = response.strip()
            
            # Estimate tokens
            tokens_consumed = len(prompt + summary_text) // 4
            
            # Track usage
            self.token_tracker.track_request(
                tokens_used=tokens_consumed,
                model=self.MODEL_ID,
                endpoint="/report",
                metadata={
                    "total_cases": total_cases,
                    "high_risk_count": high_risk_count,
                },
            )
            
            return {
                "summary": summary_text,
                "tokens_consumed": tokens_consumed,
                "generation_time_ms": generation_time_ms,
            }
            
        except Exception as e:
            print(f"✗ watsonx.ai generation failed: {e}")
            raise Exception(f"AI generation failed: {str(e)}")

    def _parse_explanation(self, text: str) -> tuple[str, str]:
        """
        Parse explanation into rationale and action

        Args:
            text: Raw explanation text

        Returns:
            (rationale, recommended_action) tuple
        """
        # Try to split by common delimiters
        if "Recommended action:" in text:
            parts = text.split("Recommended action:", 1)
            rationale = parts[0].strip()
            action = parts[1].strip()
        elif "Recommendation:" in text:
            parts = text.split("Recommendation:", 1)
            rationale = parts[0].strip()
            action = parts[1].strip()
        else:
            # If no clear split, use the whole text as rationale
            # and generate a default action
            rationale = text.strip()
            action = "Review this transaction for potential risk factors."

        return rationale, action

    def _estimate_confidence(self, risk_score: float, explanation: str) -> float:
        """
        Estimate model confidence based on risk score and explanation

        Args:
            risk_score: Original risk score
            explanation: Generated explanation text

        Returns:
            Confidence score (0.0-1.0)
        """
        # Base confidence on risk score extremeness
        # High/low risk scores = higher confidence
        # Medium risk scores = lower confidence
        
        if risk_score >= 0.8 or risk_score <= 0.2:
            base_confidence = 0.9
        elif risk_score >= 0.6 or risk_score <= 0.4:
            base_confidence = 0.75
        else:
            base_confidence = 0.6

        # Adjust based on explanation length (longer = more confident)
        if len(explanation) > 200:
            base_confidence += 0.05
        elif len(explanation) < 100:
            base_confidence -= 0.05

        # Clamp to [0.5, 0.95]
        return max(0.5, min(0.95, base_confidence))

    def get_token_usage(self) -> Dict[str, Any]:
        """Get current token usage statistics"""
        return self.token_tracker.get_usage_summary()

    def check_budget_status(self) -> tuple[bool, str]:
        """Check if budget warning is needed"""
        return self.token_tracker.check_budget_warning()

