"""Exponential Backoff Jitter Retry.
100% Python Standard Library.
"""
import random
from typing import Dict, Any, List, Optional

class ExponentialBackoffJitterRetry:
    """Enterprise retry engine with full jitter, equal jitter, and decorrelated jitter."""

    @staticmethod
    def calculate_retry_delay(
        attempt: int,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: str = "full_jitter",
        prev_delay: float = 1.0
    ) -> Dict[str, Any]:
        exp_backoff = min(max_delay, base_delay * (2 ** max(0, attempt - 1)))

        if strategy == "full_jitter":
            sleep_duration = random.uniform(0, exp_backoff)
        elif strategy == "equal_jitter":
            half = exp_backoff / 2.0
            sleep_duration = half + random.uniform(0, half)
        elif strategy == "decorrelated_jitter":
            sleep_duration = min(max_delay, random.uniform(base_delay, prev_delay * 3.0))
        else:
            sleep_duration = exp_backoff

        return {
            "attempt": attempt,
            "strategy": strategy,
            "exp_backoff_ceiling": round(exp_backoff, 4),
            "sleep_duration": round(sleep_duration, 4)
        }

    @staticmethod
    def simulate_retry_schedule(
        max_attempts: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        strategy: str = "full_jitter"
    ) -> Dict[str, Any]:
        schedule = []
        total_time = 0.0
        prev = base_delay

        for att in range(1, max_attempts + 1):
            res = ExponentialBackoffJitterRetry.calculate_retry_delay(att, base_delay, max_delay, strategy, prev)
            d = res["sleep_duration"]
            prev = d
            total_time += d
            schedule.append({
                "attempt": att,
                "delay": d,
                "cumulative_wait": round(total_time, 4)
            })

        return {
            "strategy": strategy,
            "total_attempts": max_attempts,
            "total_simulated_wait_seconds": round(total_time, 4),
            "schedule": schedule
        }

    @staticmethod
    def should_retry(status_code: Optional[int] = None, error_message: str = "", retryable_codes: Optional[List[int]] = None) -> Dict[str, Any]:
        default_retryable = [429, 500, 502, 503, 504]
        allowed_codes = retryable_codes if retryable_codes is not None else default_retryable

        is_retryable = False
        reason = "Non-retryable response"

        if status_code in allowed_codes:
            is_retryable = True
            reason = f"HTTP status {status_code} is transient"
        elif any(term in error_message.lower() for term in ["rate limit", "timeout", "connection reset", "overloaded", "throttled"]):
            is_retryable = True
            reason = f"Transient error signature in message: {error_message[:60]}"

        return {
            "should_retry": is_retryable,
            "status_code": status_code,
            "reason": reason
        }
