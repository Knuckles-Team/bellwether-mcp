---
name: bellwether-macro-series
skill_type: skill
description: >-
  Fed macro and liquidity series with point-in-time vintages via bellwether-mcp (FRED and ALFRED): series aliases, observations, revision dates and values as known on a past date. Use to read a macro series or rebuild what a backtest saw. Do NOT use for FOMC decisions (bellwether-fomc-calendar) or crypto data.
license: MIT
tags: [bellwether, fred, alfred, macro, vintage, mcp]
metadata:
  version: '0.1.0'
---

# Bellwether Macro Series

Scope: Fed macro and liquidity series with point-in-time vintages via the bellwether-mcp MCP server (FRED and ALFRED) - the shipped series aliases, observations of the latest revision or a pinned vintage, every revision date of a series, and observations as known on a past date. Use when the agent must read a macro series or reconstruct what a backtest would have seen. Do NOT use for the FOMC decision record (bellwether-fomc-calendar) or crypto data (bellwether-crypto-reference).

## Tools

| Tool | Purpose |
|------|---------|
| `fred_macro_series_aliases` | The named macro and liquidity series aliases the package ships. |
| `fred_series_observations` | Observations by `series_id` or `alias`; latest revision unless `realtime_start` and `realtime_end` pin a vintage. |
| `fred_series_vintage_dates` | Every date the series was revised or published. |
| `fred_series_observations_asof` | The series exactly as known on `vintage_date`, without look-ahead. |

## Workflow
1. Call `fred_macro_series_aliases` and prefer an alias to a raw series id.
2. For the current picture call `fred_series_observations` with a bounded `limit`.
3. For a past-date question call `fred_series_vintage_dates`, pick a date, then call `fred_series_observations_asof`.

## Steps
1. List the shipped aliases with `fred_macro_series_aliases`. Verify the series you need has an alias.
2. For the current picture call `fred_series_observations` with `alias` and a bounded `limit`. Verify observations are returned for the alias.
3. For a past-date question call `fred_series_vintage_dates`. Verify the date you want is on or after a listed vintage.
4. Read the series as of that date with `fred_series_observations_asof` and `vintage_date`. Verify the values differ from the latest revision only where the series was revised.

## Failure recovery
| Failure | Cause | Recovery |
|---------|-------|----------|
| Unknown alias refused | The alias is not shipped | Call `fred_macro_series_aliases` for valid names, or pass `series_id` to `fred_series_observations` |
| Credential error | The FRED key is not configured server-side | Report the gap and ask the operator to configure the key, then call `fred_series_observations` again |
| Backtest shows look-ahead values | `fred_series_observations` returned the latest revision | Redo the read with `fred_series_observations_asof` and a `vintage_date` |

## Gotchas
- The key is resolved server-side; never pass it as an argument.
- `fred_series_observations` returns the latest revision; using it for a backtest leaks revisions.
- An unknown alias is refused; pass `series_id` for any other FRED series.
