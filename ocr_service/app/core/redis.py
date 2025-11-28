from typing import AsyncGenerator

from upstash_redis import Redis

# Upstash Redis configuration
UPSTASH_REDIS_URL = "https://real-beetle-19713.upstash.io"
UPSTASH_REDIS_TOKEN = "AU0BAAIncDJkZDg3MzdmMGI2YmM0MmQ3OWRhNWZiMzNmMWE5ODQzZnAyMTk3MTM"

# Initialize Redis client once (singleton)
redis_client = Redis(url=UPSTASH_REDIS_URL, token=UPSTASH_REDIS_TOKEN)


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """
    FastAPI dependency for Upstash Redis.
    Returns a Redis client instance for async operations.
    """
    yield redis_client
