"""Bounded same-day CoinGlass ETF flow and AUM observations."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from bellwether_mcp.api import coinglass


def _aum_values(aum: list[Any]) -> dict[str, float]:
    if len(aum) > 10000:
        raise ValueError("ETF observation budget exceeded")
    values: dict[str, float] = {}
    for item in aum:
        if not isinstance(item, dict):
            raise ValueError("invalid ETF AUM observation")
        if type(item.get("time")) is not int or item["time"] % 86_400_000:
            raise ValueError("invalid ETF AUM date")
        when, value = (
            coinglass._stamp(item.get("time")),
            coinglass._number(item.get("aum_usd")),
        )
        if when in values or value < 0:
            raise ValueError("invalid ETF AUM observation")
        values[when] = value
    return values


def _selected_flows(
    flows: list[Any], *, ticker: str, capture: str, license_tag: str
) -> list[dict[str, Any]]:
    if len(flows) > 10000:
        raise ValueError("ETF observation budget exceeded")
    selected = [
        row
        for row in coinglass._etf(flows, capture, license_tag)
        if row["ticker"] == ticker
    ]
    if len(selected) > 10000 or len({row["record_id"] for row in selected}) != len(
        selected
    ):
        raise ValueError("invalid ETF flow observations")
    return selected


def _joined_etf(
    flows: list[Any],
    aum: list[Any],
    *,
    ticker: str,
    license_tag: str,
    flow_capture: str,
    aum_capture: str,
) -> list[dict[str, Any]]:
    if aum_capture < flow_capture:
        raise ValueError("ETF capture clock moved backwards")
    values = _aum_values(aum)
    selected = _selected_flows(
        flows, ticker=ticker, capture=flow_capture, license_tag=license_tag
    )
    if not selected or any(row["event_time"] not in values for row in selected):
        raise ValueError("ETF flow has no matching AUM observation")
    return [
        {
            **row,
            "fund_ticker": ticker,
            "flow_date": row["event_time"][:10],
            "aum_usd": values[row["event_time"]],
            "flow_observed_at": flow_capture,
            "aum_observed_at": aum_capture,
            "flow_source_uri": coinglass._BASE + coinglass._PATHS["etf"],
            "aum_source_uri": coinglass._BASE + "/api/etf/bitcoin/aum",
            "observed_at": aum_capture,
        }
        for row in selected
    ]


async def read_etf_fund_flows(
    api_key: str, *, ticker: str, license_tag: str
) -> list[dict[str, Any]]:
    """Join same-ticker, same-timestamp flow and AUM without filling gaps."""
    coinglass._validate_request(api_key, "etf", license_tag)
    if not isinstance(ticker, str) or not coinglass._TICKER.fullmatch(ticker):
        raise ValueError("invalid ETF ticker")
    options: dict[str, Any] = {
        "headers": {"CG-API-KEY": api_key},
        "max_bytes": 2 * 1024 * 1024,
        "max_redirects": 0,
    }
    flows = coinglass._response_data(
        await coinglass.safe_get_json_async(
            coinglass._BASE + coinglass._PATHS["etf"], **options
        )
    )
    flow_capture = datetime.now(UTC).isoformat()
    aum = coinglass._response_data(
        await coinglass.safe_get_json_async(
            coinglass._BASE + "/api/etf/bitcoin/aum",
            params={"ticker": ticker},
            **options,
        )
    )
    return _joined_etf(
        flows,
        aum,
        ticker=ticker,
        license_tag=license_tag,
        flow_capture=flow_capture,
        aum_capture=datetime.now(UTC).isoformat(),
    )
