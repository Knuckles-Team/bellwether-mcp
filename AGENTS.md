# market-data-mcp - AGENTS

> Claude Code loads this file via `CLAUDE.md` (`@AGENTS.md` import) — the two stay
> in sync. Edit **this** file, not `CLAUDE.md`.

## Project structure
- `market_data_mcp/api/`: thin async vendor API clients (CoinMarketCap, FRED) plus
  `fomc_calendar.py` (a pure reader over a curated dataset, no network) — pure
  functions, no MCP/adapter concerns.
- `market_data_mcp/mcp/`: the eight-tool FastMCP surface + `clients.py` (shared,
  rate-limited governed HTTP clients for the two keyed sources) + `server.py`
  (composition root).
- `market_data_mcp/connectors/`: `mcp_source_presets.json` (10 declarative
  `agent-connector-sdk` `mcp_tool` presets), `fomc_meetings.json` (the curated,
  sourced FOMC dataset), `tool_schema_fingerprints.json` (generated — see below),
  and `adapters.py` (the runtime `SourceAdapter` factory).
- `market_data_mcp/ontology/`: this connector's OWN admin-lifecycle ontology
  (`market_data.ttl`, `MarketDataSyncRun`) plus `mappings/source.yaml` (the
  PROVISIONAL stream-to-finance-v1-class mapping — read before touching presets).
- `tests/`: API-layer tests against recorded/synthetic fixtures, a FOMC-dataset
  integrity suite, a preset/adapter wiring regression test, and a startup smoke test.
- `scripts/compute_tool_fingerprints.py`: regenerates `tool_schema_fingerprints.json`
  from the live `tools/list` schema — run after any tool signature/docstring change.

## Tech stack
- Python 3.12+, `agent-connector-sdk` (not `agent-utilities`, not `epistemic-graph`
  directly — see "Why agent-connector-sdk" below), FastMCP, httpx.

## Commands
- `PYTHONPATH=. <agent-connector-sdk venv>/bin/python3 -m pytest -q`: run tests
  (this package has no resolvable standalone `uv sync` yet — see "Known environment
  gap" below; borrow the SDK's own venv, which already carries `agent_connector_sdk`,
  `epistemic_graph` and `fastmcp`).
- `... -m mypy market_data_mcp --ignore-missing-imports --check-untyped-defs`
- `uvx ruff@0.16.0 check market_data_mcp tests scripts` /
  `uvx ruff@0.16.0 format market_data_mcp tests scripts`
- `pre-commit run kiss-staged|complexity-staged|dupehound-changed --files <paths>`

## Why agent-connector-sdk, not the legacy AU client-reflection pattern
Modeled directly on `agents/world-reference-mcp` (the first package on this SDK
architecture) per the lane's explicit direction to build "one package with pluggable
source presets" rather than one bespoke package per API:

- **Ports, not ad hoc code.** Every one of this connector's 10 streams is one
  `agent_connector_sdk.manifest.presets.ToolPreset` entry in
  `connectors/mcp_source_presets.json`, extracted by the SDK's own generic
  `agent_connector_sdk.adapters.mcp_tool.McpToolSourceAdapter` — RF-ADR-009 §2.2.1:
  "a new API source is a preset, not code." Adding an eighth FRED macro series means
  adding a `FRED_MACRO_SERIES` alias in `config.py` plus a preset entry — never a new
  API client or MCP tool.
- **No direct EG dependency.** This package depends on `agent-connector-sdk` only. It
  never builds its own EG client and never writes a `kg_ingest.py`-style
  direct-to-graph tool. Delivery to a live graph is entirely the SDK's
  `agent_connector_sdk.runner`/`sinks` job, wired at deployment time from
  `connectors.adapters.build_source_adapters()`.

## Ontology mapping (read before touching `mcp_source_presets.json`)
**PROVISIONAL — read `ontology/mappings/source.yaml` in full before relying on this.**
EG's `finance-v1` ontology is being built in parallel on branch `feat/finance-core`
(`plans/refactor/proposals/FINANCE-INTEGRATION-20260924.md` section 4 proposes
`Instrument`, `Listing`, `Venue`, `BarSeries`, `IndicatorSpec`, `SignalState`,
`TrendFlip`, `MacroEvent`). As of this package's build (2026-09-24), that branch has
published nothing this lane can read against — `/var/tmp/l9/finish/finance-core/`
is empty and the EG worktree `epistemic-graph/eg-finance` is stale at the train-3
tip (it carries the pre-existing `FinanceEwma`/`FinanceMomentum` stateless kernels,
not a new TBox). This package therefore maps its streams onto the design doc's own
proposed names as the best available authority (`Instrument`, `MacroEvent`; plus
`EconomicIndicator`, which is an EG class that **already exists**,
`energy_geopolitics-v1.ttl:45`, not a new finance-v1 one).

