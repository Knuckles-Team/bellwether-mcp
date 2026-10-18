"""MCP tool backing the FOMC decision calendar (EH-412): sourced hike/cut/hold records.

Keyless: reads a packaged, curated dataset rather than calling a live vendor
API (the Federal Reserve does not publish one — see
``bellwether_mcp.api.fomc_calendar``).
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from bellwether_mcp.api import fomc_calendar


def register_fomc_calendar_tools(mcp: FastMCP, _clients: object) -> None:
    """Register the FOMC calendar tool. Takes ``clients`` for a uniform signature."""

    @mcp.tool(
        tags={"fomc-calendar"},
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    def fomc_calendar_list(
        since: str = "",
        until: str = "",
        outcome: str = "",
        offset: int = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        """FOMC decisions as sourced records: date, hike/cut/hold, target range, source_url.

        Args:
            since: inclusive ISO ``decision_date`` lower bound.
            until: inclusive ISO ``decision_date`` upper bound.
            outcome: filter to ``"hike"``, ``"cut"`` or ``"hold"`` (default: all).

        Every record carries the Federal Reserve's own press-release URL as
        ``source_url`` — this package asserts nothing beyond what that source
        states.
        """
        return fomc_calendar.list_meetings(
            since=since, until=until, outcome=outcome, offset=offset, limit=limit
        )
