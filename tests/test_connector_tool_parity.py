"""Canonical SDK parity for the Bellwether connector's legacy tool surface."""

from __future__ import annotations

import asyncio
import importlib

import pytest
from agent_connector_sdk.connector import build_server

pytestmark = pytest.mark.spec("CONN-BELLWETHER-MCP-CONNECTOR-CONTENT-R001")

PACKAGE = "bellwether_mcp"
EXPECTED_TOOLS = {
    "cmc_global_metrics",
    "cmc_listings",
    "cmc_quotes",
    "fred_macro_series_aliases",
    "fred_series_observations",
    "fred_series_observations_asof",
    "fred_series_vintage_dates",
    "fomc_calendar_list",
}


def _tool_snapshot(server):
    async def collect():
        from fastmcp import Client

        async with Client(server) as client:
            return {
                tool.name: tool.model_dump(mode="json")
                for tool in await client.list_tools()
            }

    return asyncio.run(collect())


@pytest.mark.parametrize("transport", ["stdio"])
def test_canonical_server_preserves_legacy_tools_and_schemas(monkeypatch, transport):
    """The SDK declaration exposes all eight legacy tools with identical schemas."""
    monkeypatch.setenv("MCP_FLEET_REGISTRATION", "false")
    monkeypatch.setattr(
        "sys.argv", ["connector", "--transport", transport, "--auth-type", "none"]
    )
    legacy = importlib.import_module("bellwether_mcp.mcp.server").build_server()[0]
    _, canonical = build_server(PACKAGE, command_args=[])

    legacy_tools = _tool_snapshot(legacy)
    canonical_tools = _tool_snapshot(canonical)

    assert set(legacy_tools) == EXPECTED_TOOLS
    assert set(canonical_tools) == EXPECTED_TOOLS
    assert len(legacy_tools) == len(canonical_tools) == 8
    for name in EXPECTED_TOOLS:
        assert canonical_tools[name] == legacy_tools[name]


@pytest.fixture(autouse=True)
def _no_outbound_network(monkeypatch):
    import socket

    def refuse(*_args, **_kwargs):
        raise AssertionError(
            "connector construction must not contact an external system"
        )

    monkeypatch.setattr(socket.socket, "connect", refuse)
