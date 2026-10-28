"""The served finance sources commit delta pages through the SDK sink."""

import pytest
from agent_connector_sdk.adapters.mcp_tool import McpToolSourceAdapter
from agent_connector_sdk.ingest.live_declaration import build_declaration
from agent_connector_sdk.manifest.declaration import contract_from_declaration
from agent_connector_sdk.ports.session import TransportEndpoint
from agent_connector_sdk.runner.syncing import SyncTarget, sync_stream
from agent_connector_sdk.testing.sinks import InMemorySink
from agent_connector_sdk.transports.mcp import McpTransport

from bellwether_mcp import connector_sources
from bellwether_mcp.mcp import tools_crypto_reference, tools_macro_series
from bellwether_mcp.mcp.server import build_server
from tests.conftest import json_response, mock_client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "source_id,mapping,expected_field",
    [
        ("crypto_listings_cmc", "Instrument", "symbol"),
        ("crypto_global_metrics_cmc", "MacroEvent", "id"),
        (
            "macro_series_treasury_general_account",
            "EconomicIndicator",
            "realtime_start",
        ),
        ("macro_series_fed_balance_sheet", "EconomicIndicator", "observed_at"),
        ("macro_series_reverse_repo_overnight", "EconomicIndicator", "observed_at"),
        ("fomc_calendar", "MacroEvent", "announcement_time_utc"),
    ],
)
async def test_served_finance_sources_commit_and_replay_as_deltas(
    fixture, monkeypatch, source_id, mapping, expected_field
):
    monkeypatch.setenv("MCP_FLEET_REGISTRATION", "false")
    monkeypatch.setattr(
        tools_crypto_reference, "resolve_cmc_api_key", lambda: "test-key"
    )
    monkeypatch.setattr(tools_macro_series, "resolve_fred_api_key", lambda: "test-key")
    async with (
        mock_client(
            "https://pro-api.coinmarketcap.com",
            lambda request: json_response(
                fixture(
                    "cmc_global_metrics.json"
                    if "global-metrics" in request.url.path
                    else "cmc_listings.json"
                )
            ),
        ) as cmc,
        mock_client(
            "https://api.stlouisfed.org/fred",
            lambda _: json_response(fixture("fred_observations.json")),
        ) as fred,
    ):
        components = build_server(["--transport", "stdio", "--auth-type", "none"])
        components.clients.coinmarketcap._client = cmc
        components.clients.fred._client = fred
        async with McpTransport().session(
            TransportEndpoint(in_process=components.mcp)
        ) as session:
            declaration = build_declaration(
                "bellwether-mcp",
                await session.list_tools(),
                declared={
                    "SOURCES": connector_sources.SOURCES,
                    "SCHEMA_MAPPINGS": connector_sources.SCHEMA_MAPPINGS,
                },
            )
            contract = contract_from_declaration(declaration)
            assert contract is not None
            source = next(s for s in contract.sync if s.preset == source_id)
            adapter = McpToolSourceAdapter.from_sync_spec(
                source,
                connector="bellwether-mcp",
                mapping_reference=f"connector:bellwether-mcp#mappings/{mapping}",
            )
            sink = InMemorySink()
            target = SyncTarget("bellwether-mcp", sink, max_pages=3)
            first, repeated = (
                await sync_stream(session, adapter, target),
                await sync_stream(session, adapter, target),
            )
            assert first.records and first.records == repeated.records
            assert len(sink.batches) == 2
            assert all(batch.mode.value == "delta" for batch in sink.batches.values())
            records = next(iter(sink.batches.values())).records
            assert all(None not in record.payload.values() for record in records)
            assert all(record.payload[expected_field] for record in records)
