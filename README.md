# bellwether-mcp

*Version: 1.3.6*

> **Documentation** — Installation, deployment, and tool usage are maintained in the
> [official documentation](https://knuckles-team.github.io/bellwether-mcp/).

Crypto discovery/rankings/market caps (CoinMarketCap), Fed macro and liquidity
series with point-in-time vintages (FRED/ALFRED), and the FOMC decision
calendar (hike/cut/hold, sourced) — as an MCP tool surface and, through
`agent-connector-sdk`'s declarative `mcp_tool` source adapter, as bounded,
checkpointed ingestion streams intended for EG's `finance-v1` world-model
ontology (`feat/finance-core`, not yet published — see AGENTS.md).

**Not a venue-specific OHLCV feed.** CoinMarketCap's general historical OHLCV
endpoint documents hourly/daily coverage only, not minute-level exchange
candles — pair this package with an `emerald-exchange` backend for tradable
bars and charts.

## Sources

| Ledger row | Sources | Target class (provisional) |
|---|---|---|
| EH-412 (crypto discovery/caps) | CoinMarketCap listings/quotes/global-metrics | `Instrument`, `MacroEvent` |
| EH-412 (Fed macro series) | FRED/ALFRED `series/observations`, `series/vintagedates` | `EconomicIndicator` |
| EH-412 (FOMC calendar) | Curated dataset, sourced to federalreserve.gov press releases | `MacroEvent` |
| EH-422 (macro/liquidity) | FRED named aliases: `WALCL`, `WDTGAL`, `M2SL`, `RRPONTSYD`, `WRESBAL`, `DGS10`, `DTWEXBGS` | `EconomicIndicator` |

`Instrument`, `EconomicIndicator` and `MacroEvent` are the design doc's own
proposed finance-v1 class names
(`plans/refactor/proposals/FINANCE-INTEGRATION-20260924.md` section 4/7).
EG's `feat/finance-core` branch, which owns finance-v1, has not published
anything yet as of this package's build — see AGENTS.md "Ontology mapping"
before trusting these as final.

## Tools

Nine MCP tools, one FastMCP server (`bellwether-mcp` console script):
`cmc_listings`, `cmc_quotes`, `cmc_global_metrics`, `fred_macro_series_aliases`,
`fred_series_observations`, `fred_series_observations_asof`,
`fred_series_vintage_dates`, `fomc_calendar_list`, `coinglass_macro_snapshot`.

Every tool is keyless except `cmc_*`, `fred_*` and `coinglass_*`, whose credentials are
resolved server-side through `agent_connector_sdk.credentials`
(`BELLWETHER_CMC_API_KEY`, `BELLWETHER_FRED_API_KEY`, `BELLWETHER_COINGLASS_API_KEY`) — never accepted as a
tool argument. `fomc_calendar_list` reads a packaged, curated, sourced dataset
and needs no credential and no network.

The CoinGlass source serves bounded Bitcoin ETF flows, fear-and-greed
observations and Hyperliquid whale positions. Configure the API key and give
each source an operator-owned license tag. The source does not establish
redistribution rights or claim complete history.

For a matched per-fund flow and AUM, configure the `coinglass_etf_fund_flows`
source with a Bitcoin ETF `ticker` and `license_tag`. It joins CoinGlass's
[daily flow history](https://docs.coinglass.com/reference/etf-flows-history)
with its [per-ticker AUM history](https://docs.coinglass.com/reference/etf-aum)
only when their timestamps match. Missing or conflicting AUM refuses the read.
Each record retains the capture time of each provider response.

See [`AGENTS.md`](AGENTS.md) for architecture, the ontology-mapping
authority, the FOMC dataset's provenance, rate limits, and commands.
