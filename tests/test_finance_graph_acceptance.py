"""Replay served finance sources through the SDK into a real graph.

Provider responses are synthetic. These tests do not establish live entitlements.
"""

import asyncio
import hashlib
import json
import os
import subprocess  # nosec B404 - fixed test server argv
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest

pytest.importorskip("epistemic_graph")
pytest.importorskip("agent_connector_sdk.finance.market_source")

from agent_connector_sdk.adapters.mcp_tool import McpToolSourceAdapter
from agent_connector_sdk.artifacts.pack import build_content_pack
from agent_connector_sdk.artifacts.resources import ResourceArtifactKind
from agent_connector_sdk.artifacts.tools import ToolArtifactKind
from agent_connector_sdk.finance.etf_flows import etf_fund_flows_from_source
from agent_connector_sdk.finance.market_source import (
    MarketSourceAdapter,
    MarketSourceKind,
)
from agent_connector_sdk.ingest.live_declaration import build_declaration
from agent_connector_sdk.manifest.declaration import contract_from_declaration
from agent_connector_sdk.ports.session import TransportEndpoint
from agent_connector_sdk.runner.syncing import SyncTarget, sync_stream
from agent_connector_sdk.sinks.epistemic_graph import EpistemicGraphSink
from agent_connector_sdk.transports.mcp import McpTransport
from epistemic_graph import EpistemicGraphClient
from epistemic_graph.client import SyncEpistemicGraphClient
from epistemic_graph.connector_pack import ConnectorPackClient
from epistemic_graph.generated.connector_pack import (
    AgentLibraryMutationContext,
    McpCatalogSnapshotBinding,
    PackProducer,
)
from epistemic_graph.server_binary import (
    ServerBinaryNotFoundError,
    resolve_server_binary,
)

from bellwether_mcp import connector_sources
from bellwether_mcp.api import coinglass
from bellwether_mcp.mcp import tools_coinglass, tools_macro_series
from bellwether_mcp.mcp.server import build_server

CONNECTOR = "bellwether-mcp"
TENANT = "tenant:bellwether-test"
PRINCIPAL = "service:connector"
GRAPH = "bellwether-test"
HMAC = "bellwether-test-auth-0123456789abcdef"  # nosec B105
SIGNER = "bellwether-test-signer-0123456789abcdef"  # nosec B105
DATA_KEY = "bellwether-test-encryption-0123456789abcdef"  # nosec B105


def _context(scopes):
    return {
        "principal": PRINCIPAL,
        "tenant": TENANT,
        "audience": "epistemic-graph",
        "agent_id": PRINCIPAL,
        "roles": [],
        "scopes": scopes,
        "policy_version": "policy:current",
        "delegation": [],
    }


@pytest.fixture
def graph_socket(tmp_path_factory):
    try:
        binary = (
            os.environ.get("EPISTEMIC_GRAPH_TEST_BINARY") or resolve_server_binary()
        )
    except ServerBinaryNotFoundError:
        pytest.skip("epistemic-graph server is not installed")
    tmp_path = tmp_path_factory.mktemp("eg")
    socket = tmp_path / "eg.sock"
    security = tmp_path / "security"
    security.mkdir()
    env = {
        **os.environ,
        "GRAPH_SERVICE_AUTH_SECRET": HMAC,
        "EPISTEMIC_GRAPH_AUDIENCE": "epistemic-graph",
        "EPISTEMIC_GRAPH_TENANT": TENANT,
        "EPISTEMIC_GRAPH_POLICY_VERSION": "policy:current",
        "EPISTEMIC_GRAPH_REQUIRE_OIDC": "false",
        "EPISTEMIC_GRAPH_SECURITY_STATE_DIR": str(security),
        "EPISTEMIC_GRAPH_SIGNER_KEYS_JSON": json.dumps(
            {PRINCIPAL: {"key": SIGNER, "allowed_roles": [], "may_grant_system": True}}
        ),
        "EPISTEMIC_GRAPH_ENCRYPTION_KEY": DATA_KEY,
    }
    with (tmp_path / "graph.log").open("wb") as log:
        proc = subprocess.Popen(
            [
                binary,
                "--socket-path",
                str(socket),
                "--auth-secret",
                HMAC,
                "--persist-dir",
                str(tmp_path / "data"),
            ],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )  # nosec B603
        try:
            deadline = time.monotonic() + 30
            while not socket.exists():
                if proc.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError("test graph did not start")
                time.sleep(0.05)
            client = SyncEpistemicGraphClient.connect(
                socket_path=str(socket),
                auth_secret=HMAC,
                verified_context=_context(["security:bootstrap"]),
            )
            try:
                client.consensus.bootstrap_system_identity(
                    agent_id=PRINCIPAL, signer_id=PRINCIPAL, signer_key=SIGNER
                )
            finally:
                client.close()
            client = SyncEpistemicGraphClient.connect(
                socket_path=str(socket),
                auth_secret=HMAC,
                verified_context=_context(["*"]),
            )
            try:
                client.tenants.create(GRAPH)
            finally:
                client.close()
            yield socket
        finally:
            proc.terminate()
            proc.wait(timeout=30)


