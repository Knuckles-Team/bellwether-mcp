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

from agent_connector_sdk.connector import Connector
from agent_connector_sdk.connector_hooks import RegistrationContext

from bellwether_mcp._version import __version__

_INSTRUCTIONS = (
    "Crypto discovery/caps (CoinMarketCap), Fed macro and liquidity series with "
    "point-in-time vintages (FRED/ALFRED), and the FOMC decision calendar "
    "(hike/cut/hold, sourced). Every tool is keyless except cmc_* and fred_*, "
    "whose credentials are resolved server-side — never accept them as tool "
    "arguments. Not a venue-specific OHLCV feed for trading charts: pair with "
    "an emerald-exchange backend for that."
)


def _register_legacy_tools(context: RegistrationContext) -> None:
    """Register the existing tool modules through the SDK's shared hook."""
    from bellwether_mcp.mcp.clients import Clients
    from bellwether_mcp.mcp.tools_crypto_reference import (
        register_crypto_reference_tools,
    )
    from bellwether_mcp.mcp.tools_fomc_calendar import register_fomc_calendar_tools
    from bellwether_mcp.mcp.tools_macro_series import register_macro_series_tools

    clients = Clients()
    register_crypto_reference_tools(context.server, clients)
    register_macro_series_tools(context.server, clients)
    register_fomc_calendar_tools(context.server, clients)


connector = Connector(
    instructions=_INSTRUCTIONS,
    extra_registrations=(_register_legacy_tools,),
)

__all__ = ["__version__", "connector"]
