# CONN-BELLWETHER-MCP-HTTP — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

The package carried a copy of the minimum-interval limiter in `bellwether_mcp/http_clients.py`. The SDK now ships the same class as `scion_sdk.httpsupport.RateLimiter` (SDK 0.3.13). The copy is deleted. Each `_Endpoint` in `bellwether_mcp/mcp/clients.py` holds one governed client and one SDK limiter. The process shares one `Clients` instance, so the limiter paces all traffic to a host.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk, fastmcp
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest; the proof level each row names
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: one tool per API operation; shared capabilities come from the SDK
- **Scale/Scope**: 2 rows

## Constitution Check

- One owner per concept: pass. The connector owns one external system's calls, mappings and tools only.
- Connectors depend on the SDK and are called through arbora: pass.
- No ratchets: pass. The rows add no suppression.

## Project Structure

```text
bellwether_mcp/mcp/clients.py  existing
```

## Phase 0: Research

No unknowns. Each row names the code it touches.

## Phase 1: Design

### Interfaces and data model

No interface change. `RateLimiter(min_interval_seconds)` and `await limiter.wait()` keep their signatures.

### Live integration path

A tool calls `_Endpoint.paced_client()`. It awaits the SDK limiter and returns the governed client.

### Quality and release gates

Run `uv run pytest` and the repository pre-commit hooks.

### Risks, alternatives, and decisions

Decision: keep `build_async_client` local. It builds options from this connector's user agent and endpoint type.

### CoinMarketCap redirect boundary

Each keyed CoinMarketCap request sets redirect following to false. This holds
even when a caller injects a client that follows redirects by default. The
connector refuses the redirect before it sends the key to another host.

## Phase 2: Task approach

`tasks.md` holds one task line per row, producer first.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks apply: `ruff-format`, `connector-standard`, `secrets`, `tests-fast`. Each row names its proving test. No suppression and no duplicate implementation.

## Production caller chain

1. `CONN-BELLWETHER-MCP-HTTP-R001`: every vendor tool served by bellwether_mcp/mcp/server.py::build_server obtains its endpoint from bellwether_mcp/mcp/clients.py::Clients, whose _Endpoint.paced_client (line 41) awaits the SDK RateLimiter via limiter.wait before returning the client.
2. `CONN-BELLWETHER-MCP-HTTP-R002`: the cmc_listings, cmc_quotes and cmc_global_metrics tools in bellwether_mcp/mcp/tools_crypto_reference.py call list_listings (line 93), get_quotes (line 122) and get_global_metrics (line 145) in bellwether_mcp/api/coinmarketcap.py.

## Cross-repo seams

none. The cited owner rows are library capabilities the connector calls in process; spec.md names them.
