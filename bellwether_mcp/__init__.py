"""bellwether-mcp: crypto discovery, Fed macro series and the FOMC calendar.

Wraps CoinMarketCap (crypto discovery/rankings/market caps — not a
venue-specific OHLCV feed; see ``api/coinmarketcap.py``), FRED/ALFRED (Fed
macro and liquidity series with point-in-time vintages), and a curated,
sourced FOMC decision calendar as an MCP tool surface and, through
``agent-connector-sdk``'s declarative ``mcp_tool`` source adapter, as
bounded, checkpointed ingestion streams intended for the ``finance-v1``
world-model ontology once EG's parallel ``feat/finance-core`` publishes its
class/property names (see ``bellwether_mcp/ontology/mappings/source.yaml``
for the current, provisional mapping and how to update it).

This package never calls epistemic-graph directly: extraction rides an
in-process MCP session over its own tool surface, and delivery to a live
graph is owned by ``agent_connector_sdk.runner``/``sinks``.
"""

from __future__ import annotations

from bellwether_mcp._version import __version__

__all__ = ["__version__"]
