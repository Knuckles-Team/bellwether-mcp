# CONN-BELLWETHER-MCP-FRED-VINTAGE — FRED point-in-time requests

Owner: bellwether-mcp. Cross-repo IDs: `SCION-FINANCE-SOURCES-R001`.

## Purpose and user stories

A caller needs FRED observations as known on a specified date. An invalid date
must not silently request the latest revision.

## Why a new spec

The `http` spec owns pacing and redirect boundaries. The `connector-content`
spec owns packaged content. Neither owns FRED vintage semantics.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the SDK modules and the engine, which own the shared capabilities.

## User Scenarios & Testing

### User Story 1 - FRED point-in-time requests (Priority: P1)

A caller needs FRED observations as known on a specified date. An invalid date.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-FRED-VINTAGE-R001` (validate point-in-time windows) is exercised, **Then** `tests/test_api_fred.py` checks the API and served MCP path, valid dates and zero vendor calls on refusal. Test: `tests/test_api_fred.py::test_invalid_explicit_realtime_windows_never_request`.
2. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-FRED-VINTAGE-R002` (finite observations) is exercised, **Then** `tests/test_api_fred.py` checks refusal through the served tool and existing missing-value behavior. Test: `tests/test_api_fred.py::test_served_fred_refuses_nonfinite_observations`.
3. **Given** the connector is configured, **When** the behaviour of row `CONN-BELLWETHER-MCP-FRED-VINTAGE-R003` (observation page shape) is exercised, **Then** `tests/test_api_fred.py` exercises refusal through the served tool and a valid empty page. Test: `tests/test_api_fred.py::test_served_fred_refuses_malformed_observation_pages`.

### Edge Cases

- If `CONN-BELLWETHER-MCP-FRED-VINTAGE-R001` is not met, its proving test fails: validate point-in-time windows.
- If `CONN-BELLWETHER-MCP-FRED-VINTAGE-R002` is not met, its proving test fails: finite observations.
- If `CONN-BELLWETHER-MCP-FRED-VINTAGE-R003` is not met, its proving test fails: observation page shape.

## Requirements

- **FR-001**: Validate point-in-time windows. Rows: `CONN-BELLWETHER-MCP-FRED-VINTAGE-R001`.
- **FR-002**: Finite observations. Rows: `CONN-BELLWETHER-MCP-FRED-VINTAGE-R002`.
- **FR-003**: Observation page shape. Rows: `CONN-BELLWETHER-MCP-FRED-VINTAGE-R003`.
- **FR-004**: Observation identity. Rows: `CONN-BELLWETHER-MCP-FRED-VINTAGE-R004`.
- **FR-005**: Vintage-date page shape. Rows: `CONN-BELLWETHER-MCP-FRED-VINTAGE-R005`.
- **FR-006**: Declared SDK source. Rows: `CONN-BELLWETHER-MCP-FRED-VINTAGE-R006`.

## Success Criteria

- **SC-001**: `tests/test_api_fred.py` checks the API and served MCP path, valid dates and zero vendor calls on refusal. Rows: `CONN-BELLWETHER-MCP-FRED-VINTAGE-R001`.
- **SC-002**: `tests/test_api_fred.py` checks refusal through the served tool and existing missing-value behavior. Rows: `CONN-BELLWETHER-MCP-FRED-VINTAGE-R002`.
- **SC-003**: `tests/test_api_fred.py` exercises refusal through the served tool and a valid empty page. Rows: `CONN-BELLWETHER-MCP-FRED-VINTAGE-R003`.
- **SC-004**: `tests/test_api_fred.py` exercises refusal through the served tool. Rows: `CONN-BELLWETHER-MCP-FRED-VINTAGE-R004`.
- **SC-005**: `tests/test_api_fred.py` exercises served refusal and a valid empty page. Rows: `CONN-BELLWETHER-MCP-FRED-VINTAGE-R005`.
- **SC-006**: `tests/test_api_fred.py` extracts two served pages through the SDK transport and adapter. Rows: `CONN-BELLWETHER-MCP-FRED-VINTAGE-R006`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-BELLWETHER-MCP-FRED-VINTAGE-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-BELLWETHER-MCP-FRED-VINTAGE-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
| FR-003 | `CONN-BELLWETHER-MCP-FRED-VINTAGE-R003` | [plan.md](plan.md) | T-003 | [test-spec.md](test-spec.md) |
| FR-004 | `CONN-BELLWETHER-MCP-FRED-VINTAGE-R004` | [plan.md](plan.md) | T-004 | [test-spec.md](test-spec.md) |
| FR-005 | `CONN-BELLWETHER-MCP-FRED-VINTAGE-R005` | [plan.md](plan.md) | T-005 | [test-spec.md](test-spec.md) |
| FR-006 | `CONN-BELLWETHER-MCP-FRED-VINTAGE-R006` | [plan.md](plan.md) | T-006 | [test-spec.md](test-spec.md) |
