---
name: bellwether-macro-panel
skill_type: skill
description: >-
  Crypto ETF, ETF fund-flow, sentiment and on-chain snapshots via the
  bellwether-mcp MCP server (CoinGlass). Use when the agent must read a bounded
  macro-panel dataset with the operator-supplied license tag. Do NOT use for
  rankings and quotes (bellwether-crypto-reference) or Fed series
  (bellwether-macro-series).
license: MIT
tags: [bellwether, coinglass, etf, onchain, sentiment, mcp]
metadata:
  version: '0.1.0'
---

# Bellwether Macro Panel

## Tools

| Tool | Purpose |
|------|---------|
| `coinglass_macro_snapshot` | A bounded snapshot of `etf`, `etf_fund_flows`, `sentiment` or `onchain` data. |

## Workflow
1. Choose the `dataset`; `etf_fund_flows` requires a `ticker`, the others refuse one.
2. Pass the `license_tag` the operator supplies and `mode` `delta`.
3. Report the items with their dataset and license tag.

## Gotchas
- The key is resolved server-side; a missing key is reported, not worked around.
- Read failures are reported without provider detail.
