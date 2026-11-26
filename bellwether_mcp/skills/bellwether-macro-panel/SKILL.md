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
3. Report the items from `coinglass_macro_snapshot` with their dataset and license tag.

## Steps
1. Choose the `dataset` argument: `etf`, `etf_fund_flows`, `sentiment` or `onchain`. Verify a `ticker` is set only for `etf_fund_flows`.
2. Call `coinglass_macro_snapshot` with the dataset, the operator-supplied `license_tag` and `mode` set to `delta`. Verify the response contains items.
3. Report the items from `coinglass_macro_snapshot` with their dataset and license tag. Verify every reported item carries both.

## Failure recovery
| Failure | Cause | Recovery |
|---------|-------|----------|
| Argument error on `ticker` | `etf_fund_flows` needs a ticker and the others refuse one | Resend `coinglass_macro_snapshot` with `ticker` only for `etf_fund_flows` |
| Credential error | The CoinGlass key is not configured server-side | Report the gap and ask the operator to configure the key, then call `coinglass_macro_snapshot` again |
| License tag missing | The operator did not supply one | Ask the operator for the `license_tag` before calling the tool |

## Gotchas
- The key is resolved server-side; a missing key is reported, not worked around.
- Read failures are reported without provider detail.
