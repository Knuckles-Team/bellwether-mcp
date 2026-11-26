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

## Steps
1. Call `fomc_calendar_list` with ISO `since` and `until` bounds. Verify each returned record has a `decision_date` inside the bounds.
2. Narrow by `outcome` set to hike, cut or hold when the question asks for one kind. Verify every record carries that outcome.
3. Page with `offset` and `limit` when the range is large. Verify the page count covers the whole range before concluding.
4. Report each decision with its `source_url`. Verify every reported decision has a URL from the result.

## Failure recovery
| Failure | Cause | Recovery |
|---------|-------|----------|
| Empty result | The date range has no meeting or the bounds are swapped | Widen `since` and `until` with `fomc_calendar_list` and check `since` is the earlier date |
| Outcome filter rejected | Value is not hike, cut or hold | Resend `fomc_calendar_list` with one of those three values |
| Missing recent decision | The packaged dataset is curated and may lag | State only what the source returns and do not infer a decision |

## Gotchas
- The dataset is packaged and curated; it needs no key and asserts only what the source states.
- Dates are inclusive ISO `decision_date` bounds.
