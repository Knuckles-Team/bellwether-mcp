# CONN-BELLWETHER-MCP-CMC-VALUES — CoinMarketCap market values

Owner: bellwether-mcp. Cross-repo IDs: `SDK-FINANCE-SOURCES-R001`.

## Purpose and user stories

Callers need usable market values and must not receive invalid numeric values.

## Requirements and acceptance

See [requirements.md](requirements.md).

## Why a new spec

The `cmc-paging` spec owns listing offsets. The `http` spec owns pacing and redirect boundaries. Neither owns market-value validation.
