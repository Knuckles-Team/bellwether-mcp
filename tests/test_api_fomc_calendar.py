"""FOMC calendar dataset: schema validity, filtering, sourced records, pagination."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from bellwether_mcp.api import fomc_calendar
from bellwether_mcp.errors import UnknownFomcOutcomeFilterError


def test_every_record_is_sourced_with_a_federal_reserve_url():
    for meeting in fomc_calendar.load_meetings():
        assert meeting["source_url"].startswith(
            "https://www.federalreserve.gov/newsevents/pressreleases/monetary"
        )


def test_every_outcome_is_a_valid_hike_cut_hold():
    for meeting in fomc_calendar.load_meetings():
        assert meeting["outcome"] in fomc_calendar.VALID_OUTCOMES


def test_dataset_is_chronologically_ordered_with_no_duplicate_decision_dates():
    meetings = fomc_calendar.load_meetings()
    dates = [m["decision_date"] for m in meetings]
    assert dates == sorted(dates)
    assert len(dates) == len(set(dates))


def test_bps_change_sign_matches_outcome():
    for meeting in fomc_calendar.load_meetings():
        if meeting["outcome"] == "hike":
            assert meeting["bps_change"] > 0
        elif meeting["outcome"] == "cut":
            assert meeting["bps_change"] < 0
        else:
            assert meeting["bps_change"] == 0


def test_target_range_is_internally_consistent():
    for meeting in fomc_calendar.load_meetings():
        assert meeting["target_range_high_pct"] - meeting[
            "target_range_low_pct"
        ] == pytest.approx(0.25)


def test_list_meetings_filters_by_outcome():
    result = fomc_calendar.list_meetings(outcome="cut")

    assert result["total"] > 0
    assert all(item["outcome"] == "cut" for item in result["items"])


def test_list_meetings_filters_by_date_range():
    result = fomc_calendar.list_meetings(since="2024-09-01", until="2024-12-31")

    assert result["total"] == 3  # Sep, Nov, Dec 2024 cuts
    assert all(
        "2024-09" <= item["decision_date"][:7] <= "2024-12" for item in result["items"]
    )


def test_list_meetings_rejects_unknown_outcome_filter():
    with pytest.raises(UnknownFomcOutcomeFilterError):
        fomc_calendar.list_meetings(outcome="pause")


def test_list_meetings_paginates():
    first = fomc_calendar.list_meetings(limit=5, offset=0)
    second = fomc_calendar.list_meetings(limit=5, offset=5)

    assert len(first["items"]) == 5
    assert len(second["items"]) == 5
    assert first["items"][0]["id"] != second["items"][0]["id"]
    assert first["total"] == second["total"]


def test_record_id_is_the_decision_date():
    result = fomc_calendar.list_meetings(limit=1)
    assert result["items"][0]["id"] == result["items"][0]["decision_date"]


def test_returned_announcement_times_match_sourced_release_dates():
    records = fomc_calendar.list_meetings()["items"]
    for record in records:
        timestamp = datetime.fromisoformat(record["announcement_time_utc"])
        assert timestamp.tzinfo == UTC
        assert timestamp.date().isoformat() == record["decision_date"]
    by_date = {record["decision_date"]: record for record in records}
    assert by_date["2023-02-01"]["announcement_time_utc"] == "2023-02-01T19:00:00Z"
    assert by_date["2023-03-22"]["announcement_time_utc"] == "2023-03-22T18:00:00Z"
    assert by_date["2026-01-28"]["source_url"].endswith("monetary20260128a.htm")


@pytest.mark.spec("CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R002")
@pytest.mark.asyncio
async def test_declared_fomc_source_retains_announcement_through_sdk():
    from fastmcp import FastMCP

    from bellwether_mcp.mcp.tools_fomc_calendar import register_fomc_calendar_tools
    from tests.conftest import sdk_source_pages

    server = FastMCP("fomc-test")
    register_fomc_calendar_tools(server, None)
    first, second = await sdk_source_pages(
        server, "fomc_calendar", "MacroEvent", second_page=False
    )
    assert second is None
    curated = fomc_calendar.list_meetings()["items"][0]
    record = first.records[0]
    assert record.record_id == curated["id"]
    assert record.payload["announcement_time_utc"] == curated["announcement_time_utc"]
    assert record.payload["source_url"] == curated["source_url"]
    assert record.provenance.connector == "bellwether-mcp"
    assert record.provenance.tool == "fomc_calendar_list"


@pytest.mark.spec("CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R003")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "arguments",
    [
        {"since": "20260101"},
        {"until": "2026-02-30"},
        {"since": "2026-01-01T00:00:00"},
        {"since": "2026-02-02", "until": "2026-02-01"},
    ],
)
async def test_served_fomc_refuses_invalid_date_ranges(arguments):
    from fastmcp import Client, FastMCP

    from bellwether_mcp.mcp.tools_fomc_calendar import register_fomc_calendar_tools

    server = FastMCP("fomc-test")
    register_fomc_calendar_tools(server, None)
    async with Client(server) as client:
        result = await client.call_tool(
            "fomc_calendar_list", arguments, raise_on_error=False
        )
    assert result.is_error


@pytest.mark.spec("CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R003")
def test_fomc_date_range_accepts_equal_inclusive_bounds():
    day = fomc_calendar.load_meetings()[0]["decision_date"]
    page = fomc_calendar.list_meetings(since=day, until=day)
    assert [item["decision_date"] for item in page["items"]] == [day]
