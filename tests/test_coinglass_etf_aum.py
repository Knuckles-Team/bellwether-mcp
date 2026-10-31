"""A daily fund flow must retain an independently captured matching AUM."""

import pytest
from fastmcp import Client, FastMCP

from bellwether_mcp.api import coinglass, coinglass_etf
from bellwether_mcp.mcp import tools_coinglass

FLOW = {
    "code": "0",
    "data": [
        {
            "timestamp": 1704931200000,
            "etf_flows": [
                {"etf_ticker": "IBIT", "flow_usd": 111700000},
                {"etf_ticker": "GBTC", "flow_usd": -95100000},
            ],
        }
    ],
}
AUM = {"code": "0", "data": [{"time": 1704931200000, "aum_usd": 500000000}]}


@pytest.mark.asyncio
async def test_served_join_uses_exact_ticker_date_and_captures(monkeypatch):
    requests = []

    async def fetch(url, **kwargs):
        requests.append((url, kwargs))
        return AUM if url.endswith("/aum") else FLOW

    monkeypatch.setattr(coinglass, "safe_get_json_async", fetch)
    monkeypatch.setattr(tools_coinglass, "resolve_coinglass_api_key", lambda: "secret")
    server = FastMCP("etf")
    tools_coinglass.register_coinglass_tools(server)
    async with Client(server) as client:
        result = await client.call_tool(
            "coinglass_macro_snapshot",
            {
                "dataset": "etf_fund_flows",
                "ticker": "IBIT",
                "license_tag": "operator-license",
                "mode": "delta",
            },
        )
    row = result.structured_content["items"][0]
    assert (
        row["fund_ticker"],
        row["flow_date"],
        row["net_flow_usd"],
        row["aum_usd"],
    ) == ("IBIT", "2024-01-11", 111700000, 500000000)
    assert row["flow_observed_at"] <= row["aum_observed_at"] == row["observed_at"]
    assert requests[1][1]["params"] == {"ticker": "IBIT"}
    assert all(request[1]["max_redirects"] == 0 for request in requests)
    assert all(
        request[1]["headers"] == {"CG-API-KEY": "secret"} for request in requests
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {"code": "0", "data": []},
        {"code": "0", "data": [{"time": 1705017600000, "aum_usd": 1}]},
        {"code": "0", "data": [{"time": 1704931200000, "aum_usd": -1}]},
        {"code": "0", "data": AUM["data"] * 2},
    ],
)
async def test_missing_conflicting_or_invalid_aum_refuses(monkeypatch, payload):
    async def fetch(url, **_kwargs):
        return payload if url.endswith("/aum") else FLOW

    monkeypatch.setattr(coinglass, "safe_get_json_async", fetch)
    with pytest.raises(ValueError):
        await coinglass_etf.read_etf_fund_flows(
            "secret", ticker="IBIT", license_tag="license"
        )


@pytest.mark.asyncio
async def test_declared_fund_source_runs_through_sdk_adapter(monkeypatch):
    from datetime import datetime

    from scion_sdk.adapters.mcp_tool import McpToolSourceAdapter
    from scion_sdk.finance.etf_flows import etf_fund_flows_from_source
    from scion_sdk.ingest.live_declaration import build_declaration
    from scion_sdk.manifest.declaration import contract_from_declaration
    from scion_sdk.ports.session import TransportEndpoint
    from scion_sdk.runner import syncing
    from scion_sdk.testing.sinks import InMemorySink
    from scion_sdk.transports.mcp import McpTransport

    from bellwether_mcp import connector_sources

    async def fetch(url, **_kwargs):
        return AUM if url.endswith("/aum") else FLOW

    monkeypatch.setattr(coinglass, "safe_get_json_async", fetch)
    monkeypatch.setattr(tools_coinglass, "resolve_coinglass_api_key", lambda: "secret")
    server = FastMCP("etf")
    tools_coinglass.register_coinglass_tools(server)
    async with McpTransport().session(TransportEndpoint(in_process=server)) as session:
        declarations = [
            entry
            for entry in connector_sources.SOURCES
            if entry["connector_sources"][0]["source_id"] == "coinglass_etf_fund_flows"
        ]
        declaration = build_declaration(
            "bellwether-mcp",
            await session.list_tools(),
            declared={"SOURCES": declarations},
        )
        contract = contract_from_declaration(declaration)
        source = contract.sync[0]
        source = source.model_copy(
            update={
                "raw": {
                    **source.raw,
                    "params": {
                        **source.raw["params"],
                        "ticker": "IBIT",
                        "license_tag": "licensed",
                    },
                }
            }
        )
        adapter = McpToolSourceAdapter.from_sync_spec(
            source,
            connector="bellwether-mcp",
            mapping_reference="connector:bellwether-mcp#mappings/MacroPanel",
        )
        sink = InMemorySink()
        target = syncing.SyncTarget("bellwether-mcp", sink, max_pages=1)
        assert (await syncing.sync_stream(session, adapter, target)).records == 1
        assert (await syncing.sync_stream(session, adapter, target)).records == 1
        batches = list(sink.batches.values())
        assert len(batches) == 2
        row = batches[0].records[0].payload
        fund = etf_fund_flows_from_source(
            {"flows": [row]},
            tenant_id="tenant:test",
            source_id="coinglass_etf_fund_flows",
            provider="coinglass",
            license_tag="licensed",
            observed_at_utc=datetime.fromisoformat(row["observed_at"]),
        )[0]
        assert (fund.fund_ticker, fund.net_flow_usd, fund.aum_usd) == (
            "IBIT",
            111700000,
            500000000,
        )
