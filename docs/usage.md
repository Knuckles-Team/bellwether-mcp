# Usage — MCP tools and source adapters

`bellwether-mcp` exposes its data two ways: as **MCP tools** an agent calls
directly, and as **declarative `agent-connector-sdk` source adapters** a
deployment's runner drives on a schedule for continuous knowledge-graph
ingestion. The architecture is covered in [Overview](overview.md).

## As an MCP server

Once [deployed](deployment.md), the server registers eight tools:

| Tool | Source | Covers |
|---|---|---|
| `cmc_listings` | CoinMarketCap | Latest cryptocurrency listings ranked by market cap (paged) |
| `cmc_quotes` | CoinMarketCap | Latest quote(s) for comma-separated symbols, e.g. `"BTC,ETH"` |
| `cmc_global_metrics` | CoinMarketCap | Aggregate market metrics: total cap, BTC/ETH dominance, 24h volume |
| `fred_macro_series_aliases` | FRED | The named macro/liquidity series aliases (`fed_balance_sheet`, `m2_money_stock`, …) |
| `fred_series_observations` | FRED | One page of any FRED series' observations, latest revision |
| `fred_series_observations_asof` | FRED/ALFRED | Point-in-time observations as known on a given vintage date |
| `fred_series_vintage_dates` | FRED/ALFRED | Every date a series' data was revised/published |
| `fomc_calendar_list` | Curated dataset | Sourced FOMC decision records, filterable by date range/outcome |

Example agent prompts that map onto these tools:

- *"List the top 10 cryptocurrencies by market cap"* → `cmc_listings` with `limit=10`
- *"What's the Fed's balance sheet trend?"* → `fred_series_observations` with the `fed_balance_sheet` alias
- *"What did the FOMC do at its last three meetings?"* → `fomc_calendar_list` with `limit=3`

Every tool other than `fomc_calendar_list` resolves its API key server-side
(`BELLWETHER_CMC_API_KEY` / `BELLWETHER_FRED_API_KEY`) — never accept or pass
a credential as a tool argument.

## As declarative source adapters

`bellwether_mcp.connectors.adapters.build_source_adapters()` returns one
`McpToolSourceAdapter` per stream declared in `connectors/mcp_source_presets.json`
(ten streams: three CoinMarketCap, seven FRED macro-series aliases, plus
`fomc_calendar`). Each preset pins:

- the MCP tool it extracts (`tool`),
- the record/id/title fields (`records_path`, `id_field`, `title_field`),
- pagination (`pagination`, `page_param`, `page_size_param`, `page_size`),
- and the provisional ontology target (`ontology_class`: `Instrument`,
  `EconomicIndicator`, or `MacroEvent` — see `AGENTS.md` "Ontology mapping").

Adding a new FRED macro series means adding an alias to
`config.FRED_MACRO_SERIES` plus one preset entry — never a new API client or
MCP tool (RF-ADR-009 §2.2.1: "a new API source is a preset, not code").
Wiring these adapters to a live sink/schedule is a deployment-layer concern
(`agent_connector_sdk.runner`), not something this package does itself.

## As a Python API

The vendor clients are plain async functions taking an `httpx.AsyncClient` and
explicit credentials — never building their own client or reading the
environment directly:

```python
import asyncio
from bellwether_mcp.api import coinmarketcap
from bellwether_mcp.credentials import resolve_cmc_api_key
from bellwether_mcp.mcp.clients import Clients

async def main():
    clients = Clients()
    client = await clients.coinmarketcap.paced_client()
    listings = await coinmarketcap.list_listings(
        client, api_key=resolve_cmc_api_key(), start=0, limit=10
    )
    print(listings["items"])
    await clients.aclose()

asyncio.run(main())
```

`bellwether_mcp.api.fomc_calendar.list_meetings()` needs no client or
credential at all — it reads the packaged, curated dataset synchronously.
