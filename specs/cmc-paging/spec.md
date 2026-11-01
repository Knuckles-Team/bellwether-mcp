# CONN-BELLWETHER-MCP-CMC-PAGING — CoinMarketCap listing pagination

Owner: bellwether-mcp. Cross-repo IDs: `SCION-FINANCE-SOURCES-R001`.

## Purpose and user stories

A caller paging listings needs the default request to include the first provider record and subsequent offsets to advance consistently.

## Why a new spec

The `http` spec owns pacing and redirect boundaries; `connector-content` owns packaged content. Neither owns listing pagination.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the SDK modules and the engine, which own the shared capabilities.

## User Scenarios & Testing

### User Story 1 - CoinMarketCap listing pagination (Priority: P1)

A caller paging listings needs the default request to include the first provider record and subsequent offsets to advance consistently.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-CMC-PAGING-R001` (start listings at the first record) is exercised, **Then** `tests/test_api_coinmarketcap.py` exercises default and explicit offsets through the served MCP tool. Test: `tests/test_api_coinmarketcap.py::test_served_default_listings_start_at_first_provider_record`.
2. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-CMC-PAGING-R002` (sdk source paging) is exercised, **Then** `tests/test_api_coinmarketcap.py` extracts two served pages with the SDK transport and source adapter. Test: `tests/test_api_coinmarketcap.py::test_sdk_source_adapter_pages_served_cmc`.
3. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-CMC-PAGING-R003` (valid page bounds) is exercised, **Then** `tests/test_api_coinmarketcap.py` covers served refusal and direct client validation. Test: `tests/test_api_coinmarketcap.py::test_served_cmc_rejects_invalid_page_before_vendor_call`.

### Edge Cases

- If `CONN-BELLWETHER-MCP-CMC-PAGING-R001` is not met, its proving test fails: start listings at the first record.
- If `CONN-BELLWETHER-MCP-CMC-PAGING-R002` is not met, its proving test fails: sdk source paging.
- If `CONN-BELLWETHER-MCP-CMC-PAGING-R003` is not met, its proving test fails: valid page bounds.

## Requirements

- **FR-001**: Start listings at the first record. Rows: `CONN-BELLWETHER-MCP-CMC-PAGING-R001`.
- **FR-002**: SDK source paging. Rows: `CONN-BELLWETHER-MCP-CMC-PAGING-R002`.
- **FR-003**: Valid page bounds. Rows: `CONN-BELLWETHER-MCP-CMC-PAGING-R003`.

## Success Criteria

- **SC-001**: `tests/test_api_coinmarketcap.py` exercises default and explicit offsets through the served MCP tool. Rows: `CONN-BELLWETHER-MCP-CMC-PAGING-R001`.
- **SC-002**: `tests/test_api_coinmarketcap.py` extracts two served pages with the SDK transport and source adapter. Rows: `CONN-BELLWETHER-MCP-CMC-PAGING-R002`.
- **SC-003**: `tests/test_api_coinmarketcap.py` covers served refusal and direct client validation. Rows: `CONN-BELLWETHER-MCP-CMC-PAGING-R003`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-BELLWETHER-MCP-CMC-PAGING-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-BELLWETHER-MCP-CMC-PAGING-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
| FR-003 | `CONN-BELLWETHER-MCP-CMC-PAGING-R003` | [plan.md](plan.md) | T-003 | [test-spec.md](test-spec.md) |
