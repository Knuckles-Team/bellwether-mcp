"""Governed HTTP clients and a shared per-host rate limiter.

Every outbound request in this package goes through
``agent_connector_sdk.http.client``: bounded timeouts, TLS verification,
governed retry/backoff, and a redacted-URL logger. This module adds only what
the SDK's client does not: a cooperative minimum-interval limiter so this
process honours each vendor's documented request budget even though the SDK's
governed transport has no notion of a *source-specific* pace.
"""

from __future__ import annotations

import asyncio
import time

import httpx
from agent_connector_sdk.http.client import create_async_http_client
from agent_connector_sdk.http.options import HttpClientOptions

from bellwether_mcp.config import USER_AGENT, SourceEndpoint

__all__ = ["RateLimiter", "build_async_client"]


class RateLimiter:
    """Cooperatively enforces a minimum interval between requests to one host."""

    def __init__(self, min_interval_seconds: float) -> None:
        self._min_interval = max(0.0, min_interval_seconds)
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def wait(self) -> None:
        """Sleep only as long as needed to respect the minimum interval."""
        async with self._lock:
            now = time.monotonic()
            delay = self._min_interval - (now - self._last_call)
            if delay > 0:
                await asyncio.sleep(delay)
            self._last_call = time.monotonic()


def build_async_client(
    endpoint: SourceEndpoint, *, extra_headers: dict[str, str] | None = None
) -> httpx.AsyncClient:
    """A governed async client for one vendor API's documented base URL."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    headers.update(extra_headers or {})
    options = HttpClientOptions(base_url=endpoint.base_url, headers=headers)
    return create_async_http_client(options)
