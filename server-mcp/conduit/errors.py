"""Structured error taxonomy and retry helper for Conduit MCP server."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

# ── Error codes ───────────────────────────────────────────────────────────────

INVALID_INPUT = "invalid_input"
NOT_FOUND = "not_found"
RATE_LIMITED = "rate_limited"
PROVIDER_DOWN = "provider_down"
INTERNAL_ERROR = "internal_error"


def err(code: str, message: str) -> dict:
    """Return a structured error payload ``{error, message}``."""
    return {"error": code, "message": message}


# ── Retry helper ──────────────────────────────────────────────────────────────

T = TypeVar("T")

_RETRYABLE_CODES = {RATE_LIMITED, PROVIDER_DOWN}


async def with_retry(
    fn: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 3,
    base_delay: float = 0.5,
    timeout: float = 5.0,
) -> T:
    """Call an async function with exponential back-off and a per-call timeout.

    Retries only when the result is a dict whose ``error`` key is one of
    ``rate_limited`` or ``provider_down``.  All other errors and exceptions
    are re-raised immediately.

    Args:
        fn:           Zero-argument async callable to invoke.
        max_attempts: Total number of attempts before giving up.
        base_delay:   Initial back-off in seconds; doubles each retry.
        timeout:      Per-attempt timeout in seconds.

    Returns:
        The first non-retryable result from *fn*.

    Raises:
        TimeoutError:  If every attempt times out.
        Exception:     Any non-retryable exception from *fn*.
    """
    delay = base_delay
    for attempt in range(1, max_attempts + 1):
        try:
            result = await asyncio.wait_for(fn(), timeout=timeout)
        except TimeoutError:
            logger.warning("Attempt %d/%d timed out", attempt, max_attempts)
            if attempt == max_attempts:
                raise
            await asyncio.sleep(delay)
            delay *= 2
            continue

        if isinstance(result, dict) and result.get("error") in _RETRYABLE_CODES:
            logger.warning(
                "Attempt %d/%d got retryable error %r: %s",
                attempt,
                max_attempts,
                result["error"],
                result.get("message", ""),
            )
            if attempt == max_attempts:
                return result
            await asyncio.sleep(delay)
            delay *= 2
            continue

        return result

    # unreachable, but makes type-checkers happy
    raise RuntimeError("with_retry exhausted without returning")
