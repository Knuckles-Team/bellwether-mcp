"""CoinMarketCap client: discovery/caps only, 0-based offset translated to CMC's 1-based `start`."""

from __future__ import annotations

import httpx
import pytest

from bellwether_mcp.api import coinmarketcap
from tests.conftest import json_response, mock_client


@pytest.mark.asyncio
async def test_list_listings_translates_zero_based_offset_to_cmc_start(fixture):
    payload = fixture("cmc_listings.json")
    seen_params: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_params.update(dict(request.url.params))
        return json_response(payload)

    async with mock_client("https://pro-api.coinmarketcap.com", handler) as client:
        result = await coinmarketcap.list_listings(
            client, api_key="k", start=0, limit=100
        )

    assert seen_params["start"] == "1"  # CMC is 1-indexed; our own contract is 0-based
    assert len(result["items"]) == 2
    assert result["items"][0]["cmc_id"] == "1"
    assert result["items"][0]["symbol"] == "BTC"
    assert result["items"][0]["price_usd"] == 65123.45
    assert result["total"] is None  # CMC reports no reliable total


@pytest.mark.asyncio
async def test_list_listings_second_page_offset(fixture):
    payload = fixture("cmc_listings.json")
    seen_params: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_params.update(dict(request.url.params))
        return json_response(payload)

    async with mock_client("https://pro-api.coinmarketcap.com", handler) as client:
        await coinmarketcap.list_listings(client, api_key="k", start=100, limit=100)

    assert seen_params["start"] == "101"


@pytest.mark.asyncio
async def test_get_quotes_flattens_symbol_keyed_data(fixture):
    payload = fixture("cmc_quotes.json")

    async with mock_client(
        "https://pro-api.coinmarketcap.com", lambda r: json_response(payload)
    ) as client:
        result = await coinmarketcap.get_quotes(client, api_key="k", symbols="BTC,ETH")

    symbols = {item["symbol"] for item in result["items"]}
    assert symbols == {"BTC", "ETH"}
    assert result["total"] == 2


@pytest.mark.asyncio
async def test_get_global_metrics_returns_one_snapshot_record(fixture):
    payload = fixture("cmc_global_metrics.json")

    async with mock_client(
        "https://pro-api.coinmarketcap.com", lambda r: json_response(payload)
    ) as client:
        result = await coinmarketcap.get_global_metrics(client, api_key="k")

    assert result["total"] == 1
    snapshot = result["items"][0]
    assert snapshot["btc_dominance"] == 52.31
    assert snapshot["total_market_cap_usd"] == 2510000000000


@pytest.mark.spec("CONN-BELLWETHER-MCP-HTTP-R002")
@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["listings", "quotes", "global"])
async def test_api_key_is_not_forwarded_on_redirect(operation):
    seen = []
    key = "synthetic"

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.host)
        return httpx.Response(
            307, headers={"Location": "https://other.example.test/collect"}
        )

    async with httpx.AsyncClient(
        base_url="https://pro-api.coinmarketcap.com",
        transport=httpx.MockTransport(handler),
        follow_redirects=True,
    ) as client:
        with pytest.raises(httpx.HTTPStatusError):
            if operation == "listings":
                await coinmarketcap.list_listings(client, api_key=key, start=0, limit=1)
            elif operation == "quotes":
                await coinmarketcap.get_quotes(client, api_key=key, symbols="BTC")
            else:
                await coinmarketcap.get_global_metrics(client, api_key=key)
    assert seen == ["pro-api.coinmarketcap.com"]


@pytest.mark.spec("CONN-BELLWETHER-MCP-CMC-PAGING-R001")
@pytest.mark.asyncio
async def test_served_default_listings_start_at_first_provider_record(
    fixture, monkeypatch
):
    from types import SimpleNamespace

    from fastmcp import Client, FastMCP

    from bellwether_mcp.mcp import tools_crypto_reference

    seen = []
    payload = fixture("cmc_listings.json")

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(dict(request.url.params))
        return json_response(payload)

    async with mock_client("https://pro-api.coinmarketcap.com", handler) as http:

        class Endpoint:
            async def paced_client(self):
                return http

        monkeypatch.setattr(tools_crypto_reference, "resolve_cmc_api_key", lambda: "k")
        server = FastMCP("cmc-test")
        tools_crypto_reference.register_crypto_reference_tools(
            server, SimpleNamespace(coinmarketcap=Endpoint())
        )
        async with Client(server) as client:
            first = await client.call_tool("cmc_listings", {})
            later = await client.call_tool("cmc_listings", {"start": 100})
        assert not first.is_error and not later.is_error
        assert seen == [
            {"start": "1", "limit": "100", "convert": "USD"},
            {"start": "101", "limit": "100", "convert": "USD"},
        ]


@pytest.mark.spec("CONN-BELLWETHER-MCP-CMC-PAGING-R002")
@pytest.mark.asyncio
async def test_sdk_source_adapter_pages_served_cmc(fixture, monkeypatch):
    from types import SimpleNamespace

    from agent_connector_sdk.adapters.mcp_tool import McpToolSourceAdapter
    from agent_connector_sdk.ingest.live_declaration import build_declaration
    from agent_connector_sdk.manifest.declaration import contract_from_declaration
    from agent_connector_sdk.ports.session import TransportEndpoint
    from agent_connector_sdk.transports.mcp import McpTransport
    from fastmcp import FastMCP

    from bellwether_mcp import connector_sources
    from bellwether_mcp.mcp import tools_crypto_reference

    base = fixture("cmc_listings.json")["data"][0]
    seen = []

    def handler(request):
        start = int(request.url.params["start"])
        seen.append(start)
        count = min(100, max(0, 102 - start))
        return json_response(
            {"data": [{**base, "id": n} for n in range(start, start + count)]}
        )

    async with mock_client("https://pro-api.coinmarketcap.com", handler) as http:

        class Endpoint:
            async def paced_client(self):
                return http

        monkeypatch.setattr(tools_crypto_reference, "resolve_cmc_api_key", lambda: "k")
        server = FastMCP("cmc-test")
        tools_crypto_reference.register_crypto_reference_tools(
            server, SimpleNamespace(coinmarketcap=Endpoint())
        )
        async with McpTransport().session(
            TransportEndpoint(in_process=server)
        ) as session:
            tools = await session.list_tools()
            sources = [
                entry
                for entry in connector_sources.SOURCES
                if entry["connector_sources"][0]["source_id"] == "crypto_listings_cmc"
            ]
            declaration = build_declaration(
                "bellwether-mcp", tools, declared={"SOURCES": sources}
            )
            contract = contract_from_declaration(declaration)
            assert contract is not None
            adapter = McpToolSourceAdapter.from_sync_spec(
                contract.sync[0],
                connector=contract.connector,
                mapping_reference="connector:bellwether-mcp#mappings/Instrument",
            )
            await adapter.discover(session)
            first = await adapter.extract(session, None)
            second = await adapter.extract(session, first.checkpoint)
            assert [record.record_id for record in first.records] == [
                str(n) for n in range(1, 101)
            ]
            assert [record.record_id for record in second.records] == ["101"]
            assert seen == [1, 101]
