---
name: bellwether-fomc-calendar
skill_type: skill
description: >-
  The FOMC decision calendar via the bellwether-mcp MCP server - sourced
  hike, cut and hold records with date, target range and the Federal Reserve
  press-release URL, filtered by date range or outcome. Use when the agent must
  state what the FOMC decided on or between dates. Do NOT use for rate series
  values (bellwether-macro-series).
license: MIT
tags: [bellwether, fomc, calendar, rates, mcp]
metadata:
  version: '0.1.0'
---

# Bellwether FOMC Calendar

## Tools

| Tool | Purpose |
|------|---------|
| `fomc_calendar_list` | FOMC decisions filtered by `since`, `until` and `outcome`, paged by `offset` and `limit`. |

## Workflow
1. Call `fomc_calendar_list` with an ISO date range and optional `outcome` of hike, cut or hold.
2. Report each decision with its `source_url`.

## Gotchas
- The dataset is packaged and curated; it needs no key and asserts only what the source states.
- Dates are inclusive ISO `decision_date` bounds.
