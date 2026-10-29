# CONN-BELLWETHER-MCP-CMC-PAGING — CoinMarketCap listing pagination

Owner: bellwether-mcp. Cross-repo IDs: `SCION-FINANCE-SOURCES-R001`.

## Purpose and user stories

A caller paging listings needs the default request to include the first provider record and subsequent offsets to advance consistently.

## Requirements and acceptance

See [requirements.md](requirements.md).

## Why a new spec

The `http` spec owns pacing and redirect boundaries; `connector-content` owns packaged content. Neither owns listing pagination.
