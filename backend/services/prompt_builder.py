"""
Prompt Builder for watsonx.ai

Constructs optimized prompts for risk assessment explanations.
See docs/AI_PROMPTS.md for prompt engineering guidelines.
"""

from typing import Dict, Any


class PromptBuilder:
    """Builds prompts for IBM watsonx.ai Granite models"""

    SYSTEM_ROLE = """You are a financial risk assessment expert specializing in anti-money laundering (AML) and fraud detection.
Your role is to analyze banking transactions and provide clear, actionable explanations for compliance officers.

Guidelines:
- Be concise but thorough (2-3 sentences)
- Focus on risk factors: amount, country, patterns
- Provide specific, actionable recommendations
- Use professional, clear language
- Consider both false positives and genuine risks"""

    def __init__(self):
        """Initialize the prompt builder"""
        pass

    def build_explanation_prompt(
        self,
        customer_name: str,
        amount: float,
        country: str,
        risk_score: float,
    ) -> str:
        """
        Build a prompt for risk explanation

        Args:
            customer_name: Customer name
            amount: Transaction amount in USD
            country: Country code (e.g., "USA", "SG")
            risk_score: Risk score between 0.0 and 1.0

        Returns:
            Formatted prompt string for watsonx.ai
        """
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "HIGH"
        elif risk_score >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Build the user prompt
        user_prompt = f"""Analyze this banking transaction for risk:

Customer: {customer_name}
Amount: ${amount:,.2f} USD
Country: {country}
Risk Score: {risk_score:.2f} ({risk_level} RISK)

Provide:
1. Brief explanation of why this transaction has a {risk_level} risk score
2. Key risk factors (amount, country, patterns)
3. Recommended action (approve, review, escalate)

Keep your response concise (2-3 sentences per section)."""

        return user_prompt

    def build_risk_category_prompt(
        self,
        custoner_name: str,
        amount: float,
        country: str,
        transaction_type: str = "wire transfer",
    ) -> str:
        """
        Build a prompt for AI-powered risk category classification
        
        Args:
            custoner_name: Customer name
            amount: Transaction amount in USD
            country: Country code (e.g., "USA", "SG")
            transaction_type: Type of transaction
        """
        prompt = f"""Classify the risk category of this banking transaction:
        Customer: {custoner_name}
        Transaction Amount: ${amount:,.2f} USD
        Country: {country}
        Transaction Type: {transaction_type}
        Possible risk categories:
        1. Fraud
        2. Money Laundering
        3. Sanctions Violation
        Provide your response in EXACTLY this format:
        RISK_CATEGORY: [Fraud/Money Laundering/Sanctions Violation/None]
        REASONING: [2-3 sentence explanation of key risk factors]
        """
        return prompt

    def build_risk_scoring_prompt(
        self,
        customer_name: str,
        amount: float,
        country: str,
        transaction_type: str = "wire transfer",
    ) -> str:
        """
        Build a prompt for AI-powered risk score calculation
        
        Args:
            customer_name: Customer name
            amount: Transaction amount in USD
            country: Country code (e.g., "USA", "SG")
            transaction_type: Type of transaction
            
        Returns:
            Formatted prompt for risk score generation
        """
        user_prompt = f"""Analyze this banking transaction and calculate a risk score:

Customer: {customer_name}
Transaction Amount: ${amount:,.2f} USD
Country: {country}
Transaction Type: {transaction_type}

Calculate a risk score between 0.0 (no risk) and 1.0 (very high risk) based on:
1. Transaction amount (large amounts = higher risk)
2. Country risk profile (high-risk jurisdictions)
3. Typical patterns for this transaction type
4. AML/fraud indicators

Provide your response in EXACTLY this format:
RISK_SCORE: [number between 0.0 and 1.0]
REASONING: [2-3 sentence explanation of key risk factors]
RISK_LEVEL: [LOW/MEDIUM/HIGH]

Example:
RISK_SCORE: 0.75
REASONING: Large transaction amount ($50,000) to a high-risk jurisdiction raises AML concerns. The country has known issues with financial crime. Additional due diligence is recommended.
RISK_LEVEL: HIGH"""

        return user_prompt

    def build_report_summary_prompt(
        self,
        total_cases: int,
        high_risk_count: int,
        medium_risk_count: int,
        low_risk_count: int,
        avg_risk: float,
        total_amount: float,
    ) -> str:
        """
        Build a prompt for report summary generation

        Args:
            total_cases: Total number of cases analyzed
            high_risk_count: Number of high-risk cases
            medium_risk_count: Number of medium-risk cases
            low_risk_count: Number of low-risk cases
            avg_risk: Average risk score (0.0-1.0)
            total_amount: Total transaction volume in USD

        Returns:
            Formatted prompt string for report summary
        """
        user_prompt = f"""Generate an executive summary for this risk assessment report:

Total Cases: {total_cases}
Total Transaction Volume: ${total_amount:,.2f} USD
Average Risk Score: {avg_risk:.2f}

Risk Distribution:
- High Risk (≥0.7): {high_risk_count} cases
- Medium Risk (0.4-0.69): {medium_risk_count} cases
- Low Risk (<0.4): {low_risk_count} cases

Provide a brief (2-3 sentence) executive summary highlighting:
1. Overall risk assessment
2. Key concerns or patterns
3. Recommended priority actions

Be concise and actionable."""

        return user_prompt

    def format_full_prompt(self, user_prompt: str) -> str:
        """
        Combine system role and user prompt

        Args:
            user_prompt: The specific task prompt

        Returns:
            Full formatted prompt with system context
        """
        return f"""{self.SYSTEM_ROLE}

{user_prompt}"""

    def optimize_for_token_limit(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Ensure prompt fits within token budget

        Args:
            prompt: The prompt to optimize
            max_tokens: Maximum allowed tokens (approximate)

        Returns:
            Optimized prompt (truncated if necessary)
        """
        # Rough approximation: 1 token ≈ 4 characters
        max_chars = max_tokens * 4

        if len(prompt) > max_chars:
            # Truncate and add ellipsis
            return prompt[:max_chars - 20] + "\n\n[Note: Response truncated]"

        return prompt

