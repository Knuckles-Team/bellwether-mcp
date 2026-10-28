"""Read CoinGlass ETF, sentiment and on-chain source snapshots."""

from typing import Any, Literal

import httpx
from fastmcp import FastMCP

from bellwether_mcp.api.coinglass import read_snapshot
from bellwether_mcp.credentials import resolve_coinglass_api_key
from bellwether_mcp.mcp.source_pages import source_page


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
        dataset: Literal["etf", "sentiment", "onchain"],
        license_tag: str,
        mode: Literal["delta"],
        source_checkpoint: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Read a bounded snapshot; license rights are supplied by the operator."""
        try:
            records = await read_snapshot(
                resolve_coinglass_api_key(), dataset=dataset, license_tag=license_tag
            )
        except (httpx.HTTPError, OSError, ValueError, TypeError, OverflowError):
            raise RuntimeError("CoinGlass data read failed") from None
        return source_page(
            {"items": records, "offset": 0, "limit": len(records) + 1}, mode
        )
