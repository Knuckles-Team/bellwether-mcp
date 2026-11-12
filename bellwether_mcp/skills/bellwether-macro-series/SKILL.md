---
name: bellwether-macro-series
skill_type: skill
description: >-
  Fed macro and liquidity series with point-in-time vintages via the
  bellwether-mcp MCP server (FRED and ALFRED) - the shipped series aliases,
  observations of the latest revision or a pinned vintage, every revision date
  of a series, and observations as known on a past date. Use when the agent
  must read a macro series or reconstruct what a backtest would have seen. Do
  NOT use for the FOMC decision record (bellwether-fomc-calendar) or crypto data
  (bellwether-crypto-reference).
license: MIT
tags: [bellwether, fred, alfred, macro, vintage, mcp]
metadata:
  version: '0.1.0'
---

# Bellwether Macro Series

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

## Gotchas
- The key is resolved server-side; never pass it as an argument.
- `fred_series_observations` returns the latest revision; using it for a backtest leaks revisions.
- An unknown alias is refused; pass `series_id` for any other FRED series.
