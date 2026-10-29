# CONN-BELLWETHER-MCP-HTTP — Outbound HTTP pacing

Owner: bellwether-mcp. Cross-repo IDs: `SCION-CENTRALIZED-CAPABILITIES-R005`.
Public provenance: SDK centralization audit of 2026-10-22, which found a copied request limiter in this connector.

## Purpose and user stories

A vendor API publishes a request budget. The connector must keep each host's calls at least the configured interval apart. The SDK owns the limiter, so the connector uses it and ships no copy.

## Requirements and acceptance

- FR-001: Each vendor endpoint paces its calls with the SDK `RateLimiter` at the endpoint's `min_interval_seconds`.
- SC-001: The package defines no `RateLimiter` class of its own.

## Why a new spec

Search: `specs/` held only `_template/`. No local spec owns outbound HTTP. The limiter contract is `SCION-CENTRALIZED-CAPABILITIES-R005`. This spec owns only the connector's use of it.

## Scope and interfaces

Owned behavior: the per-endpoint limiter in `bellwether_mcp/mcp/clients.py`. The governed client wrapper `build_async_client` stays in `bellwether_mcp/http_clients.py`. Non-goals: changing any endpoint interval.

## Traceability

| Requirement | Design section | Test ID | Evidence |
|---|---|---|---|
| FR-001 | plan.md Live integration path | T-001 |  |
| SC-001 | plan.md Existing system and reuse | T-002 |  |

## Open questions

None.
