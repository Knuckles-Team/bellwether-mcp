"""Build the bellwether-mcp FastMCP server.

Composition root: one shared :class:`~bellwether_mcp.mcp.clients.Clients`
wired into all three tool-registration modules on top of
``agent_connector_sdk.mcp.server.create_mcp_server`` (secure server
construction, auth, network-exposure checks, fleet registration lease).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, NamedTuple

from agent_connector_sdk.connector_identity import connector_version
from agent_connector_sdk.mcp.content import ConnectorContent
from agent_connector_sdk.mcp.server import create_mcp_server
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from bellwether_mcp.mcp.clients import Clients
from bellwether_mcp.mcp.tools_crypto_reference import register_crypto_reference_tools
from bellwether_mcp.mcp.tools_fomc_calendar import register_fomc_calendar_tools
from bellwether_mcp.mcp.tools_macro_series import register_macro_series_tools

__all__ = ["build_server"]

_INSTRUCTIONS = (
    "Crypto discovery/caps (CoinMarketCap), Fed macro and liquidity series with "
    "point-in-time vintages (FRED/ALFRED), and the FOMC decision calendar "
    "(hike/cut/hold, sourced). Every tool is keyless except cmc_* and fred_*, "
    "whose credentials are resolved server-side — never accept them as tool "
    "arguments. Not a venue-specific OHLCV feed for trading charts: pair with "
    "an emerald-exchange backend for that."
)


class ServerComponents(NamedTuple):
    """The server and its existing startup/lifetime collaborators."""

    mcp: FastMCP[Any]
    args: Any
    middlewares: list[Any]
    clients: Clients


def build_server(
    command_args: list[str] | None = None,
) -> ServerComponents:
    """Return ``(mcp, args, middlewares, clients)``; the caller runs ``mcp``."""
    args, mcp, middlewares = create_mcp_server(
        name="bellwether-mcp",
        version=connector_version("bellwether_mcp"),
        instructions=_INSTRUCTIONS,
        command_args=command_args,
        content=ConnectorContent.for_package(
            "bellwether_mcp",
            Path(__file__).resolve().parents[1],
            connector_version("bellwether_mcp"),
        ),
    )
    clients = Clients()
    register_crypto_reference_tools(mcp, clients)
    register_macro_series_tools(mcp, clients)
    register_fomc_calendar_tools(mcp, clients)

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(_request: Request) -> JSONResponse:
        return JSONResponse({"status": "OK"})

    for middleware in middlewares:
        mcp.add_middleware(middleware)
    return ServerComponents(mcp, args, middlewares, clients)
