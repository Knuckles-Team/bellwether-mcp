"""Read CoinGlass ETF, sentiment and on-chain source snapshots."""

from typing import Any, Literal

import httpx
from fastmcp import FastMCP

from bellwether_mcp.api.coinglass import read_snapshot
from bellwether_mcp.api.coinglass_etf import read_etf_fund_flows
from bellwether_mcp.credentials import resolve_coinglass_api_key
from bellwether_mcp.mcp.source_pages import source_page


async def _read_macro(
    dataset: str, ticker: str | None, license_tag: str
) -> list[dict[str, Any]]:
    key = resolve_coinglass_api_key()
    if dataset == "etf_fund_flows":
        if ticker is None:
            raise ValueError("ETF fund flows require a ticker")
        return await read_etf_fund_flows(key, ticker=ticker, license_tag=license_tag)
    if ticker is not None:
        raise ValueError("ticker is only valid for ETF fund flows")
    return await read_snapshot(key, dataset=dataset, license_tag=license_tag)


def register_coinglass_tools(mcp: FastMCP) -> None:
    """Register the bounded source tool without exposing provider credentials."""

    @mcp.tool(
        tags={"macro-panel"},
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def coinglass_macro_snapshot(
        *,
        dataset: Literal["etf", "etf_fund_flows", "sentiment", "onchain"],
        license_tag: str,
        mode: Literal["delta"],
        ticker: str | None = None,
        source_checkpoint: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Read a bounded snapshot; license rights are supplied by the operator."""
        try:
            records = await _read_macro(dataset, ticker, license_tag)
        except (httpx.HTTPError, OSError, ValueError, TypeError, OverflowError):
            raise RuntimeError("CoinGlass data read failed") from None
        return source_page(
            {"items": records, "offset": 0, "limit": len(records) + 1}, mode
        )
