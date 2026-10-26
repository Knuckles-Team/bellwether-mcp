"""MCP tools backing FRED/ALFRED macro and liquidity series (EH-412/EH-422)."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from bellwether_mcp.api import fred
from bellwether_mcp.config import FRED_MACRO_SERIES
from bellwether_mcp.credentials import resolve_fred_api_key
from bellwether_mcp.errors import UnknownFredSeriesAliasError
from bellwether_mcp.mcp.clients import Clients


def _resolve_alias_or_series_id(series_id: str, alias: str) -> str:
    """Accept either a raw FRED ``series_id`` or one of :data:`FRED_MACRO_SERIES`'s aliases."""
    if alias:
        if alias not in FRED_MACRO_SERIES:
            raise UnknownFredSeriesAliasError(
                f"alias {alias!r} is not one of {sorted(FRED_MACRO_SERIES)}; "
                "pass series_id directly for any other FRED series"
            )
        return FRED_MACRO_SERIES[alias]
    if not series_id:
        raise ValueError("either series_id or alias is required")
    return series_id


def register_macro_series_tools(mcp: FastMCP, clients: Clients) -> None:
    """Register the FRED/ALFRED series-observation and vintage tools."""

    @mcp.tool(
        tags={"macro-series"},
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def fred_macro_series_aliases() -> dict[str, Any]:
        """The named macro/liquidity series aliases this package ships (EH-422)."""
        return {"aliases": dict(FRED_MACRO_SERIES)}

    @mcp.tool(
        tags={"macro-series"},
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def fred_series_observations(
        *,
        series_id: str = "",
        alias: str = "",
        offset: int = 0,
        limit: int = 1000,
        realtime_start: str = "",
        realtime_end: str = "",
    ) -> dict[str, Any]:
        """Observations for a FRED series, by raw ``series_id`` or a named ``alias``.

        Today's latest revision by default; pass ``realtime_start``/
        ``realtime_end`` (``YYYY-MM-DD``) to pin a vintage instead — see
        ``fred_series_observations_asof`` for the common single-date case.
        """
        resolved = _resolve_alias_or_series_id(series_id, alias)
        client = await clients.fred.paced_client()
        return await fred.get_observations(
            client,
            api_key=resolve_fred_api_key(),
            series_id=resolved,
            offset=offset,
            limit=limit,
            realtime_start=realtime_start or None,
            realtime_end=realtime_end or None,
        )

    @mcp.tool(
        tags={"macro-series"},
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def fred_series_observations_asof(
        *,
        vintage_date: str,
        series_id: str = "",
        alias: str = "",
        offset: int = 0,
        limit: int = 1000,
    ) -> dict[str, Any]:
        """Point-in-time (ALFRED) observations: the series exactly as known on ``vintage_date``.

        Reconstructs what a point-in-time backtest would actually have seen —
        no look-ahead into revisions published after ``vintage_date``.
        """
        resolved = _resolve_alias_or_series_id(series_id, alias)
        client = await clients.fred.paced_client()
        return await fred.get_observations_asof(
            client,
            api_key=resolve_fred_api_key(),
            series_id=resolved,
            vintage_date=vintage_date,
            offset=offset,
            limit=limit,
        )

    @mcp.tool(
        tags={"macro-series"},
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def fred_series_vintage_dates(
        *, series_id: str = "", alias: str = "", offset: int = 0, limit: int = 1000
    ) -> dict[str, Any]:
        """Every date this series was revised/published — feed one into `*_asof`."""
        resolved = _resolve_alias_or_series_id(series_id, alias)
        client = await clients.fred.paced_client()
        return await fred.get_vintage_dates(
            client,
            api_key=resolve_fred_api_key(),
            series_id=resolved,
            offset=offset,
            limit=limit,
        )
