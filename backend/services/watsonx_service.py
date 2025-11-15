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
            GenParams.MAX_NEW_TOKENS: 800,  # Increased for complete responses
            GenParams.MIN_NEW_TOKENS: 50,
            GenParams.TEMPERATURE: 0.3,
            GenParams.TOP_K: 50,
            GenParams.TOP_P: 0.9,
            GenParams.REPETITION_PENALTY: 1.1,
            GenParams.STOP_SEQUENCES: ["Prompt:", "\n\nPrompt:"],  # Stop if echoing prompt
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
    
    def _clean_response(self, response: str) -> str:
        """
        Clean AI response by removing prompt echoing, hallucinations, and truncations.
        
        Args:
            response: Raw response from watsonx.ai
            
        Returns:
            Cleaned response text
        """
        # Remove prompt echo if present (case-insensitive)
        prompt_markers = [
            "Prompt:",
            "\n\nPrompt:",
            "Prompt 2:",
            "\n\nPrompt 2:",
            "Example:",
            "\n\nExample:",
            "Another example:",
            "Analyze this banking transaction",
        ]
        
        for marker in prompt_markers:
            if marker in response:
                # Split and keep only the first part
                response = response.split(marker)[0].strip()
        
        # Remove common AI meta-text
        meta_patterns = [
            "Here is the analysis:",
            "Here's the analysis:",
            "Analysis:",
        ]
        for pattern in meta_patterns:
            if response.startswith(pattern):
                response = response[len(pattern):].strip()
        
        # Remove incomplete numbered list items (e.g., "3." with no content)
        import re
        # Remove lines that are just a number followed by period and whitespace/newline
        response = re.sub(r'\n\d+\.\s*\n', '\n', response)
        # Also remove if it's at the end
        response = re.sub(r'\n\d+\.\s*$', '', response)
        
        return response.strip()

    def generate_explanation(
        self,
        customer_name: str,
        amount: float,
        country: str,
        risk_score: float,
        account_age_days: int = None,
        transaction_count_30d: int = None,
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
            account_age_days=account_age_days,
            transaction_count_30d=transaction_count_30d,
        )

        # Generate response
        start_time = time.time()
        
        try:
            response = self._model.generate_text(prompt=prompt)
            
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            # Debug: Print raw response
            print(f"\n{'='*60}")
            print("RAW AI RESPONSE (Explanation):")
            print(f"{'='*60}")
            print(response)
            print(f"{'='*60}\n")
            
            # Clean and parse response
            explanation_text = self._clean_response(response)
            
            # Debug: Print cleaned response
            print(f"\n{'='*60}")
            print("CLEANED RESPONSE (Explanation):")
            print(f"{'='*60}")
            print(explanation_text)
            print(f"{'='*60}\n")
            
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

    def generate_risk_score(
        self,
        customer_name: str,
        amount: float,
        country: str,
        transaction_type: str = "wire transfer",
    ) -> Dict[str, Any]:
        """
        Generate AI-powered risk score for a transaction
        
        Args:
            customer_name: Customer name
            amount: Transaction amount in USD
            country: Country code
            transaction_type: Type of transaction
            
        Returns:
            Dictionary with:
            - risk_score: Calculated risk score (0.0-1.0)
            - reasoning: Explanation of the score
            - risk_level: LOW/MEDIUM/HIGH
            - tokens_consumed: Number of tokens used
            - generation_time_ms: Generation time in milliseconds
            
        Raises:
            Exception: If watsonx.ai is unavailable or request fails
        """
        if not self.is_available():
            raise Exception("watsonx.ai service is not available")
        
        # Check budget
        if not self.token_tracker.is_within_budget(estimated_tokens=300):
            raise Exception("Token budget exceeded")
        
        # Build prompt
        prompt = self.prompt_builder.build_risk_scoring_prompt(
            customer_name=customer_name,
            amount=amount,
            country=country,
            transaction_type=transaction_type,
        )
        
        # Generate response
        start_time = time.time()
        
        try:
            response = self._model.generate_text(prompt=prompt)
            
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            # Clean and parse the response
            cleaned_response = self._clean_response(response)
            risk_score, reasoning, risk_level = self._parse_risk_score(cleaned_response)
            
            # Estimate tokens
            tokens_consumed = len(prompt + response) // 4
            
            # Track usage
            self.token_tracker.track_request(
                tokens_used=tokens_consumed,
                model=self.MODEL_ID,
                endpoint="/calculate-risk",
                metadata={
                    "customer_name": customer_name,
                    "amount": amount,
                    "country": country,
                },
            )
            
            return {
                "risk_score": risk_score,
                "reasoning": reasoning,
                "risk_level": risk_level,
                "tokens_consumed": tokens_consumed,
                "generation_time_ms": generation_time_ms,
            }
            
        except Exception as e:
            print(f"✗ Risk score generation failed: {e}")
            raise Exception(f"AI risk scoring failed: {str(e)}")

    def generate_risk_category(
        self,
        customer_name: str,
        amount: float,
        country: str,
        transaction_type: str = "wire transfer",
    ) -> Dict[str, Any]:
        """
        Categorize risk type for a transaction using watsonx.ai

        Args:
            customer_name: Customer name
            amount: Transaction amount in USD
            country: Country code
            transaction_type: Type of transaction

        Returns:
            Dictionary with:
            - risk_category: Categorized risk type (e.g., Fraud, AML, Sanctions)
            - tokens_consumed: Number of tokens used
            - generation_time_ms: Generation time in milliseconds

        Raises:
            Exception: If watsonx.ai is unavailable or request fails
        """
        if not self.is_available():
            raise Exception("watsonx.ai service is not available")
        
        # Check budget
        if not self.token_tracker.is_within_budget(estimated_tokens=300):
            raise Exception("Token budget exceeded")

        # Build prompt
        prompt = self.prompt_builder.build_risk_category_prompt(
            custoner_name=customer_name,
            amount=amount,
            country=country,
            transaction_type=transaction_type,
        )

        start_time = time.time()
        try:
            response = self._model.generate_text(prompt=prompt)
            
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            # Clean and parse the response
            cleaned_response = self._clean_response(response)
            risk_category, reasoning = self.parse_risk_category(cleaned_response)
            
            # Estimate tokens
            tokens_consumed = len(prompt + response) // 4
            
            # Track usage
            self.token_tracker.track_request(
                tokens_used=tokens_consumed,
                model=self.MODEL_ID,
                endpoint="/calculate-risk",
                metadata={
                    "customer_name": customer_name,
                    "amount": amount,
                    "country": country,
                },
            )
            
            return {
                "risk_category": risk_category,
                "reasoning": reasoning,
                "tokens_consumed": tokens_consumed,
                "generation_time_ms": generation_time_ms,
            }
            
        except Exception as e:
            print(f"✗ Risk score generation failed: {e}")
            raise Exception(f"AI risk scoring failed: {str(e)}")

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
    
    def parse_risk_category(self, text: str) -> tuple[str, str]:
        """
        Parse risk category response from AI
        
        Args:
            text: Raw AI response
        """
        
        import re
        # Extract risk category
        category_match = re.search(r'RISK_CATEGORY:\s*(.+?)(?=REASONING:|$)', text, re.IGNORECASE | re.DOTALL)
        risk_category = category_match.group(1).strip() if category_match else "Uncategorized"
        # Extract reasoning
        reasoning_match = re.search(r'REASONING:\s*(.+)', text, re.IGNORECASE | re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided."
        return risk_category, reasoning

    def analyze_compliance_with_rag(
        self,
        customer_name: str,
        amount: float,
        country: str,
        risk_score: float,
        document_context: str,
        account_age_days: int = None,
        transaction_count_30d: int = None,
    ) -> Dict[str, Any]:
        """
        Analyze transaction compliance using RAG (Retrieval Augmented Generation).
        Uses uploaded compliance documents to provide context-aware analysis.
        
        Args:
            customer_name: Customer name
            amount: Transaction amount in USD
            country: Country code
            risk_score: Current risk score
            document_context: Relevant text from compliance documents
            
        Returns:
            Dictionary with:
            - compliance_status: COMPLIANT|NON_COMPLIANT|REVIEW_REQUIRED
            - violations: List of potential violations
            - relevant_regulations: List of applicable regulations
            - recommendation: Compliance recommendation
            - confidence: Analysis confidence
            - tokens_consumed: Number of tokens used
            - generation_time_ms: Generation time in milliseconds
            
        Raises:
            Exception: If watsonx.ai is unavailable or request fails
        """
        if not self.is_available():
            raise Exception("watsonx.ai service is not available")
        
        # Check budget
        if not self.token_tracker.is_within_budget(estimated_tokens=500):
            raise Exception("Token budget exceeded")
        
        # Build RAG prompt with document context
        prompt = self._build_compliance_rag_prompt(
            customer_name=customer_name,
            amount=amount,
            country=country,
            risk_score=risk_score,
            document_context=document_context,
            account_age_days=account_age_days,
            transaction_count_30d=transaction_count_30d,
        )
        
        # Generate response
        start_time = time.time()
        
        try:
            response = self._model.generate_text(prompt=prompt)
            
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            # Clean and parse the response
            cleaned_response = self._clean_response(response)
            parsed = self._parse_compliance_analysis(cleaned_response)
            
            # Estimate tokens
            tokens_consumed = len(prompt + response) // 4
            
            # Track usage
            self.token_tracker.track_request(
                tokens_used=tokens_consumed,
                model=self.MODEL_ID,
                endpoint="/analyze-compliance",
                metadata={
                    "customer_name": customer_name,
                    "amount": amount,
                    "country": country,
                },
            )
            
            return {
                **parsed,
                "tokens_consumed": tokens_consumed,
                "generation_time_ms": generation_time_ms,
            }
            
        except Exception as e:
            print(f"✗ Compliance analysis failed: {e}")
            raise Exception(f"AI compliance analysis failed: {str(e)}")
    
    def _build_compliance_rag_prompt(
        self,
        customer_name: str,
        amount: float,
        country: str,
        risk_score: float,
        document_context: str,
        account_age_days: int = None,
        transaction_count_30d: int = None,
    ) -> str:
        """Build RAG prompt for compliance analysis."""
        # Build AML indicators section
        aml_indicators = ""
        if account_age_days is not None:
            aml_indicators += f"\nAccount Age: {account_age_days} days"
        if transaction_count_30d is not None:
            aml_indicators += f"\nTransaction Velocity: {transaction_count_30d} large transactions in past 30 days"
        
        prompt = f"""You are a compliance analyst reviewing a banking transaction. Use the provided compliance documents to determine if this transaction violates any regulations.

=== COMPLIANCE DOCUMENTS ===
{document_context}

=== TRANSACTION TO ANALYZE ===
Customer: {customer_name}
Amount: ${amount:,.2f} USD
Country: {country}
Current Risk Score: {risk_score:.2f} (0.0 = low risk, 1.0 = high risk){aml_indicators}

=== INSTRUCTIONS ===
Based on the compliance documents above, analyze this transaction and provide your assessment in EXACTLY this format:

COMPLIANCE_STATUS: [COMPLIANT/NON_COMPLIANT/REVIEW_REQUIRED]
VIOLATIONS: [List any potential violations, one per line, or "None" if compliant]
RELEVANT_REGULATIONS: [List applicable regulations from the documents, one per line]
RECOMMENDATION: [Your specific recommendation for this transaction]
CONFIDENCE: [number between 0.0 and 1.0 indicating your confidence in this analysis]

Example:
COMPLIANCE_STATUS: REVIEW_REQUIRED
VIOLATIONS: Transaction exceeds $10,000 threshold requiring enhanced due diligence
RELEVANT_REGULATIONS: AML Policy - Enhanced Due Diligence requirement; KYC Guidelines - Risk-Based Approach
RECOMMENDATION: Conduct enhanced due diligence before processing. Verify source of funds and beneficial ownership.
CONFIDENCE: 0.85"""

        return prompt
    
    def _parse_compliance_analysis(self, text: str) -> Dict[str, Any]:
        """Parse compliance analysis response from AI."""
        import re
        
        # Extract compliance status
        status_match = re.search(
            r'COMPLIANCE_STATUS:\s*(COMPLIANT|NON_COMPLIANT|REVIEW_REQUIRED)',
            text,
            re.IGNORECASE
        )
        compliance_status = status_match.group(1).upper() if status_match else "REVIEW_REQUIRED"
        
        # Extract violations
        violations_match = re.search(
            r'VIOLATIONS:\s*(.+?)(?=RELEVANT_REGULATIONS:|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        violations_text = violations_match.group(1).strip() if violations_match else "None identified"
        
        # Parse violations list
        violations = []
        if violations_text.lower() != "none" and "none" not in violations_text.lower():
            # Split by newlines or semicolons
            violations = [
                v.strip("- •").strip()
                for v in re.split(r'[;\n]', violations_text)
                if v.strip() and v.strip() != "None"
            ]
        
        # Extract regulations
        regulations_match = re.search(
            r'RELEVANT_REGULATIONS:\s*(.+?)(?=RECOMMENDATION:|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        regulations_text = regulations_match.group(1).strip() if regulations_match else ""
        
        # Parse regulations list
        relevant_regulations = [
            r.strip("- •").strip()
            for r in re.split(r'[;\n]', regulations_text)
            if r.strip()
        ]
        
        # Extract recommendation
        recommendation_match = re.search(
            r'RECOMMENDATION:\s*(.+?)(?=CONFIDENCE:|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        recommendation = recommendation_match.group(1).strip() if recommendation_match else "Manual review recommended"
        
        # Extract confidence
        confidence_match = re.search(r'CONFIDENCE:\s*(0?\.\d+|1\.0|0|1)', text, re.IGNORECASE)
        confidence = float(confidence_match.group(1)) if confidence_match else 0.7
        confidence = max(0.0, min(1.0, confidence))
        
        return {
            "compliance_status": compliance_status,
            "violations": violations,
            "relevant_regulations": relevant_regulations,
            "recommendation": recommendation,
            "confidence": confidence,
        }
    
    def _parse_risk_score(self, text: str) -> tuple[float, str, str]:
        """
        Parse risk score response from AI
        
        Args:
            text: Raw AI response
            
        Returns:
            (risk_score, reasoning, risk_level) tuple
        """
        import re
        
        # Extract risk score
        score_match = re.search(r'RISK_SCORE:\s*(0?\.\d+|1\.0|0|1)', text, re.IGNORECASE)
        risk_score = float(score_match.group(1)) if score_match else 0.5
        
        # Ensure risk score is between 0 and 1
        risk_score = max(0.0, min(1.0, risk_score))
        
        # Extract reasoning
        reasoning_match = re.search(r'REASONING:\s*(.+?)(?=RISK_LEVEL:|$)', text, re.IGNORECASE | re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else "Risk assessment completed."
        
        # Extract risk level
        level_match = re.search(r'RISK_LEVEL:\s*(LOW|MEDIUM|HIGH)', text, re.IGNORECASE)
        risk_level = level_match.group(1).upper() if level_match else self._calculate_risk_level(risk_score)
        
        return risk_score, reasoning, risk_level
    
    def _calculate_risk_level(self, risk_score: float) -> str:
        """Calculate risk level from score"""
        if risk_score >= 0.7:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    def _parse_explanation(self, text: str) -> tuple[str, str]:
        """
        Parse explanation into rationale and action

        Args:
            text: Raw explanation text

        Returns:
            (rationale, recommended_action) tuple
        """
        import re
        
        # Try to split by common delimiters (case-insensitive)
        # Handle numbered list format: "3. Recommended action:"
        patterns = [
            r'(?:^\d+\.\s*)?Recommended action:\s*',
            r'(?:^\d+\.\s*)?Recommendation:\s*',
        ]
        
        rationale = text.strip()
        action = "Review this transaction for potential risk factors."
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Split at the match
                rationale = text[:match.start()].strip()
                action = text[match.end():].strip()
                break
        
        # Clean up any trailing numbered items in rationale
        rationale = re.sub(r'\n\d+\.\s*$', '', rationale).strip()
        
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

