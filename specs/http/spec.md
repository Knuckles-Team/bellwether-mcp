# CONN-BELLWETHER-MCP-HTTP — Outbound HTTP pacing

Owner: bellwether-mcp. Cross-repo IDs: `SCION-CENTRALIZED-CAPABILITIES-R005`.
Public provenance: SDK centralization audit of 2026-10-22, which found a copied request limiter in this connector.

## Purpose and user stories

A vendor API publishes a request budget. The connector must keep each host's calls at least the configured interval apart. The SDK owns the limiter, so the connector uses it and ships no copy.

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

## User Scenarios & Testing

### User Story 1 - Outbound HTTP pacing (Priority: P1)

A vendor API publishes a request budget. The connector must keep each host's calls at least the configured interval apart. The SDK owns the limiter, so the connector uses it and ships no copy.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-HTTP-R001` (sdk request pacing) is exercised, **Then** `tests/test_sdk_rate_limiter.py::test_endpoint_limiter_is_the_sdk_limiter` and `tests/test_sdk_rate_limiter.py::test_package_ships_no_rate_limiter` pass.
2. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-HTTP-R002` (coinmarketcap keys never follow redirects) is exercised, **Then** `tests/test_api_coinmarketcap.py::test_api_key_is_not_forwarded_on_redirect` exercises listings, quotes and global metrics.

### Edge Cases

- If `CONN-BELLWETHER-MCP-HTTP-R001` is not met, its proving test fails: sdk request pacing.
- If `CONN-BELLWETHER-MCP-HTTP-R002` is not met, its proving test fails: coinmarketcap keys never follow redirects.

## Requirements

- **FR-001**: SDK request pacing. Rows: `CONN-BELLWETHER-MCP-HTTP-R001`.
- **FR-002**: CoinMarketCap keys never follow redirects. Rows: `CONN-BELLWETHER-MCP-HTTP-R002`.

## Success Criteria

- **SC-001**: `tests/test_sdk_rate_limiter.py::test_endpoint_limiter_is_the_sdk_limiter` and `tests/test_sdk_rate_limiter.py::test_package_ships_no_rate_limiter` pass. Rows: `CONN-BELLWETHER-MCP-HTTP-R001`.
- **SC-002**: `tests/test_api_coinmarketcap.py::test_api_key_is_not_forwarded_on_redirect` exercises listings, quotes and global metrics. Rows: `CONN-BELLWETHER-MCP-HTTP-R002`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-BELLWETHER-MCP-HTTP-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-BELLWETHER-MCP-HTTP-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
