"""FOMC calendar dataset: schema validity, filtering, sourced records, pagination."""

from __future__ import annotations

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
