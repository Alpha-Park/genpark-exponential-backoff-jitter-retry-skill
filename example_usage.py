"""Example usage for GenPark Exponential Backoff Jitter Retry."""
from client import ExponentialBackoffJitterRetry

def main():
    print("Calculating next backoff delay for attempt #4 (429 Rate Limit)...")
    delay = ExponentialBackoffJitterRetry.calculate_retry_delay(
        attempt=4,
        base_delay=1.0,
        max_delay=30.0,
        strategy="full_jitter"
    )
    print("Delay calculation:", delay)

    print("
Simulating 5-attempt retry timeline...")
    timeline = ExponentialBackoffJitterRetry.simulate_retry_schedule(
        max_attempts=5,
        base_delay=1.0,
        max_delay=30.0
    )
    for step in timeline["schedule"]:
        print(f" - Attempt {step['attempt']}: sleep {step['delay']}s (Cumulative: {step['cumulative_wait']}s)")

    print("
Evaluating retryability of 429 status:")
    check = ExponentialBackoffJitterRetry.should_retry(status_code=429)
    print("Should retry:", check["should_retry"], "| Reason:", check["reason"])

if __name__ == "__main__":
    main()