**When `feat/finance-core` publishes its actual names, this needs a rename pass, not
a redesign** — the stream-to-concept assignments should not change, only the exact
class/property spelling. Update `connectors/mcp_source_presets.json`'s
`ontology_class` fields and `ontology/mappings/source.yaml` together; `adapters.py`'s
`build_schema_mappings()` reads the preset file, so no code change is needed for a
pure rename.

`adapters.py` is the real authority; `connector_manifest.yml`'s crosswalk (once
generated) is advisory — see `world-reference-mcp/AGENTS.md`'s identical note for why
(AU's hub-class crosswalk predates brand-new EG classes on every sibling's first pass).

## FOMC dataset provenance (read before trusting `fomc_meetings.json`)
The Federal Reserve does not publish its meeting calendar or decisions as a JSON
API — only as HTML (`https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm`)
and one press-release page per meeting
(`https://www.federalreserve.gov/newsevents/pressreleases/monetary<YYYYMMDD>a.htm`).
`connectors/fomc_meetings.json` is therefore a **curated, hand-checked dataset**,
not a live scrape.

- **Coverage:** every regularly scheduled FOMC meeting from 2023-01 (the first meeting
  after the design doc's `plans/finance/recommended_plan.md` reference period) through
  2026-03, 18 records.
- **How it was checked:** cross-checked via web search against federalreserve.gov
  press releases, FOMC minutes, and independent recaps (CNBC, Chase/J.P. Morgan) on
  2026-09-24 — dates, hike/cut/hold direction, basis-point size and resulting target
  range for every record were checked against at least one primary or near-primary
  source before being written. This is NOT a substitute for reading the Fed's own
  page; it is a best-effort curation pass, and every record carries the Fed's own
  `source_url` so a caller can check independently.
- **Known limitation of the `source_url` convention:** the URL is constructed from
  the standard `monetary<YYYYMMDD>a.htm` pattern using each meeting's second
  (decision) day — one record (2026-01-28) was independently observed on
  federalreserve.gov to actually use a `monetary20260128a1.htm` variant (an
  extra `1` suffix); if any other record's real URL differs from the constructed
  pattern, the pattern is documented here as a best-effort convention, not a
  guarantee — confirm the exact URL against `fomccalendars.htm` before publishing a
  claim sourced to it.
- **How to extend:** add a new object to the `meetings` array in
  `connectors/fomc_meetings.json` (oldest-first; `test_dataset_is_chronologically_ordered_with_no_duplicate_decision_dates`
  enforces ordering) with a real `source_url`, then re-run the test suite —
  `test_api_fomc_calendar.py` checks internal consistency (outcome/bps_change sign,
  target-range width, sourced URL) on every record, so a malformed addition fails
  loud.
- **This package makes no claim about future meetings** — it is not a forecast, and
  `fomc_calendar_list` returns only what is in the dataset.

## Credentials
Two of eight tools need a credential, resolved server-side through
`agent_connector_sdk.credentials` — never accepted as a tool argument:
- `cmc_listings`, `cmc_quotes`, `cmc_global_metrics`: `MARKET_DATA_CMC_API_KEY`
  (`env://` by default) — CoinMarketCap has **no keyless endpoint**, including its
  free "Basic" plan.
- `fred_series_observations`, `fred_series_observations_asof`,
  `fred_series_vintage_dates`: `MARKET_DATA_FRED_API_KEY` (`env://` by default).

Both accept an `openbao://apps/market-data-mcp#<FIELD>` reference in the same
environment variable instead, resolved through
`agent_connector_sdk.credentials.resolver.CompositeCredentialResolver` at the
deployment composition root (`market_data_mcp.credentials.default_resolver` wires
only the `env://` scheme; a deployment adds an OpenBao resolver).

`fomc_calendar_list` is keyless and needs no network — it reads packaged data.

## Rate limits
CoinMarketCap and FRED are each called through `market_data_mcp.mcp.clients.Clients`,
one governed `httpx.AsyncClient` (TLS, bounded timeout, retry/backoff —
`agent_connector_sdk.http`) plus one `RateLimiter` (a cooperative minimum-interval
sleeper) per host, sized to each API's documented budget in `config.py`'s per-source
comments (CMC: 30 req/min on the Basic plan; FRED: 120 req/min per key).
`USER_AGENT` identifies this connector with a contact address.

## Macro/liquidity series (EH-422)
`config.FRED_MACRO_SERIES` names seven real, documented FRED series: `WALCL` (Fed
balance sheet), `WDTGAL` (Treasury General Account), `M2SL` (M2), `RRPONTSYD`
(overnight reverse repo), `WRESBAL` (bank reserve balances), `DGS10` (10Y yield), and
`DTWEXBGS` (the closest FRED-hosted proxy for the ICE "DXY" dollar index — DXY itself
is not a FRED series; do not conflate the two without noting the substitution).
`WALCL`, `WDTGAL` and `RRPONTSYD` are the three ingredients of the commonly used "Fed
net liquidity" composite (`WALCL - WDTGAL - RRPONTSYD`) — this package ships the raw
series only; computing and versioning the composite as an `IndicatorSpec` is EG's job
per the design doc's ownership split (finance-v1's signals/indicators live in EG,
not in a fleet connector).

