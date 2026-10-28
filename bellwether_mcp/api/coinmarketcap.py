"""CoinMarketCap Pro API: crypto discovery, rankings, market caps (EH-412).

https://coinmarketcap.com/api/documentation/pro-api-reference/cryptocurrency.
CMC is a discovery/caps source, not a venue-specific OHLCV feed — its general
historical OHLCV endpoint documents hourly/daily coverage only and must not
be assumed to supply minute-level exchange candles (that role stays with
emerald-exchange's venue backends). This client therefore exposes listings,
per-symbol quotes and global market metrics only.

Every endpoint requires ``X-CMC_PRO_API_KEY`` — there is no keyless CMC
endpoint, including the free "Basic" plan.
"""

from __future__ import annotations

from math import isfinite
from typing import Any

import httpx

__all__ = ["get_global_metrics", "get_quotes", "list_listings"]


def _finite_number(value: Any) -> int | float | None:
    if value is None:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(value)
    ):
        raise ValueError("CMC market value must be finite")
    return value


def _required_data(payload: Any, expected: type[Any]) -> Any:
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), expected):
        raise ValueError("CMC response data is malformed")
    return payload["data"]


def _global_usd(data: dict[str, Any]) -> dict[str, Any]:
    quote = data.get("quote")
    if (
        not isinstance(quote, dict)
        or not isinstance(quote.get("USD"), dict)
        or not quote["USD"]
    ):
        raise ValueError("CMC global USD quote is malformed")
    return quote["USD"]


def _quote_usd(item: dict[str, Any]) -> dict[str, Any]:
    usd = item.get("quote", {}).get("USD", {})
    return {
        "price_usd": _finite_number(usd.get("price")),
        "market_cap_usd": _finite_number(usd.get("market_cap")),
        "volume_24h_usd": _finite_number(usd.get("volume_24h")),
        "percent_change_24h": _finite_number(usd.get("percent_change_24h")),
        "percent_change_7d": _finite_number(usd.get("percent_change_7d")),
        "last_updated": usd.get("last_updated"),
    }


def _listing_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "cmc_id": str(item["id"]),
        "name": item.get("name", ""),
        "symbol": item.get("symbol", ""),
        "cmc_rank": _finite_number(item.get("cmc_rank")),
        "circulating_supply": _finite_number(item.get("circulating_supply")),
        "total_supply": _finite_number(item.get("total_supply")),
        "max_supply": _finite_number(item.get("max_supply")),
        **_quote_usd(item),
    }


async def list_listings(
    client: httpx.AsyncClient, *, api_key: str, start: int, limit: int
) -> dict[str, Any]:
    """One page of the latest cryptocurrency listings, ranked by market cap.

    ``start`` is a 0-based offset (this package's own convention, matching
    ``ToolPreset(pagination="offset")``'s zero-based semantics) — translated
    to CMC's native 1-based ``start`` query parameter internally, so a caller
    never has to know CMC's API is 1-indexed.

    CMC's listings endpoint reports no reliable total count, so callers page
    until a page shorter than ``limit`` comes back (``total`` is always
    ``None`` here).
    """
    response = await client.get(
        "/v1/cryptocurrency/listings/latest",
        headers={"X-CMC_PRO_API_KEY": api_key},
        follow_redirects=False,
        params={"start": start + 1, "limit": limit, "convert": "USD"},
    )
    response.raise_for_status()
    payload = response.json()
    items = [_listing_record(item) for item in _required_data(payload, list)]
    return {"items": items, "offset": start, "limit": limit, "total": None}


async def get_quotes(
    client: httpx.AsyncClient, *, api_key: str, symbols: str
) -> dict[str, Any]:
    """Latest quote(s) for one or more comma-separated symbols (e.g. ``"BTC,ETH"``)."""
    response = await client.get(
        "/v1/cryptocurrency/quotes/latest",
        headers={"X-CMC_PRO_API_KEY": api_key},
        follow_redirects=False,
        params={"symbol": symbols, "convert": "USD"},
    )
    response.raise_for_status()
    payload = response.json()
    data = _required_data(payload, dict)
    items = []
    for symbol, entries in data.items():
        # CMC returns either one object or a list when a symbol maps to
        # several listed assets (rare ticker collisions).
        for item in entries if isinstance(entries, list) else [entries]:
            items.append({"symbol": symbol, **_listing_record(item)})
    return {"items": items, "offset": 0, "limit": len(items), "total": len(items)}


async def get_global_metrics(
    client: httpx.AsyncClient, *, api_key: str
) -> dict[str, Any]:
    """Aggregate market metrics: total market cap, BTC/ETH dominance, volume.

    A macro/liquidity gauge for the crypto market as a whole (EH-422) —
    distinct from any single asset's quote.
    """
    response = await client.get(
        "/v1/global-metrics/quotes/latest",
        headers={"X-CMC_PRO_API_KEY": api_key},
        follow_redirects=False,
        params={"convert": "USD"},
    )
    response.raise_for_status()
    payload = _required_data(response.json(), dict)
    usd = _global_usd(payload)
    return {
        "items": [
            {
                "id": "global",
                "active_cryptocurrencies": _finite_number(
                    payload.get("active_cryptocurrencies")
                ),
                "btc_dominance": _finite_number(payload.get("btc_dominance")),
                "eth_dominance": _finite_number(payload.get("eth_dominance")),
                "total_market_cap_usd": _finite_number(usd.get("total_market_cap")),
                "total_volume_24h_usd": _finite_number(usd.get("total_volume_24h")),
                "last_updated": usd.get("last_updated"),
            }
        ],
        "offset": 0,
        "limit": 1,
        "total": 1,
    }