def _catalog():
    return McpCatalogSnapshotBinding(
        configuration_revision=7,
        catalog_generation=11,
        snapshot_digest="a" * 64,
        child_connection_generation=3,
        authorization_scope_digest="b" * 64,
    )


def _mutation_context():
    return AgentLibraryMutationContext(
        request_id=1,
        principal="principal-a",
        caller_principal="caller-a",
        attempt_nonce="07" * 32,
        tenant_id=TENANT,
        actor_scope="scope-a",
        purpose_id="purpose-a",
        policy_revision="policy-1",
        policy_digest="sha256:" + "c" * 64,
        policy_decision_id="decision-1",
        idempotency_key="caller-value",
        expected_revision=1,
        trace_id="trace-1",
        created_at_ms=1700000000000,
    )


async def _setup(session, socket):
    client = await EpistemicGraphClient.connect(
        socket_path=str(socket),
        auth_secret=HMAC,
        graph_name=GRAPH,
        verified_context=_context(["*"]),
    )
    context = _mutation_context()
    key = "finance-acceptance:bind"
    await client._send(
        "ConnectorPack",
        {
            "op": {
                "op": "bind",
                "request": {
                    "context": context.model_copy(
                        update={"idempotency_key": key}
                    ).model_dump(mode="json"),
                    "connector": CONNECTOR,
                    "importer": "principal:sha256:"
                    + hashlib.sha256(PRINCIPAL.encode()).hexdigest(),
                },
            }
        },
        None,
        idempotency_key=key,
    )
    pack = await build_content_pack(
        session, connector=CONNECTOR, kinds=[ToolArtifactKind(), ResourceArtifactKind()]
    )
    await ConnectorPackClient(client).import_pack(
        pack.archive,
        connector=CONNECTOR,
        server_package_version=pack.server_package_version,
        producer=PackProducer(name="finance-acceptance", version="1"),
        catalog=_catalog(),
        context=context,
    )
    declaration = build_declaration(
        CONNECTOR,
        await session.list_tools(),
        declared={
            "SOURCES": connector_sources.SOURCES,
            "SCHEMA_MAPPINGS": connector_sources.SCHEMA_MAPPINGS,
        },
    )
    return client, context, contract_from_declaration(declaration)


async def _sync(session, client, context, contract, stream, kind, mapping, params=None):
    source = next(item for item in contract.sync if item.preset == stream)
    if params:
        source = source.model_copy(
            update={"raw": {**source.raw, "params": {**source.raw["params"], **params}}}
        )
    base = McpToolSourceAdapter.from_sync_spec(
        source,
        connector=CONNECTOR,
        mapping_reference=f"connector:{CONNECTOR}#mappings/{mapping}",
    )
    adapter = MarketSourceAdapter(
        base, market_kind=kind, connector=CONNECTOR, stream=stream
    )

    async def authority(_):
        return _catalog(), context

    target = SyncTarget(CONNECTOR, EpistemicGraphSink(client, authority), max_pages=3)
    first = await sync_stream(session, adapter, target)
    await asyncio.sleep(0.6)
    second = await sync_stream(session, adapter, target)
    await asyncio.sleep(0.6)
    assert first.records == second.records
    rows = await client.query.cypher_read(
        f"MATCH (n) WHERE n.source_stream = '{stream}' RETURN n LIMIT 20"
    )
    assert len(rows) == first.records
    return [row["n"] for row in rows]


