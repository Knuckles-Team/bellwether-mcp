# bellwether-mcp

Crypto discovery/caps (**CoinMarketCap**), Fed macro and liquidity series with
point-in-time vintages (**FRED/ALFRED**), and the FOMC decision calendar
(hike/cut/hold, sourced) as an **MCP Server** for the agent-utilities
ecosystem — a typed, deterministic tool surface plus `agent-connector-sdk`
declarative source-adapter presets.

!!! info "Official documentation"
    This site is the canonical reference for `bellwether-mcp`, maintained alongside
    every release.

[![PyPI](https://img.shields.io/pypi/v/bellwether-mcp)](https://pypi.org/project/bellwether-mcp/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/bellwether-mcp)](https://github.com/Knuckles-Team/bellwether-mcp/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/bellwether-mcp)

## Overview

`bellwether-mcp` wraps three keyless-by-default data sources with eight
consolidated MCP tools:

- **CoinMarketCap** — cryptocurrency discovery, rankings and market caps.
  **Not** a venue-specific OHLCV feed; pair with an `emerald-exchange` backend
  for tradable bars.
- **FRED / ALFRED** — Federal Reserve macro and liquidity series, including
  point-in-time ("as of") vintages via the same REST API's
  `realtime_start`/`realtime_end` parameters.
- **FOMC decision calendar** — a curated, sourced dataset (the Fed publishes
  no JSON API for this), covering every regularly scheduled meeting with a
  hike/cut/hold outcome, basis-point change, and resulting target range.

Every tool other than `fomc_calendar_list` requires a server-side-resolved
credential (`BELLWETHER_CMC_API_KEY` / `BELLWETHER_FRED_API_KEY`) — never
accepted as a tool argument. This package ships **no A2A agent**: unlike most
fleet packages it is built directly on `agent-connector-sdk` (not
`agent-utilities`) — see [Overview](overview.md) for why.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-start: **[Installation](installation.md)** — pip, source, and the prebuilt Docker image.
- :material-server-network: **[Deployment](deployment.md)** — run the MCP server, Docker Compose, Caddy + Technitium.
- :material-console: **[Usage](usage.md)** — the eight MCP tools and the declarative source adapters.
- :material-sitemap: **[Architecture](overview.md)** — the agent-connector-sdk pattern and MCP configuration.
- :material-tag-multiple: **[Concepts](concepts.md)** — the design-doc ontology mapping this connector targets.

</div>

## Quick start

```bash
pip install bellwether-mcp
export BELLWETHER_CMC_API_KEY=your_coinmarketcap_key
export BELLWETHER_FRED_API_KEY=your_fred_key
bellwether-mcp                    # stdio MCP server (default transport)
```

See **[Installation](installation.md)** and **[Deployment](deployment.md)** for the
full matrix (the Docker image, HTTP transports, reverse proxy, DNS).