**ETF flows:** `fred_series_observations` accepts ANY `series_id`, not only the named
aliases — including a Z.1 Financial Accounts flow-of-funds series once a deployer
identifies the exact series id for their asset scope on FRED's own site. This package
does not hardcode a specific "ETF flow" series id: `plans/finance/recommended_plan.md`
line 94 explicitly flags ETF flows as needing "a separately qualified" source (API
availability, definitions, cost, coverage), a vetting step out of this connector's
scope to perform unverified. This is a documented, deliberate gap, not a claim of
coverage this package does not have.

## Known environment gap: `uv sync` does not resolve standalone
Same gap as `world-reference-mcp` (see its `AGENTS.md`): `agent-connector-sdk`'s
`pyproject.toml` currently declares `epistemic-graph>=2.27.0,<3`, but the index this
workspace's `uv sync` consults only has `epistemic-graph<=2.23.0` — a pre-existing
SDK-side packaging gap, not this package's to fix; not touched here. All commands
above instead borrow `agent-connector-sdk`'s own canonical `.venv`
(`agent-connector-sdk/.venv`, which does carry `agent_connector_sdk`, `fastmcp` and
`httpx`) via `PYTHONPATH`.

## Not yet built (see WRAPUP.md for the full EH-412/EH-422 disposition)
- `agent_utilities.*` skill/ontology/prompt/source_connector_providers entry points
  are declared in `pyproject.toml` but the `skills/`, `prompts/`, `ontology/`
  federation registration (`REGISTERED_FEDERATED_IRIS`, `ontology.lock`) is deferred
  to the orchestrator's fleet registration pass — see `REGISTRATION.patch.md`.
- `agent_connector_sdk.source_adapters` entry-point group / `runner` composition
  (which sink/schedule actually drives `connectors.adapters.build_source_adapters()`
  in a live deployment) is not wired — this package provides the factory; runner
  composition is deployment-layer work, out of this lane's scope.
- A curated Z.1 "ETF flows" FRED series id (see "Macro/liquidity series" above) — a
  deliberate gap, not an oversight.
- CoinMarketCap's historical OHLCV endpoint is not wrapped — CMC is scoped to
  discovery/caps only per the design doc; venue OHLCV stays with emerald-exchange.
- `connector_manifest.yml` cannot be generated yet: `generate_connector_manifests.py`
  fail-closes with `FleetRegistryError: provider is not registered in the MCP fleet
  registry` — `market-data-mcp` (like `world-reference-mcp`) is not one of the 72
  entries in `mcp-fleet.registry.yml`. This is the same deferred fleet-registration
  pass named above, not a bug in the generator; do not hand-write the manifest to
  route around it.
- `auth.py` and `agent_server.py` are deliberately not added, matching the fleet
  template's exception path this package already documented above ("Why
  agent-connector-sdk"): there is no single backend session to authenticate
  against (`credentials.py` already resolves both keyed sources), and an
  `agent_server.py` will require an `agent_utilities` import this package's
  architecture explicitly rules out. `world-reference-mcp` — the other package on
  this architecture — reached the identical conclusion.

## Quality bar
Run `uvx ruff@0.16.0 check/format`, mypy, pytest and
`pre-commit run kiss-staged/complexity-staged/dupehound-changed --files <changed>`
before committing. Do not silence a check to force green.

## Specs: extend first

Find the spec row that owns the behavior before any code change. Search with `git grep -n "<term>" -- specs`. Cite the row ID in the commit `Spec:` trailer. Extend the owning spec before any new spec text. Add a child row, a new rollup, or a dated `plan.md` "Amendments" entry. Create a new spec only for a capability that no spec owns. Audits, reviews, and carry-overs land in the owning spec. They never get a spec directory. Reuse an existing function, module, or store before adding one. The rules are the ecosystem [spec standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/spec-standard.md).
