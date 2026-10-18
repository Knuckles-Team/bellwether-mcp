"""Lazily-built, process-lifetime governed clients for the two keyed vendor APIs.

One instance is shared by every registered tool so the rate limiter actually
limits the whole process's traffic to a host, not just one tool's calls to
it. Built lazily so importing this module (as tests do) never opens a socket.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import httpx

from bellwether_mcp import config
from bellwether_mcp.http_clients import RateLimiter, build_async_client


@dataclass
class _Endpoint:
    config: config.SourceEndpoint
    extra_headers: dict[str, str] = field(default_factory=dict)
    _client: httpx.AsyncClient | None = field(default=None, init=False, repr=False)
    _limiter: RateLimiter | None = field(default=None, init=False, repr=False)

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = build_async_client(
                self.config, extra_headers=self.extra_headers
            )
        return self._client

    @property
    def limiter(self) -> RateLimiter:
        if self._limiter is None:
            self._limiter = RateLimiter(self.config.min_interval_seconds)
        return self._limiter

    async def paced_client(self) -> httpx.AsyncClient:
        """Wait out this host's minimum interval, then return its client."""
        await self.limiter.wait()
        return self.client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()


class Clients:
    """One rate-limited, governed client per vendor API this package calls.

    The FOMC calendar has no client here: it reads a packaged dataset, not a
    live API (see ``bellwether_mcp.api.fomc_calendar``).
    """

    def __init__(self) -> None:
        self.coinmarketcap = _Endpoint(config.COINMARKETCAP)
        self.fred = _Endpoint(config.FRED)

    def _all(self) -> tuple[_Endpoint, ...]:
        return (self.coinmarketcap, self.fred)

    async def aclose(self) -> None:
        """Close every client that was actually opened."""
        for endpoint in self._all():
            await endpoint.aclose()
