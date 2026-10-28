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


@pytest.fixture
def no_vendor_requests():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return json_response({"observations": [], "count": 0})

    return calls, handler


@pytest.mark.spec("CONN-BELLWETHER-MCP-FRED-VINTAGE-R001")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value",
    ["", " ", "20260801", "2026-2-01", "2026-02-30", "2026-01-01T00:00:00", None],
)
async def test_asof_refuses_invalid_vintage_before_request(value, no_vendor_requests):
    calls, handler = no_vendor_requests

    async with mock_client("https://api.stlouisfed.org/fred", handler) as client:
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            await fred.get_observations_asof(
                client, api_key="k", series_id="WALCL", vintage_date=value
            )
    assert calls == []


@pytest.mark.spec("CONN-BELLWETHER-MCP-FRED-VINTAGE-R001")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "start,end", [("", None), (None, ""), ("2026-08-02", "2026-08-01")]
)
async def test_invalid_explicit_realtime_windows_never_request(
    start, end, no_vendor_requests
):
    calls, handler = no_vendor_requests

    async with mock_client("https://api.stlouisfed.org/fred", handler) as client:
        with pytest.raises(ValueError):
            await fred.get_observations(
                client,
                api_key="k",
                series_id="WALCL",
                realtime_start=start,
                realtime_end=end,
            )
    assert calls == []


def _served_fred(http, monkeypatch):
    from types import SimpleNamespace

    from fastmcp import FastMCP

    from bellwether_mcp.mcp import tools_macro_series

    class Endpoint:
        async def paced_client(self):
            return http

    monkeypatch.setattr(tools_macro_series, "resolve_fred_api_key", lambda: "k")
    server = FastMCP("fred-test")
    tools_macro_series.register_macro_series_tools(
        server, SimpleNamespace(fred=Endpoint())
    )
    return server


@pytest.mark.spec("CONN-BELLWETHER-MCP-FRED-VINTAGE-R001")
@pytest.mark.asyncio
async def test_served_asof_refuses_missing_vintage_without_upstream_call(
    monkeypatch, no_vendor_requests
):
    from fastmcp import Client

    calls, handler = no_vendor_requests

    async with mock_client("https://api.stlouisfed.org/fred", handler) as http:
        server = _served_fred(http, monkeypatch)
        async with Client(server) as client:
            result = await client.call_tool(
                "fred_series_observations_asof",
                {"series_id": "WALCL", "vintage_date": ""},
                raise_on_error=False,
            )
            assert result.is_error
        assert calls == []


async def _assert_served_fred_refuses(payload, monkeypatch):
    from fastmcp import Client

    async with mock_client(
        "https://api.stlouisfed.org/fred", lambda r: json_response(payload)
    ) as http:
        server = _served_fred(http, monkeypatch)
        async with Client(server) as client:
            result = await client.call_tool(
                "fred_series_observations", {"series_id": "WALCL"}, raise_on_error=False
            )
            assert result.is_error


@pytest.mark.spec("CONN-BELLWETHER-MCP-FRED-VINTAGE-R002")
@pytest.mark.asyncio
@pytest.mark.parametrize("value", ["NaN", "inf", "-inf", "1e309"])
async def test_served_fred_refuses_nonfinite_observations(value, fixture, monkeypatch):
    payload = fixture("fred_observations.json")
    payload["observations"][0]["value"] = value
    await _assert_served_fred_refuses(payload, monkeypatch)


@pytest.mark.spec("CONN-BELLWETHER-MCP-FRED-VINTAGE-R003")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"observations": None},
        {"observations": {}},
        {"observations": ["invalid"]},
        [],
    ],
)
async def test_served_fred_refuses_malformed_observation_pages(payload, monkeypatch):
    await _assert_served_fred_refuses(payload, monkeypatch)


@pytest.mark.spec("CONN-BELLWETHER-MCP-FRED-VINTAGE-R003")
@pytest.mark.asyncio
async def test_empty_observation_page_is_valid():
    async with mock_client(
        "https://api.stlouisfed.org/fred",
        lambda r: json_response({"observations": [], "count": 0}),
    ) as client:
        result = await fred.get_observations(client, api_key="k", series_id="WALCL")
    assert result["items"] == []
    assert result["total"] == 0


@pytest.mark.spec("CONN-BELLWETHER-MCP-FRED-VINTAGE-R004")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field,replacement",
    [
        ("date", None),
        ("realtime_start", None),
        ("value", None),
        ("date", "20260101"),
        ("realtime_start", "2026-02-30"),
    ],
)
async def test_served_fred_refuses_missing_or_invalid_identity(
    field, replacement, fixture, monkeypatch
):
    payload = fixture("fred_observations.json")
    observation = payload["observations"][0]
    if replacement is None:
        del observation[field]
    else:
        observation[field] = replacement
    await _assert_served_fred_refuses(payload, monkeypatch)
