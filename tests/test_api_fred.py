"""FRED/ALFRED client: observations, point-in-time vintages, missing-value handling."""

from __future__ import annotations

import httpx
import pytest

from bellwether_mcp.api import fred
from tests.conftest import json_response, mock_client


@pytest.mark.asyncio
async def test_get_observations_maps_missing_value_dot_to_none(fixture):
    payload = fixture("fred_observations.json")

    async with mock_client(
        "https://api.stlouisfed.org/fred", lambda r: json_response(payload)
    ) as client:
        result = await fred.get_observations(client, api_key="k", series_id="WALCL")

    assert result["total"] == 3
    values = [item["value"] for item in result["items"]]
    assert values == [7215432.0, 7198765.0, None]  # the "." observation becomes None
    assert all(item["observation_id"].startswith("WALCL:") for item in result["items"])


@pytest.mark.asyncio
async def test_get_observations_asof_pins_realtime_window(fixture):
    payload = fixture("fred_observations.json")
    seen_params: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_params.update(dict(request.url.params))
        return json_response(payload)

    async with mock_client("https://api.stlouisfed.org/fred", handler) as client:
        await fred.get_observations_asof(
            client, api_key="k", series_id="WALCL", vintage_date="2026-08-01"
        )

    assert seen_params["realtime_start"] == "2026-08-01"
    assert seen_params["realtime_end"] == "2026-08-01"


@pytest.mark.asyncio
async def test_get_observations_without_vintage_omits_realtime_params(fixture):
    payload = fixture("fred_observations.json")
    seen_params: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_params.update(dict(request.url.params))
        return json_response(payload)

    async with mock_client("https://api.stlouisfed.org/fred", handler) as client:
        await fred.get_observations(client, api_key="k", series_id="WALCL")

    assert "realtime_start" not in seen_params
    assert "realtime_end" not in seen_params


@pytest.mark.asyncio
async def test_get_vintage_dates_lists_every_revision(fixture):
    payload = fixture("fred_vintage_dates.json")

    async with mock_client(
        "https://api.stlouisfed.org/fred", lambda r: json_response(payload)
    ) as client:
        result = await fred.get_vintage_dates(client, api_key="k", series_id="WALCL")

    assert result["total"] == 3
    assert [item["vintage_date"] for item in result["items"]] == [
        "2026-07-01",
        "2026-08-01",
        "2026-09-01",
    ]
    assert result["items"][0]["vintage_id"] == "WALCL:2026-07-01"
