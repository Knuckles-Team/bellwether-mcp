# Concept Registry — bellwether-mcp

> **Prefix**: none allocated — this package carries no local `CONCEPT:*` tags.
> **Bridge**: the design doc `plans/refactor/proposals/FINANCE-INTEGRATION-20260924.md`
> (section 4/7) — the source of the provisional finance-v1 class names below.

---

## Ontology targets (provisional)

This connector maps its ten declared streams onto EG's `finance-v1` ontology,
which is being built in parallel on branch `feat/finance-core` and had
published nothing as of this package's build. Until it does, each stream
targets the design doc's own proposed class name — see
`ontology/mappings/source.yaml` for the full, authoritative table and its
provenance note.

| Stream family | Target class (provisional) |
|---|---|
| CoinMarketCap listings/quotes | `Instrument` |
| CoinMarketCap global metrics | `MacroEvent` |
| FRED macro-series observations | `EconomicIndicator` |
| FOMC decision calendar | `MacroEvent` |

`EconomicIndicator` already exists in EG (`energy_geopolitics-v1.ttl:45`); the
others are finance-v1 proposals, not yet landed.

## This connector's own ontology

`bellwether_mcp/ontology/market_data.ttl` declares exactly one class,
`MarketDataSyncRun` — this connector's own sync-lifecycle bookkeeping record
(federated into the agent-utilities knowledge-graph hub). It does **not**
redeclare the finance-v1 domain classes above.

## Cross-project references

This project is built on `scion-sdk`, not `agent-utilities` — see
[Overview](overview.md) "Why scion-sdk". It therefore inherits no
`agent-utilities` 5-Pillar concepts and registers none of its own; when
`feat/finance-core` publishes real class/property names, this page and
`ontology/mappings/source.yaml` need a rename pass, not a redesign.
