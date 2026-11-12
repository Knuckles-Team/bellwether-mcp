---
name: bellwether-crypto-reference
skill_type: skill
description: >-
  Crypto discovery and market-cap reference data via the bellwether-mcp MCP
  server - ranked listings, quotes for comma-separated symbols and aggregate
  market metrics from CoinMarketCap. Use when the agent must rank assets by
  market cap, quote symbols, or read total cap, dominance and 24h volume as a
  liquidity gauge. Do NOT use for tradable exchange bars (use an exchange
  connector), macro series (bellwether-macro-series) or on-chain and ETF panels
  (bellwether-macro-panel).
license: MIT
tags: [bellwether, crypto, coinmarketcap, market-cap, mcp]
metadata:
  version: '0.1.0'
---

# Bellwether Crypto Reference

Discovery and caps data for the crypto market. The API key is resolved server-side and is never a tool argument.

## Tools

| Tool | Purpose |
|------|---------|
| `cmc_listings` | Latest listings ranked by market cap; page with `start` and `limit`. |
| `cmc_quotes` | Latest quotes for comma-separated symbols such as `BTC,ETH`. |
| `cmc_global_metrics` | Total market cap, BTC and ETH dominance and 24h volume. |

## Workflow
1. Rank with `cmc_listings` when the asset is not known; keep the symbol it returns.
2. Quote the symbols with `cmc_quotes`.
3. Read `cmc_global_metrics` for a market-wide liquidity gauge.
4. For incremental sweeps pass `mode` `delta` with the `source_checkpoint` of the last page.

## Gotchas
- These are discovery and cap figures, not venue-specific OHLCV bars.
- A missing key fails at credential resolution; report the gap, do not estimate values.
- Free-tier keys limit request rate; the client paces calls.
