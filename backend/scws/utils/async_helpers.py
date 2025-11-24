"""
Async utility functions
"""

import asyncio
from typing import Callable, TypeVar, Awaitable

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[[], Awaitable[T]],
    max_attempts: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
) -> T:
    """
    Retry an async function with exponential backoff

    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Backoff multiplication factor

    Returns:
        Result from successful function call

    Raises:
        Last exception if all attempts fail
    """
    last_exception: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e

            if attempt == max_attempts:
                break

            delay = min(initial_delay * (backoff_factor ** (attempt - 1)), max_delay)
            await asyncio.sleep(delay)

    if last_exception:
        raise last_exception
    raise RuntimeError("retry_with_backoff failed without exception")


async def with_timeout(coro: Awaitable[T], timeout: float) -> T:
    """
    Execute a coroutine with a timeout

    Args:
        coro: Coroutine to execute
        timeout: Timeout in seconds

    Returns:
        Result from coroutine

    Raises:
        asyncio.TimeoutError: If timeout is exceeded
    """
    return await asyncio.wait_for(coro, timeout=timeout)
