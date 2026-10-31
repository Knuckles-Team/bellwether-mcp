"""Base URLs, contact info and rate-limit knobs for the market-data APIs.

Every value has a documented-limit-respecting default and is overridable
through :func:`scion_sdk.config.setting` so a deployment can point
at a mirror or tune throughput without a code change. Nothing here performs
I/O.
"""

from __future__ import annotations

import os
import warnings
from dataclasses import dataclass
from typing import Any

from scion_sdk.config import setting

#: Settings prefix. ``MARKET_DATA_`` (the name before the bellwether-mcp rename)
#: is still read, with a DeprecationWarning, for one release.
ENV_PREFIX = "BELLWETHER_"
DEPRECATED_ENV_PREFIX = "MARKET_DATA_"


def env_name(suffix: str) -> str:
    """The environment variable to read for ``suffix``, honoring the old prefix."""
    new, old = ENV_PREFIX + suffix, DEPRECATED_ENV_PREFIX + suffix
    if os.environ.get(new) is None and os.environ.get(old) is not None:
        warnings.warn(
            f"{old} is deprecated; set {new} instead (bellwether-mcp rename)",
            DeprecationWarning,
            stacklevel=3,
        )
        return old
    return new


def _setting(suffix: str, default: Any, **kwargs: Any) -> Any:
    return setting(env_name(suffix), default, **kwargs)


#: Contact identity every governed client advertises.
CONTACT_EMAIL = _setting("CONTACT_EMAIL", "connectors@knuckles.team")
USER_AGENT = _setting(
    "USER_AGENT",
    f"bellwether-mcp/0.1 (+mailto:{CONTACT_EMAIL})",
)


@dataclass(frozen=True)
class SourceEndpoint:
    """One vendor API's base URL and its documented request budget."""

    base_url: str
    #: Minimum seconds between requests this process issues to this host.
    min_interval_seconds: float
    #: Default page size, bounded by the vendor's own documented maximum.
    page_size: int


#: CoinMarketCap Pro API. Documented default plan limit: 30 req/min. Requires
#: an API key (``X-CMC_PRO_API_KEY`` header) on every endpoint, including the
#: free "Basic" tier — there is no keyless CMC endpoint.
#: https://coinmarketcap.com/api/documentation/pro-api-reference/cryptocurrency
COINMARKETCAP = SourceEndpoint(
    base_url=_setting("CMC_BASE_URL", "https://pro-api.coinmarketcap.com"),
    min_interval_seconds=_setting("CMC_MIN_INTERVAL", 2.0, cast=float),
    page_size=_setting("CMC_PAGE_SIZE", 100, cast=int),
)

#: FRED (Federal Reserve Economic Data) + its point-in-time twin ALFRED — the
#: same REST API; ALFRED's vintage behaviour is reached by passing
#: ``realtime_start``/``realtime_end`` (or ``vintage_dates``) on the same
#: endpoints, not a separate host. Documented limit: 120 req/min per key.
#: https://fred.stlouisfed.org/docs/api/fred/
FRED = SourceEndpoint(
    base_url=_setting("FRED_BASE_URL", "https://api.stlouisfed.org/fred"),
    min_interval_seconds=_setting("FRED_MIN_INTERVAL", 0.5, cast=float),
    page_size=_setting("FRED_PAGE_SIZE", 1000, cast=int),
)

#: FOMC meeting/decision calendar has no live JSON API (the Federal Reserve
#: publishes it as HTML pages: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
#: and per-meeting press releases at
#: https://www.federalreserve.gov/newsevents/pressreleases/monetary<YYYYMMDD>a.htm).
#: This connector ships a curated, versioned, per-record-sourced dataset
#: instead of scraping HTML at call time — see
#: ``bellwether_mcp/connectors/fomc_meetings.json`` and
#: ``bellwether_mcp/api/fomc_calendar.py`` for the sourcing/verification note.
FOMC_CALENDAR_SOURCE_URL = _setting(
    "FOMC_SOURCE_URL",
    "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
)

#: A named set of FRED series this package ships as ready-made "macro and
#: liquidity" presets (EH-422) — real, documented FRED series ids. Extend this
#: table (not the API client) to add another series; the client itself takes
#: any ``series_id`` a caller supplies, keyless-parameter-free.
#:
#: ``fed_balance_sheet``, ``treasury_general_account`` and
#: ``reverse_repo_overnight`` are the three ingredients of the commonly used
#: "Fed net liquidity" composite: ``WALCL - WDTGAL - RRPONTSYD`` (total assets
#: minus the Treasury's operating cash minus reverse-repo drains). This
#: package ships the three raw series only — computing and versioning the
#: composite as an ``IndicatorSpec`` is EG's job per the design doc's
#: ownership split (`plans/refactor/proposals/FINANCE-INTEGRATION-20260924.md`
#: section 4: "signals, indicators and backtests move to EG").
FRED_MACRO_SERIES: dict[str, str] = {
    # Federal Reserve balance sheet (H.4.1): total assets, weekly (Wednesday) level.
    "fed_balance_sheet": "WALCL",
    # U.S. Treasury General Account balance at the Fed, weekly (Wednesday) level.
    "treasury_general_account": "WDTGAL",
    # M2 money stock, monthly, seasonally adjusted.
    "m2_money_stock": "M2SL",
    # Overnight reverse repurchase agreements awarded to counterparties by the
    # Fed (a standard "excess liquidity draining" gauge).
    "reverse_repo_overnight": "RRPONTSYD",
    # Reserve balances depository institutions hold at Federal Reserve Banks.
    "bank_reserve_balances": "WRESBAL",
    # 10-Year Treasury Constant Maturity Rate, daily.
    "treasury_10y_yield": "DGS10",
    # Trade Weighted U.S. Dollar Index: Broad, Goods and Services — the closest
    # FRED-hosted proxy for the ICE "DXY" dollar index (DXY itself is not a
    # FRED series; document this distinction wherever the two are compared).
    "dollar_index_broad": "DTWEXBGS",
}
