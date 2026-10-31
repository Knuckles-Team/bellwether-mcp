"""CoinGlass macro snapshots retain provider values and observation times."""

import httpx
import pytest
from fastmcp import Client, FastMCP

from bellwether_mcp.api import coinglass
from bellwether_mcp.mcp import tools_coinglass

ETF = {
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
SENTIMENT = {
    "code": "0",
    "data": [{"data_list": [42, 55], "time_list": [1704931200, 1705017600]}],
}
POSITIONS = {
    "code": "0",
    "data": [
        {
            "user": "0x" + "ab" * 20,
            "symbol": "ETH",
            "position_size": -3.5,
            "entry_price": 2249.7,
            "mark_price": 1645.8,
            "update_time": 1704931200123,
        }
    ],
}
DATA = {"etf": ETF, "sentiment": SENTIMENT, "onchain": POSITIONS}


def stub(monkeypatch):
    async def fetch(url, **kwargs):
        assert kwargs["headers"] == {"CG-API-KEY": "secret"}
        assert kwargs["max_redirects"] == 0
        if url.endswith("flow-history"):
            return ETF
        if url.endswith("fear-greed-history"):
            return SENTIMENT
        return POSITIONS

    monkeypatch.setattr(coinglass, "safe_get_json_async", fetch)
    monkeypatch.setattr(tools_coinglass, "resolve_coinglass_api_key", lambda: "secret")


@pytest.mark.asyncio
@pytest.mark.parametrize("kind,count", [("etf", 2), ("sentiment", 2), ("onchain", 1)])
async def test_served_snapshots_preserve_actual_provider_facts(
    kind, count, monkeypatch
):
    stub(monkeypatch)
    server = FastMCP("macro")
    tools_coinglass.register_coinglass_tools(server)
    async with Client(server) as client:
        result = await client.call_tool(
            "coinglass_macro_snapshot",
            {"dataset": kind, "license_tag": "licensed", "mode": "delta"},
        )
    data = result.structured_content
    assert len(data["items"]) == count
    assert all(
        r["provider"] == "coinglass"
        and r["observed_at"]
        and r["event_time"]
        and r["license_tag"] == "licensed"
        for r in data["items"]
    )
    assert data["checkpoint"]["generation"]
    if kind == "etf":
        assert {r["net_flow_usd"] for r in data["items"]} == {111700000, -95100000}
    if kind == "onchain":
        assert data["items"][0]["position_size"] == -3.5
        assert data["items"][0]["event_time"].endswith(".123Z")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind,payload",
    [
        (
            "etf",
            {
                "code": "0",
                "data": [
                    {
                        "timestamp": 1704931200000,
                        "etf_flows": [{"etf_ticker": "IBIT", "flow_usd": float("nan")}],
                    }
                ],
            },
        ),
        ("sentiment", {"code": "0", "data": [{"data_list": [10], "time_list": []}]}),
        (
            "onchain",
            {"code": "0", "data": [{**POSITIONS["data"][0], "user": "private-value"}]},
        ),
        ("etf", {"code": "1", "data": []}),
    ],
)
async def test_malformed_provider_data_refuses_without_private_values(
    kind, payload, monkeypatch
):
    async def fetch(*_args, **_kwargs):
        return payload

    monkeypatch.setattr(coinglass, "safe_get_json_async", fetch)
    monkeypatch.setattr(tools_coinglass, "resolve_coinglass_api_key", lambda: "secret")
    server = FastMCP("macro")
    tools_coinglass.register_coinglass_tools(server)
    async with Client(server) as client:
        result = await client.call_tool(
            "coinglass_macro_snapshot",
            {"dataset": kind, "license_tag": "licensed", "mode": "delta"},
            raise_on_error=False,
        )
    assert result.is_error
    assert "private-value" not in str(result.content) and "secret" not in str(
        result.content
    )


@pytest.mark.asyncio
async def test_guarded_http_uses_header_and_fixed_destination(monkeypatch):
    from scion_sdk.source_connectors.http_safety import safe_get_json_async

    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json=ETF)

    transport = httpx.MockTransport(respond)
    monkeypatch.setattr(
        coinglass,
        "safe_get_json_async",
        lambda url, **kw: safe_get_json_async(url, transport=transport, **kw),
    )
    records = await coinglass.read_snapshot(
        "secret", dataset="etf", license_tag="licensed"
    )
    assert len(records) == 2
    assert requests[0].headers["CG-API-KEY"] == "secret"
    assert "secret" not in str(requests[0].url)


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["etf", "sentiment", "onchain"])
async def test_declared_source_replays_into_sdk_sink(kind, monkeypatch):
    import scion_sdk.adapters.mcp_tool as adapter_module
    import scion_sdk.ingest.live_declaration as declaration_module
    import scion_sdk.manifest.declaration as contract_module
    import scion_sdk.ports.session as session_module
    import scion_sdk.runner.syncing as sync_module
    import scion_sdk.testing.sinks as sink_module
    import scion_sdk.transports.mcp as transport_module

    from bellwether_mcp import connector_sources

    stub(monkeypatch)
    server = FastMCP("macro")
    tools_coinglass.register_coinglass_tools(server)
    async with transport_module.McpTransport().session(
        session_module.TransportEndpoint(in_process=server)
    ) as session:
        declaration = declaration_module.build_declaration(
            "bellwether-mcp",
            await session.list_tools(),
            declared={
                "SOURCES": [
                    entry
                    for entry in connector_sources.SOURCES
                    if entry["connector_sources"][0]["source_id"] == f"coinglass_{kind}"
                ]
            },
        )
        contract = contract_module.contract_from_declaration(declaration)
        source = next(s for s in contract.sync if s.preset == f"coinglass_{kind}")
        source = source.model_copy(
            update={
                "raw": {
                    **source.raw,
                    "params": {**source.raw["params"], "license_tag": "licensed"},
                }
            }
        )
        adapter = adapter_module.McpToolSourceAdapter.from_sync_spec(
            source,
            connector="bellwether-mcp",
            mapping_reference="connector:bellwether-mcp#mappings/MacroPanel",
        )
        sink = sink_module.InMemorySink()
        target = sync_module.SyncTarget("bellwether-mcp", sink, max_pages=1)
        first, again = (
            await sync_module.sync_stream(session, adapter, target),
            await sync_module.sync_stream(session, adapter, target),
        )
        assert first.records == again.records > 0
        assert len(sink.batches) == 2
        assert all(batch.mode.value == "delta" for batch in sink.batches.values())
