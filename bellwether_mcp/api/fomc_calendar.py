"""The FOMC decision calendar as sourced records (EH-412).

The Federal Reserve does not publish its meeting calendar or decisions as a
JSON API — only as HTML
(https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) and one
press-release page per meeting. This module therefore reads a curated,
versioned dataset (``bellwether_mcp/connectors/fomc_meetings.json``) instead
of scraping HTML at call time. Every record carries the Federal Reserve's own
press-release URL as ``source_url`` — never asserted as one of this package's
own findings. See ``AGENTS.md``'s "FOMC dataset provenance" section for how
and when this dataset was verified, and how to extend it.

No network I/O happens here; loading is a pure, cached read of packaged data.
"""

from __future__ import annotations

import json
from datetime import date
from functools import lru_cache
from importlib import resources
from typing import Any

from bellwether_mcp.errors import UnknownFomcOutcomeFilterError

__all__ = ["VALID_OUTCOMES", "list_meetings", "load_meetings"]

VALID_OUTCOMES = frozenset({"hike", "cut", "hold"})


@lru_cache(maxsize=1)
def load_meetings() -> tuple[dict[str, Any], ...]:
    """The full curated FOMC meeting dataset, oldest first, each record sourced."""
    raw = json.loads(
        resources.files("bellwether_mcp.connectors")
        .joinpath("fomc_meetings.json")
        .read_text()
    )
    meetings = tuple(raw["meetings"])
    for meeting in meetings:
        if meeting["outcome"] not in VALID_OUTCOMES:
            raise ValueError(
                f"fomc_meetings.json has an invalid outcome {meeting['outcome']!r} "
                f"for {meeting['decision_date']!r} (expected one of {sorted(VALID_OUTCOMES)})"
            )
    return meetings


def _record(meeting: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": meeting["decision_date"],
        "meeting_start_date": meeting["meeting_start_date"],
        "decision_date": meeting["decision_date"],
        "announcement_time_utc": meeting["announcement_time_utc"],
        "outcome": meeting["outcome"],
        "bps_change": meeting["bps_change"],
        "target_range_low_pct": meeting["target_range_low_pct"],
        "target_range_high_pct": meeting["target_range_high_pct"],
        "source_url": meeting["source_url"],
    }


def _date_bound(value: str) -> date | None:
    if value == "":
        return None
    if not isinstance(value, str):
        raise ValueError("FOMC date bound must be YYYY-MM-DD")
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("FOMC date bound must be YYYY-MM-DD")
    return parsed


def _validate_date_range(since: str, until: str) -> None:
    lower, upper = _date_bound(since), _date_bound(until)
    if lower is not None and upper is not None and lower > upper:
        raise ValueError("FOMC date range is reversed")


def _matches_filters(
    meeting: dict[str, Any], *, since: str, until: str, outcome: str
) -> bool:
    """Apply the existing inclusive date and exact outcome filters."""
    return (
        (not since or meeting["decision_date"] >= since)
        and (not until or meeting["decision_date"] <= until)
        and (not outcome or meeting["outcome"] == outcome)
    )


def list_meetings(
    *,
    since: str = "",
    until: str = "",
    outcome: str = "",
    offset: int = 0,
    limit: int = 100,
) -> dict[str, Any]:
    """Sourced FOMC decision records, optionally filtered by date range/outcome.

    Args:
        since: inclusive ISO ``decision_date`` lower bound (``""`` = no bound).
        until: inclusive ISO ``decision_date`` upper bound (``""`` = no bound).
        outcome: one of ``"hike"``, ``"cut"``, ``"hold"``, or ``""`` for all.

    Raises:
        UnknownFomcOutcomeFilterError: ``outcome`` is not empty and not one of
            :data:`VALID_OUTCOMES`.
    """
    _validate_date_range(since, until)
    if outcome and outcome not in VALID_OUTCOMES:
        raise UnknownFomcOutcomeFilterError(
            f"outcome {outcome!r} is not one of {sorted(VALID_OUTCOMES)}"
        )
    matches = [
        m
        for m in load_meetings()
        if _matches_filters(m, since=since, until=until, outcome=outcome)
    ]
    page = matches[offset : offset + limit]
    return {
        "items": [_record(m) for m in page],
        "offset": offset,
        "limit": limit,
        "total": len(matches),
    }
