"""Build this package's ``SourceAdapter``s from its declarative presets.

One :class:`~agent_connector_sdk.adapters.mcp_tool.McpToolSourceAdapter` per
entry of ``mcp_source_presets.json`` — no bespoke per-source adapter code
(RF-ADR-009 2.2.1: "a new API source is a preset, not code"). This is the
authoritative wiring from a stream onto its (provisional — see
``ontology/mappings/source.yaml``) finance-v1 class: each preset's
``doc_type``/``ontology_class`` pair becomes one ``SchemaMapping`` entry, keyed
exactly as :func:`build_source_adapters` tells every adapter to reference it.
"""

from __future__ import annotations

import json
from importlib import resources
from typing import Any

from agent_connector_sdk.adapters.mcp_tool import McpToolSourceAdapter
from agent_connector_sdk.manifest.model import SchemaMapping
from agent_connector_sdk.manifest.presets import ToolPreset

__all__ = ["CONNECTOR_NAME", "build_schema_mappings", "build_source_adapters"]

CONNECTOR_NAME = "bellwether-mcp"


def _read_json(name: str) -> dict[str, Any]:
    return json.loads(
        resources.files("bellwether_mcp.connectors").joinpath(name).read_text()
    )


def _presets() -> dict[str, dict[str, Any]]:
    return {
        name: raw
        for name, raw in _read_json("mcp_source_presets.json").items()
        if not name.startswith("_")
    }


def _fingerprints() -> dict[str, str]:
    return _read_json("tool_schema_fingerprints.json")["tools"]


def build_schema_mappings(
    presets: dict[str, dict[str, Any]] | None = None,
) -> dict[str, SchemaMapping]:
    """One ``SchemaMapping`` per stream, keyed by its preset name.

    Keying by ``doc_type`` instead would silently collapse distinct classes
    that share one identity bucket — all seven ``macro_series_*`` streams
    share ``doc_type="macro_series_observation"`` (they differ only by which
    FRED series they pull) yet are still seven independently checkpointed
    streams. The preset name is always unique.
    """
    return {
        name: SchemaMapping(ontology_class=str(raw["ontology_class"]))
        for name, raw in (presets or _presets()).items()
    }


def build_source_adapters(
    *, connector: str = CONNECTOR_NAME
) -> tuple[McpToolSourceAdapter, ...]:
    """One adapter per declared stream, each pinned to its live tool fingerprint."""
    presets = _presets()
    fingerprints = _fingerprints()
    mappings = build_schema_mappings(presets)
    adapters = []
    for name, raw in presets.items():
        preset = ToolPreset.from_mapping(name, raw)
        adapters.append(
            McpToolSourceAdapter(
                preset,
                connector=connector,
                tool_schema_sha256=fingerprints[preset.tool],
                mapping_reference=f"manifest:{connector}#schema_mappings/{name}",
                schema_mappings=mappings,
            )
        )
    return tuple(adapters)
