# CONN-BELLWETHER-MCP-CMC-VALUES — CoinMarketCap market values

Owner: bellwether-mcp. Cross-repo IDs: `SCION-FINANCE-SOURCES-R001`.

## Purpose and user stories

Callers need usable market values and must not receive invalid numeric values.

## Why a new spec

The `cmc-paging` spec owns listing offsets. The `http` spec owns pacing and redirect boundaries. Neither owns market-value validation.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the SDK modules and the engine, which own the shared capabilities.

## User Scenarios & Testing

### User Story 1 - CoinMarketCap market values (Priority: P1)

Callers need usable market values and must not receive invalid numeric values.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-CMC-VALUES-R001` (finite market values) is exercised, **Then** `tests/test_api_coinmarketcap.py` checks served refusal and null preservation. Test: `tests/test_api_coinmarketcap.py::test_served_cmc_refuses_invalid_numeric_values`.
2. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-CMC-VALUES-R002` (response data shape) is exercised, **Then** `tests/test_api_coinmarketcap.py` exercises served refusal and valid empty collections. Test: `tests/test_api_coinmarketcap.py::test_served_cmc_refuses_missing_or_invalid_data`.
3. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-CMC-VALUES-R003` (provider identity) is exercised, **Then** `tests/test_api_coinmarketcap.py` covers served refusal for listings and quotes. Test: `tests/test_api_coinmarketcap.py::test_served_cmc_refuses_invalid_provider_identity`.

### Edge Cases

- If `CONN-BELLWETHER-MCP-CMC-VALUES-R001` is not met, its proving test fails: finite market values.
- If `CONN-BELLWETHER-MCP-CMC-VALUES-R002` is not met, its proving test fails: response data shape.
- If `CONN-BELLWETHER-MCP-CMC-VALUES-R003` is not met, its proving test fails: provider identity.

## Requirements

- **FR-001**: Finite market values. Rows: `CONN-BELLWETHER-MCP-CMC-VALUES-R001`.
- **FR-002**: Response data shape. Rows: `CONN-BELLWETHER-MCP-CMC-VALUES-R002`.
- **FR-003**: Provider identity. Rows: `CONN-BELLWETHER-MCP-CMC-VALUES-R003`.
- **FR-004**: Unique page identities. Rows: `CONN-BELLWETHER-MCP-CMC-VALUES-R004`.

## Success Criteria

- **SC-001**: `tests/test_api_coinmarketcap.py` checks served refusal and null preservation. Rows: `CONN-BELLWETHER-MCP-CMC-VALUES-R001`.
- **SC-002**: `tests/test_api_coinmarketcap.py` exercises served refusal and valid empty collections. Rows: `CONN-BELLWETHER-MCP-CMC-VALUES-R002`.
- **SC-003**: `tests/test_api_coinmarketcap.py` covers served refusal for listings and quotes. Rows: `CONN-BELLWETHER-MCP-CMC-VALUES-R003`.
- **SC-004**: `tests/test_api_coinmarketcap.py` exercises repeated IDs through both served tools. Rows: `CONN-BELLWETHER-MCP-CMC-VALUES-R004`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-BELLWETHER-MCP-CMC-VALUES-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-BELLWETHER-MCP-CMC-VALUES-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
| FR-003 | `CONN-BELLWETHER-MCP-CMC-VALUES-R003` | [plan.md](plan.md) | T-003 | [test-spec.md](test-spec.md) |
| FR-004 | `CONN-BELLWETHER-MCP-CMC-VALUES-R004` | [plan.md](plan.md) | T-004 | [test-spec.md](test-spec.md) |
