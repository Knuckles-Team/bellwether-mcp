"""Governed HTTP clients for this package's vendor APIs.

Every outbound request in this package goes through
``scion_sdk.http.client``: bounded timeouts, TLS verification,
governed retry/backoff, and a redacted-URL logger. This module adds only the
connector's user agent and endpoint defaults. Per-host pacing uses the SDK's
``scion_sdk.httpsupport.RateLimiter``.
"""

from __future__ import annotations

import httpx
from scion_sdk.http.client import create_async_http_client
from scion_sdk.http.options import HttpClientOptions

from bellwether_mcp.config import USER_AGENT, SourceEndpoint

__all__ = ["build_async_client"]


def build_async_client(
    endpoint: SourceEndpoint, *, extra_headers: dict[str, str] | None = None
) -> httpx.AsyncClient:
    """A governed async client for one vendor API's documented base URL."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    headers.update(extra_headers or {})
    options = HttpClientOptions(base_url=endpoint.base_url, headers=headers)
    return create_async_http_client(options)
