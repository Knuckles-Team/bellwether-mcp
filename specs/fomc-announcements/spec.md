# CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS — Sourced decision times

Owner: bellwether-mcp. Cross-repo ID: SCION-FINANCE-SOURCES-R001.

## Purpose and scope

Consumers of the curated FOMC decision calendar need each decision's actual announcement time and a Federal Reserve source. This covers the existing historical dataset, not future schedules or vintage history.

## Why a new spec

The connector-content spec covers packaged resources and the http spec covers transport; neither owns FOMC decision records.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the SDK modules and the engine, which own the shared capabilities.

## User Scenarios & Testing

### User Story 1 - Sourced decision times (Priority: P1)

Consumers of the curated FOMC decision calendar need each decision's actual announcement time and a Federal Reserve source. This covers the existing historical dataset, not future schedules or vintage history.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R001` (historical release time) is exercised, **Then** `tests/test_api_fomc_calendar.py` checks UTC timestamps, representative standard and daylight time releases, the corrected January 2026 source, and the returned record. Test: `tests/test_api_fomc_calendar.py::test_returned_announcement_times_match_sourced_release_dates`.
2. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R002` (declared sdk source) is exercised, **Then** `tests/test_api_fomc_calendar.py` extracts the served source through the SDK transport. Test: `tests/test_api_fomc_calendar.py::test_declared_fomc_source_retains_announcement_through_sdk`.
3. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R003` (calendar date bounds) is exercised, **Then** `tests/test_api_fomc_calendar.py` covers served refusal and inclusive bounds. Test: `tests/test_api_fomc_calendar.py::test_served_fomc_refuses_invalid_date_ranges`.

### Edge Cases

- If `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R001` is not met, its proving test fails: historical release time.
- If `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R002` is not met, its proving test fails: declared sdk source.
- If `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R003` is not met, its proving test fails: calendar date bounds.

## Requirements

- **FR-001**: Historical release time. Rows: `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R001`.
- **FR-002**: Declared SDK source. Rows: `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R002`.
- **FR-003**: Calendar date bounds. Rows: `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R003`.

## Success Criteria

- **SC-001**: `tests/test_api_fomc_calendar.py` checks UTC timestamps, representative standard and daylight time releases, the corrected January 2026 source, and the returned record. Rows: `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R001`.
- **SC-002**: `tests/test_api_fomc_calendar.py` extracts the served source through the SDK transport. Rows: `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R002`.
- **SC-003**: `tests/test_api_fomc_calendar.py` covers served refusal and inclusive bounds. Rows: `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R003`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
| FR-003 | `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R003` | [plan.md](plan.md) | T-003 | [test-spec.md](test-spec.md) |
