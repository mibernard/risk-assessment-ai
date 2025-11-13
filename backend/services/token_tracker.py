"""
Token Usage Tracker

Monitors watsonx.ai API usage to stay within budget.
Budget: $250 USD for the challenge.
"""

from datetime import datetime
from typing import Dict, Any
import json
from pathlib import Path


class TokenTracker:
    """Tracks token usage and costs for IBM watsonx.ai API calls"""

    # Pricing (approximate, verify with IBM documentation)
    # Granite-13b-instruct-v2 pricing: ~$0.0001 per 1K tokens
    COST_PER_1K_TOKENS = 0.0001

    def __init__(self, budget_usd: float = 250.0, storage_path: str = "./token_usage.json"):
        """
        Initialize token tracker

        Args:
            budget_usd: Total budget in USD
            storage_path: Path to store usage data
        """
        self.budget_usd = budget_usd
        self.storage_path = Path(storage_path)
        self.usage_data = self._load_usage_data()

    def _load_usage_data(self) -> Dict[str, Any]:
        """Load existing usage data from disk"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Initialize new usage data
        return {
            "total_tokens": 0,
            "total_requests": 0,
            "total_cost_usd": 0.0,
            "requests": [],
            "started_at": datetime.now().isoformat(),
        }

    def _save_usage_data(self):
        """Save usage data to disk"""
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.usage_data, f, indent=2)
        except IOError as e:
            print(f"Warning: Failed to save token usage data: {e}")

    def track_request(
        self,
        tokens_used: int,
        model: str,
        endpoint: str,
        metadata: Dict[str, Any] = None,
    ):
        """
        Record a new API request

        Args:
            tokens_used: Number of tokens consumed
            model: Model name (e.g., "granite-3-2-8b-instruct")
            endpoint: API endpoint called (e.g., "/explain", "/report")
            metadata: Additional metadata (case_id, etc.)
        """
        cost = self._calculate_cost(tokens_used)

        # Update totals
        self.usage_data["total_tokens"] += tokens_used
        self.usage_data["total_requests"] += 1
        self.usage_data["total_cost_usd"] += cost

        # Record individual request
        request_record = {
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens_used,
            "cost_usd": cost,
            "model": model,
            "endpoint": endpoint,
            "metadata": metadata or {},
        }
        self.usage_data["requests"].append(request_record)

        # Save to disk
        self._save_usage_data()

    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost in USD for given tokens"""
        return (tokens / 1000) * self.COST_PER_1K_TOKENS

    def get_usage_summary(self) -> Dict[str, Any]:
        """
        Get current usage summary

        Returns:
            Dictionary with usage stats
        """
        total_cost = self.usage_data["total_cost_usd"]
        remaining = self.budget_usd - total_cost
        percentage_used = (total_cost / self.budget_usd) * 100 if self.budget_usd > 0 else 0

        return {
            "total_budget_usd": self.budget_usd,
            "spent_usd": round(total_cost, 4),
            "remaining_usd": round(remaining, 4),
            "tokens_used": self.usage_data["total_tokens"],
            "requests_count": self.usage_data["total_requests"],
            "percentage_used": round(percentage_used, 2),
            "started_at": self.usage_data.get("started_at"),
        }

    def is_within_budget(self, estimated_tokens: int = 0) -> bool:
        """
        Check if we're within budget

        Args:
            estimated_tokens: Tokens we plan to use (for pre-flight check)

        Returns:
            True if within budget, False otherwise
        """
        estimated_cost = self._calculate_cost(estimated_tokens)
        total_projected = self.usage_data["total_cost_usd"] + estimated_cost
        return total_projected < self.budget_usd

    def get_remaining_budget(self) -> float:
        """Get remaining budget in USD"""
        return self.budget_usd - self.usage_data["total_cost_usd"]

    def get_remaining_tokens_estimate(self) -> int:
        """Estimate how many tokens we can still use"""
        remaining_usd = self.get_remaining_budget()
        return int((remaining_usd / self.COST_PER_1K_TOKENS) * 1000)

    def check_budget_warning(self) -> tuple[bool, str]:
        """
        Check if budget warning is needed

        Returns:
            (warning_needed, message) tuple
        """
        summary = self.get_usage_summary()
        percentage = summary["percentage_used"]

        if percentage >= 90:
            return (
                True,
                f"⚠️ CRITICAL: {percentage:.1f}% of token budget used! Remaining: ${summary['remaining_usd']:.2f}",
            )
        elif percentage >= 75:
            return (
                True,
                f"⚠️ WARNING: {percentage:.1f}% of token budget used. Remaining: ${summary['remaining_usd']:.2f}",
            )
        elif percentage >= 50:
            return (
                True,
                f"ℹ️ INFO: {percentage:.1f}% of token budget used. Remaining: ${summary['remaining_usd']:.2f}",
            )

        return (False, "")

    def reset_usage(self):
        """Reset usage data (use with caution!)"""
        self.usage_data = {
            "total_tokens": 0,
            "total_requests": 0,
            "total_cost_usd": 0.0,
            "requests": [],
            "started_at": datetime.now().isoformat(),
        }
        self._save_usage_data()

