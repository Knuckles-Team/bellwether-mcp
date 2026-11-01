# CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

This plan delivers sourced decision times for the connector, reusing the SDK for shared capabilities.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk, fastmcp
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest; the proof level each row names
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: one tool per API operation; shared capabilities come from the SDK
- **Scale/Scope**: 3 rows

## Constitution Check

- One owner per concept: pass. The connector owns one external system's calls, mappings and tools only.
- Connectors depend on the SDK and are called through arbora: pass.
- No ratchets: pass. The rows add no suppression.

## Project Structure

```text
No file is added; the rows edit existing files.
```

## Phase 0: Research

No unknowns. Each row names the code it touches.

## Phase 1: Design

The rows are delivered in place; the design is the caller chain below.

## Phase 2: Task approach

`tasks.md` holds one task line per row, producer first.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks apply: `ruff-format`, `connector-standard`, `secrets`, `tests-fast`. Each row names its proving test. No suppression and no duplicate implementation.

## Production caller chain

1. `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R001`: the bellwether-mcp console script (bellwether_mcp/mcp_server.py::mcp_server) builds the server via bellwether_mcp/mcp/server.py::build_server, which calls bellwether_mcp/mcp/tools_fomc_calendar.py::register_fomc_calendar_tools and serves fomc_calendar_list, which calls bellwether_mcp/api/fomc_calendar.py::list_meetings.
2. `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R002`: the declared FOMC source is read by the scion_sdk MCP source adapter over the served fomc_calendar_list tool registered through bellwether_mcp/__init__.py::connector, down to bellwether_mcp/api/fomc_calendar.py::list_meetings.
3. `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R003`: the bellwether-mcp console script (bellwether_mcp/mcp_server.py::mcp_server) builds the server via bellwether_mcp/mcp/server.py::build_server, which calls bellwether_mcp/mcp/tools_fomc_calendar.py::register_fomc_calendar_tools and serves fomc_calendar_list, which calls bellwether_mcp/api/fomc_calendar.py::list_meetings.

## Cross-repo seams

none
