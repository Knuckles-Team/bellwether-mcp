"""FRED + ALFRED (point-in-time vintages): Fed macro and liquidity series (EH-412/EH-422).

https://fred.stlouisfed.org/docs/api/fred/series_observations.html
https://fred.stlouisfed.org/docs/api/fred/series_vintagedates.html

ALFRED is not a separate host or API — it is the *same* FRED REST API's
``realtime_start``/``realtime_end`` parameters on ``series/observations``,
which select "the data as it was known/published as of this date" instead of
today's latest revision. This client exposes that explicitly
(:func:`get_observations_asof`) rather than only ever returning today's
revised values, so a caller can reconstruct what a point-in-time backtest
would actually have seen (no look-ahead into later data revisions).
"""

from __future__ import annotations

from typing import Any

import httpx

__all__ = ["get_observations", "get_observations_asof", "get_vintage_dates"]


def _parse_observation_value(raw: Any) -> float | None:
    """FRED encodes a missing observation as the literal string ``"."``."""
    if raw is None or raw == ".":
        return None
    return float(raw)


def _observation_record(series_id: str, obs: dict[str, Any]) -> dict[str, Any]:
    realtime_start = obs.get("realtime_start", "")
    date = obs.get("date", "")
    return {
        # Unique within one call's vintage window; a single series_id+date can
        # recur across different realtime_start vintages, so the record
        # identity folds in the vintage too.
        "observation_id": f"{series_id}:{date}:{realtime_start}",
        "series_id": series_id,
        "date": date,
        "value": _parse_observation_value(obs.get("value")),
        "realtime_start": realtime_start,
        "realtime_end": obs.get("realtime_end", ""),
    }


async def get_observations(
    client: httpx.AsyncClient,
    *,
    api_key: str,
    series_id: str,
    offset: int = 0,
    limit: int = 1000,
    realtime_start: str | None = None,
    realtime_end: str | None = None,
) -> dict[str, Any]:
    """One page of a FRED series' observations, latest-revision by default.

    Pass ``realtime_start``/``realtime_end`` (``YYYY-MM-DD``) to pin the
    vintage instead of today's latest revision — see
    :func:`get_observations_asof` for the common "as of one date" case.
    """
    params: dict[str, Any] = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "offset": offset,
        "limit": limit,
        "sort_order": "asc",
    }
    if realtime_start:
        params["realtime_start"] = realtime_start
    if realtime_end:
        params["realtime_end"] = realtime_end
    response = await client.get("/series/observations", params=params)
    response.raise_for_status()
    payload = response.json()
    items = [
        _observation_record(series_id, obs) for obs in payload.get("observations", [])
    ]
    return {
        "items": items,
        "offset": offset,
        "limit": limit,
        "total": payload.get("count"),
    }


async def get_observations_asof(
    client: httpx.AsyncClient,
    *,
    api_key: str,
    series_id: str,
    vintage_date: str,
    offset: int = 0,
    limit: int = 1000,
) -> dict[str, Any]:
    """Point-in-time (ALFRED) observations: the series exactly as known on ``vintage_date``.

    A pure convenience over :func:`get_observations` pinning both
    ``realtime_start`` and ``realtime_end`` to the same date.
    """
    return await get_observations(
        client,
        api_key=api_key,
        series_id=series_id,
        offset=offset,
        limit=limit,
        realtime_start=vintage_date,
        realtime_end=vintage_date,
    )


async def get_vintage_dates(
    client: httpx.AsyncClient,
    *,
    api_key: str,
    series_id: str,
    offset: int = 0,
    limit: int = 1000,
) -> dict[str, Any]:
    """Every date this series' data was revised/published — the ALFRED vintage list.

    Feed any entry back into :func:`get_observations_asof` as ``vintage_date``
    to reconstruct that exact point-in-time view.
    """
    response = await client.get(
        "/series/vintagedates",
        params={
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "offset": offset,
            "limit": limit,
        },
    )
    response.raise_for_status()
    payload = response.json()
    dates = payload.get("vintage_dates", [])
    items = [
        {"vintage_id": f"{series_id}:{d}", "series_id": series_id, "vintage_date": d}
        for d in dates
    ]
    return {
        "items": items,
        "offset": offset,
        "limit": limit,
        "total": payload.get("count"),
    }