async def test_fred_served_graph_and_liquidity(graph_socket, monkeypatch):
    panel_module = pytest.importorskip("agent_connector_sdk.finance.liquidity_panel")
    monkeypatch.setenv("MCP_FLEET_REGISTRATION", "false")
    monkeypatch.setattr(tools_macro_series, "resolve_fred_api_key", lambda: "test-key")
    payload = json.loads(
        (Path(__file__).parent / "fixtures/fred_observations.json").read_text()
    )
    vendor = httpx.AsyncClient(
        base_url="https://api.stlouisfed.org/fred",
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json=payload)),
    )
    components = build_server(["--transport", "stdio", "--auth-type", "none"])
    components.clients.fred._client = vendor
    try:
        async with McpTransport().session(
            TransportEndpoint(in_process=components.mcp)
        ) as session:
            client, context, contract = await _setup(session, graph_socket)
            try:
                for stream in (
                    "macro_series_fed_balance_sheet",
                    "macro_series_treasury_general_account",
                    "macro_series_reverse_repo_overnight",
                ):
                    rows = await _sync(
                        session,
                        client,
                        context,
                        contract,
                        stream,
                        MarketSourceKind.FRED,
                        "EconomicIndicator",
                    )
                    assert len(rows) == 3
                    assert all(
                        row["observed_at"]
                        and row["source_provenance"]["connector"] == CONNECTOR
                        for row in rows
                    )
                panel = await panel_module.read_liquidity_panel(
                    client,
                    as_of=datetime.now(UTC) + timedelta(seconds=1),
                    max_age=timedelta(days=365),
                )
                assert panel["net_liquidity_usd"] == -7_198_765_000_000_000
                assert len(panel["heat"]) == 3
                assert all(cell["source_ref"] for cell in panel["heat"])
            finally:
                await client.close()
    finally:
        await vendor.aclose()


async def test_coinglass_served_graph_panels(graph_socket, monkeypatch):
    monkeypatch.setenv("MCP_FLEET_REGISTRATION", "false")
    monkeypatch.setattr(
        tools_coinglass, "resolve_coinglass_api_key", lambda: "test-key"
    )

    async def fetch(url, **kwargs):
        endpoint = url.rsplit("/", 1)[-1]
        if endpoint == "aum":
            assert kwargs["params"] == {"ticker": "IBIT"}
        data = {
            "aum": [{"time": 1704931200000, "aum_usd": 500000000}],
            "fear-greed-history": [
                {"data_list": [42, 55], "time_list": [1704931200, 1705017600]}
            ],
            "whale-position": [
                {
                    "user": "0x" + "ab" * 20,
                    "symbol": "ETH",
                    "position_size": -3.5,
                    "entry_price": 2249.7,
                    "mark_price": 1645.8,
                    "update_time": 1704931200123,
                }
            ],
            "flow-history": [
                {
                    "timestamp": 1704931200000,
                    "etf_flows": [{"etf_ticker": "IBIT", "flow_usd": 111700000}],
                }
            ],
        }
        return {"code": "0", "data": data[endpoint]}

    monkeypatch.setattr(coinglass, "safe_get_json_async", fetch)
    components = build_server(["--transport", "stdio", "--auth-type", "none"])
    async with McpTransport().session(
        TransportEndpoint(in_process=components.mcp)
    ) as session:
        client, context, contract = await _setup(session, graph_socket)
        try:
            rows = await _sync(
                session,
                client,
                context,
                contract,
                "coinglass_etf_fund_flows",
                MarketSourceKind.ETF_FLOW,
                "MacroPanel",
                {"ticker": "IBIT", "license_tag": "licensed"},
            )
            assert len(rows) == 1
            row = rows[0]
            assert row["aum_usd"] == 500000000 and row["net_flow_usd"] == 111700000
            assert row["aum_observed_at"] and row["flow_observed_at"]
            fund = etf_fund_flows_from_source(
                {"flows": [row]},
                tenant_id=TENANT,
                source_id="coinglass_etf_fund_flows",
                provider="coinglass",
                license_tag="licensed",
                observed_at_utc=datetime.fromisoformat(row["observed_at"]),
            )[0]
            assert fund.aum_usd == 500000000 and fund.net_flow_usd == 111700000
            for stream, kind, count in (
                ("coinglass_sentiment", MarketSourceKind.SENTIMENT, 2),
                ("coinglass_onchain", MarketSourceKind.ONCHAIN_POSITION, 1),
            ):
                rows = await _sync(
                    session,
                    client,
                    context,
                    contract,
                    stream,
                    kind,
                    "MacroPanel",
                    {"license_tag": "licensed"},
                )
                assert len(rows) == count
                assert all(
                    row["event_time"]
                    and row["observed_at"]
                    and row["source_provenance"]["connector"] == CONNECTOR
                    for row in rows
                )
        finally:
            await client.close()
