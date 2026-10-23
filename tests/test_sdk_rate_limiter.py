"""Vendor endpoints pace calls with the SDK request limiter."""

from __future__ import annotations

import pytest
from agent_connector_sdk.httpsupport import RateLimiter

from bellwether_mcp import http_clients
from bellwether_mcp.mcp.clients import Clients

pytestmark = [pytest.mark.spec("CONN-BELLWETHER-MCP-HTTP-R001")]


def test_endpoint_limiter_is_the_sdk_limiter() -> None:
    clients = Clients()
    for endpoint in clients._all():
        limiter = endpoint.limiter
        assert type(limiter) is RateLimiter
        assert limiter.min_interval_seconds == max(
            0.0, endpoint.config.min_interval_seconds
        )
        assert endpoint.limiter is limiter


def test_package_ships_no_rate_limiter() -> None:
    assert not hasattr(http_clients, "RateLimiter")
