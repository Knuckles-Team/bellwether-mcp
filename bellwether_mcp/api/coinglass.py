"""Bounded CoinGlass ETF flows, sentiment and on-chain position snapshots."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import UTC, datetime, timedelta
from typing import Any

from scion_sdk.source_connectors.http_safety import safe_get_json_async

_BASE = "https://open-api-v4.coinglass.com"
_PATHS = {
    "etf": "/api/etf/bitcoin/flow-history",
    "sentiment": "/api/index/fear-greed-history",
    "onchain": "/api/hyperliquid/whale-position",
}
_TICKER = re.compile(r"^[A-Z0-9][A-Z0-9.\-]{0,19}$")
_WALLET = re.compile(r"^0x[0-9a-fA-F]{40}$")
_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def _number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("invalid CoinGlass number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("invalid CoinGlass number")
    return result


def _stamp(value: Any, *, seconds: bool = False) -> str:
    if type(value) is not int or value < 0:
        raise ValueError("invalid CoinGlass timestamp")
    try:
        moment = _EPOCH + timedelta(milliseconds=value * (1000 if seconds else 1))
    except OverflowError:
        raise ValueError("invalid CoinGlass timestamp") from None
    return moment.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _identity(*parts: str) -> str:
    return hashlib.sha256(json.dumps(parts, separators=(",", ":")).encode()).hexdigest()


def _etf(items: list[Any], observed: str, license_tag: str) -> list[dict[str, Any]]:
    records = []
    for day in items:
        if not isinstance(day, dict) or not isinstance(day.get("etf_flows"), list):
            raise ValueError("invalid ETF flow page")
        when = _stamp(day.get("timestamp"))
        for flow in day["etf_flows"]:
            if not isinstance(flow, dict):
                raise TypeError("invalid ETF flow")
            ticker = flow.get("etf_ticker")
            if not isinstance(ticker, str) or not _TICKER.fullmatch(ticker):
                raise ValueError("invalid ETF ticker")
            records.append(
                {
                    "record_id": _identity("etf", ticker, when),
                    "dataset": "etf",
                    "ticker": ticker,
                    "event_time": when,
                    "observed_at": observed,
                    "net_flow_usd": _number(flow.get("flow_usd")),
                    "provider": "coinglass",
                    "license_tag": license_tag,
                }
            )
    return records


def _sentiment(
    items: list[Any], observed: str, license_tag: str
) -> list[dict[str, Any]]:
    if len(items) != 1 or not isinstance(items[0], dict):
        raise ValueError("invalid sentiment page")
    values, times = items[0].get("data_list"), items[0].get("time_list")
    if (
        not isinstance(values, list)
        or not isinstance(times, list)
        or len(values) != len(times)
    ):
        raise ValueError("invalid sentiment series")
    return [
        {
            "record_id": _identity("sentiment", when),
            "dataset": "sentiment",
            "event_time": when,
            "observed_at": observed,
            "value": _number(value),
            "provider": "coinglass",
            "license_tag": license_tag,
        }
        for value, stamp in zip(values, times, strict=True)
        for when in [_stamp(stamp, seconds=True)]
    ]


def _positions(
    items: list[Any], observed: str, license_tag: str
) -> list[dict[str, Any]]:
    records = []
    for item in items:
        if not isinstance(item, dict):
            raise TypeError("invalid position")
        wallet, symbol = item.get("user"), item.get("symbol")
        if (
            not isinstance(wallet, str)
            or not _WALLET.fullmatch(wallet)
            or not isinstance(symbol, str)
            or not _TICKER.fullmatch(symbol)
        ):
            raise ValueError("invalid on-chain position identity")
        wallet = wallet.lower()
        updated = _stamp(item.get("update_time"))
        records.append(
            {
                "record_id": _identity("onchain", wallet, symbol),
                "dataset": "onchain",
                "wallet": wallet,
                "symbol": symbol,
                "event_time": updated,
                "observed_at": observed,
                "position_size": _number(item.get("position_size")),
                "entry_price": _number(item.get("entry_price")),
                "mark_price": _number(item.get("mark_price")),
                "provider": "coinglass",
                "license_tag": license_tag,
            }
        )
    return records


def _validate_request(api_key: str, dataset: str, license_tag: str) -> None:
    if (
        dataset not in _PATHS
        or not isinstance(license_tag, str)
        or not license_tag.strip()
        or not isinstance(api_key, str)
        or not api_key.strip()
    ):
        raise ValueError("CoinGlass source requires a dataset, key and license tag")


def _response_data(payload: Any) -> list[Any]:
    if (
        not isinstance(payload, dict)
        or payload.get("code") != "0"
        or not isinstance(payload.get("data"), list)
    ):
        raise ValueError("invalid CoinGlass response")
    return payload["data"]


async def read_snapshot(
    api_key: str, *, dataset: str, license_tag: str
) -> list[dict[str, Any]]:
    """Read one bounded vendor snapshot without asserting complete history."""
    _validate_request(api_key, dataset, license_tag)
    payload = await safe_get_json_async(
        _BASE + _PATHS[dataset],
        headers={"CG-API-KEY": api_key},
        max_bytes=2 * 1024 * 1024,
        max_redirects=0,
    )
    observed = datetime.now(UTC).isoformat()
    mapper = {"etf": _etf, "sentiment": _sentiment, "onchain": _positions}[dataset]
    records = mapper(_response_data(payload), observed, license_tag)
    if len(records) > 10000 or len({item["record_id"] for item in records}) != len(
        records
    ):
        raise ValueError("invalid CoinGlass record set")
    return records
