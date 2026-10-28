"""Shared test fixtures. No live network: every HTTP call is mocked."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import httpx
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    """Read one recorded or synthetic fixture JSON file by name."""
    return json.loads((FIXTURES / name).read_text())


def mock_client(
    base_url: str, handler: Callable[[httpx.Request], httpx.Response]
) -> httpx.AsyncClient:
    """An ``httpx.AsyncClient`` whose transport is a synchronous fixture handler."""
    return httpx.AsyncClient(base_url=base_url, transport=httpx.MockTransport(handler))


def json_response(payload: dict) -> httpx.Response:
    """A 200 JSON response carrying ``payload``."""
    return httpx.Response(200, json=payload)


@pytest.fixture
def fixture() -> Callable[[str], dict]:
    return load_fixture


async def sdk_source_pages(server, source_id, mapping):
    """Extract two pages via the declared source and SDK MCP transport."""
    from agent_connector_sdk.adapters.mcp_tool import McpToolSourceAdapter
    from agent_connector_sdk.ingest.live_declaration import build_declaration
    from agent_connector_sdk.manifest.declaration import contract_from_declaration
    from agent_connector_sdk.ports.session import TransportEndpoint
    from agent_connector_sdk.transports.mcp import McpTransport

    from bellwether_mcp import connector_sources

    async with McpTransport().session(TransportEndpoint(in_process=server)) as session:
        tools = await session.list_tools()
        sources = [
            entry
            for entry in connector_sources.SOURCES
            if entry["connector_sources"][0]["source_id"] == source_id
        ]
        declaration = build_declaration(
            "bellwether-mcp", tools, declared={"SOURCES": sources}
        )
        contract = contract_from_declaration(declaration)
        assert contract is not None
        adapter = McpToolSourceAdapter.from_sync_spec(
            contract.sync[0],
            connector=contract.connector,
            mapping_reference=f"connector:bellwether-mcp#mappings/{mapping}",
        )
        await adapter.discover(session)
        first = await adapter.extract(session, None)
        second = await adapter.extract(session, first.checkpoint)
        return first, second
