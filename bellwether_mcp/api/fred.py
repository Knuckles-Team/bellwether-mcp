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

from datetime import date
from math import isfinite
from typing import Any

import httpx

__all__ = ["get_observations", "get_observations_asof", "get_vintage_dates"]


def _parse_observation_value(raw: Any) -> float | None:
    """FRED encodes a missing observation as the literal string ``"."``."""
    if raw is None or raw == ".":
        return None
    return _finite_value(raw)


def _finite_value(raw: Any) -> float:
    value = float(raw)
    if not isfinite(value):
        raise ValueError("FRED observation value must be finite")
    return value


def _observation_page(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict) or not isinstance(
        payload.get("observations"), list
    ):
        raise ValueError("FRED observations page is malformed")
    observations = payload["observations"]
    if not all(isinstance(item, dict) for item in observations):
        raise ValueError("FRED observations page contains a non-object observation")
    return observations


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


def _require_realtime_date(value: str) -> str:
    """Refuse missing, malformed or noncanonical FRED vintage dates."""
    if not isinstance(value, str):
        raise ValueError("FRED realtime date must be YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("FRED realtime date must be YYYY-MM-DD") from exc
    if parsed.isoformat() != value:
        raise ValueError("FRED realtime date must be YYYY-MM-DD")
    return value


def _realtime_params(start: str | None, end: str | None) -> dict[str, str]:
    params = {}
    if start is not None:
        params["realtime_start"] = _require_realtime_date(start)
    if end is not None:
        params["realtime_end"] = _require_realtime_date(end)
    if start is not None and end is not None and start > end:
        raise ValueError("FRED realtime start must not exceed realtime end")
    return params


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
    params.update(_realtime_params(realtime_start, realtime_end))
    response = await client.get("/series/observations", params=params)
    response.raise_for_status()
    payload = response.json()
    items = [_observation_record(series_id, obs) for obs in _observation_page(payload)]
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
    vintage_date = _require_realtime_date(vintage_date)
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
