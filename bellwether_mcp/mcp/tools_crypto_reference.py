"""MCP tools backing the CoinMarketCap discovery/caps stream (EH-412)."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from bellwether_mcp.api import coinmarketcap
from bellwether_mcp.credentials import resolve_cmc_api_key
from bellwether_mcp.mcp.clients import Clients


def register_crypto_reference_tools(mcp: FastMCP, clients: Clients) -> None:
    """Register the CoinMarketCap listings/quotes/global-metrics tools."""

    @mcp.tool(
        tags={"crypto-reference"},
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def cmc_listings(start: int = 1, limit: int = 100) -> dict[str, Any]:
        """Latest cryptocurrency listings ranked by market cap (discovery/caps).

        Not a venue-specific OHLCV feed — use an emerald-exchange backend for
        tradable bars. The API key is resolved server-side, never accepted as
        an argument.
        """
        client = await clients.coinmarketcap.paced_client()
        return await coinmarketcap.list_listings(
            client, api_key=resolve_cmc_api_key(), start=start, limit=limit
        )

    @mcp.tool(
        tags={"crypto-reference"},
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def cmc_quotes(symbols: str) -> dict[str, Any]:
        """Latest quote(s) for comma-separated symbols, e.g. ``"BTC,ETH"``."""
        client = await clients.coinmarketcap.paced_client()
        return await coinmarketcap.get_quotes(
            client, api_key=resolve_cmc_api_key(), symbols=symbols
        )

    @mcp.tool(
        tags={"crypto-reference"},
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def cmc_global_metrics() -> dict[str, Any]:
        """Aggregate crypto market metrics: total cap, dominance, 24h volume.

        A macro/liquidity gauge for the crypto market as a whole (EH-422).
        """
        client = await clients.coinmarketcap.paced_client()
        return await coinmarketcap.get_global_metrics(
            client, api_key=resolve_cmc_api_key()
        )
