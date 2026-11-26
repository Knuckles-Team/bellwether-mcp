---
name: bellwether-crypto-reference
skill_type: skill
description: >-
  Crypto market-cap reference data via bellwether-mcp (CoinMarketCap): ranked listings, quotes for symbols and global market metrics. Use to rank assets, quote symbols, or read total cap, dominance and 24h volume. Do NOT use for exchange bars, macro series (bellwether-macro-series) or ETF panels (bellwether-macro-panel).
license: MIT
tags: [bellwether, crypto, coinmarketcap, market-cap, mcp]
metadata:
  version: '0.1.0'
---

# Bellwether Crypto Reference

Scope: Crypto discovery and market-cap reference data via the bellwether-mcp MCP server - ranked listings, quotes for comma-separated symbols and aggregate market metrics from CoinMarketCap. Use when the agent must rank assets by market cap, quote symbols, or read total cap, dominance and 24h volume as a liquidity gauge. Do NOT use for tradable exchange bars (use an exchange connector), macro series (bellwether-macro-series) or on-chain and ETF panels (bellwether-macro-panel).

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

## Steps
1. Rank assets with `cmc_listings` (`start`, `limit`). Verify the response lists symbols ordered by market cap.
2. Quote the chosen symbols with `cmc_quotes` using a comma-separated list such as `BTC,ETH`. Verify each requested symbol has a quote in the result.
3. Read the market-wide gauge with `cmc_global_metrics`. Verify total market cap, dominance and 24h volume are present.
4. For incremental sweeps call `cmc_listings` with `mode` set to `delta` and the last page's `source_checkpoint`. Verify the result continues after that checkpoint.

## Failure recovery
| Failure | Cause | Recovery |
|---------|-------|----------|
| Credential resolution error | The CoinMarketCap key is not configured server-side | Report the gap and ask the operator to configure the key, then call `cmc_global_metrics` to confirm; do not estimate values |
| Missing symbol in quotes | Symbol misspelled or not listed | Call `cmc_listings` and copy the exact symbol from its output |
| Rate-limit error | Free-tier key limits request rate | Reduce `limit` in `cmc_listings`, and rerun the call after the client's paced interval |

## Gotchas
- These are discovery and cap figures, not venue-specific OHLCV bars.
- A missing key fails at credential resolution; report the gap, do not estimate values.
- Free-tier keys limit request rate; the client paces calls.
