"""CONN-BELLWETHER-MCP-CONNECTOR-CONTENT-R001: the server lists its packaged skills, ontology and prompts by default."""

from __future__ import annotations

import asyncio
import importlib
from pathlib import Path

import pytest
from fastmcp import Client

PACKAGE = "bellwether_mcp"
ROOT = Path(list(importlib.import_module(PACKAGE).__path__)[0])

pytestmark = pytest.mark.spec("CONN-BELLWETHER-MCP-CONNECTOR-CONTENT-R001")


def _server():
    module = importlib.import_module("bellwether_mcp.mcp.server")
    return module.build_server(
        command_args=["--transport", "stdio", "--auth-type", "none"]
    )[0]


async def _assert_packaged_resources(client, resources):
    for uri in resources:
        if uri.startswith(("ontology://", "shapes://")):
            directory = ROOT / "ontology"
            if uri.startswith("shapes://"):
                directory = directory / "shapes"
            actual = await client.read_resource(uri)
            assert (
                actual[0].text.encode()
                == (directory / uri.rsplit("/", 1)[-1]).read_bytes()
            )


async def _listings():
    async with Client(_server()) as client:
        resources = {str(r.uri) for r in await client.list_resources()}
        prompts = {p.name for p in await client.list_prompts()}
        await _assert_packaged_resources(client, resources)
    return resources, prompts


def test_default_content_surfaces() -> None:
    resources, prompts = asyncio.run(_listings())
    if list(ROOT.glob("skills/*/SKILL.md")):
        assert any(u.startswith("skill://") for u in resources)
    if list(ROOT.glob("ontology/*.ttl")):
        assert any(u.startswith("ontology://bellwether-mcp/") for u in resources)
    for path in ROOT.glob("prompts/*.json"):
        if not path.name.startswith("_"):
            assert path.stem in prompts


@pytest.fixture(autouse=True)
def _no_outbound_network(monkeypatch):
    import socket

    def refuse(*_args, **_kwargs):
        raise AssertionError("content publication must not contact an external system")

    monkeypatch.setenv("MCP_FLEET_REGISTRATION", "false")
    monkeypatch.setattr(socket.socket, "connect", refuse)


def test_sdk_floor_supports_content_identity_and_current_pack_protocol() -> None:
    import tomllib

    from packaging.requirements import Requirement

    project = tomllib.loads((ROOT.parent / "pyproject.toml").read_text())["project"]
    declared = list(project.get("dependencies", []))
    for extra in project.get("optional-dependencies", {}).values():
        declared.extend(extra)
    sdk = [Requirement(value) for value in declared if value.startswith("scion-sdk")]
    assert sdk
    for requirement in sdk:
        assert requirement.specifier.contains("0.5.6")
        assert not requirement.specifier.contains("0.5.5")


def test_sdk_loads_every_preserved_source_mapping_and_resource():
    from agent_connector_sdk.ingest.live_declaration import load_declaration

    declared = load_declaration(PACKAGE)
    assert declared.connector == "bellwether-mcp"
    assert len(declared.sources) == 9
    assert set(declared.schema_mappings) == {
        "MarketDataSyncRun",
        "Instrument",
        "EconomicIndicator",
        "MacroEvent",
        "MacroPanel",
    }
    assert len(declared.resources) == 1


def test_production_content_pack_binds_packaged_ontology_and_shapes():
    import hashlib
    from importlib.metadata import version

    from agent_connector_sdk.artifacts.pack import build_content_pack
    from agent_connector_sdk.artifacts.resources import ResourceArtifactKind
    from agent_connector_sdk.ports.session import TransportEndpoint
    from agent_connector_sdk.transports.mcp import McpTransport

    async def capture():
        async with McpTransport().session(
            TransportEndpoint(in_process=_server())
        ) as session:
            return await build_content_pack(
                session, connector="bellwether-mcp", kinds=(ResourceArtifactKind(),)
            )

    pack = asyncio.run(capture())
    assert pack.server_package_version == version("bellwether-mcp")
    entries = {str(entry.uri): entry for entry in pack.archive.entries}
    assert "connector://resources" in entries
    for path in ROOT.glob("ontology/**/*.ttl"):
        scheme = "shapes" if path.parent.name == "shapes" else "ontology"
        uri = f"{scheme}://bellwether-mcp/{path.name}"
        assert entries[uri].body.sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
