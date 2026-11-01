# CONN-BELLWETHER-MCP-FRED-VINTAGE — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

This plan delivers fred point-in-time requests for the connector, reusing the SDK for shared capabilities.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk, fastmcp
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest; the proof level each row names
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: one tool per API operation; shared capabilities come from the SDK
- **Scale/Scope**: 6 rows

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

1. `CONN-BELLWETHER-MCP-FRED-VINTAGE-R001`: the bellwether-mcp console script (bellwether_mcp/mcp_server.py::mcp_server) builds the server via bellwether_mcp/mcp/server.py::build_server, which calls bellwether_mcp/mcp/tools_macro_series.py::register_macro_series_tools and serves the fred_series_observations, fred_series_observations_asof and fred_series_vintage_dates tools, which call bellwether_mcp/api/fred.py.
2. `CONN-BELLWETHER-MCP-FRED-VINTAGE-R002`: the bellwether-mcp console script (bellwether_mcp/mcp_server.py::mcp_server) builds the server via bellwether_mcp/mcp/server.py::build_server, which calls bellwether_mcp/mcp/tools_macro_series.py::register_macro_series_tools and serves the fred_series_observations, fred_series_observations_asof and fred_series_vintage_dates tools, which call bellwether_mcp/api/fred.py.
3. `CONN-BELLWETHER-MCP-FRED-VINTAGE-R003`: the bellwether-mcp console script (bellwether_mcp/mcp_server.py::mcp_server) builds the server via bellwether_mcp/mcp/server.py::build_server, which calls bellwether_mcp/mcp/tools_macro_series.py::register_macro_series_tools and serves the fred_series_observations, fred_series_observations_asof and fred_series_vintage_dates tools, which call bellwether_mcp/api/fred.py.
4. `CONN-BELLWETHER-MCP-FRED-VINTAGE-R004`: the bellwether-mcp console script (bellwether_mcp/mcp_server.py::mcp_server) builds the server via bellwether_mcp/mcp/server.py::build_server, which calls bellwether_mcp/mcp/tools_macro_series.py::register_macro_series_tools and serves the fred_series_observations, fred_series_observations_asof and fred_series_vintage_dates tools, which call bellwether_mcp/api/fred.py.
5. `CONN-BELLWETHER-MCP-FRED-VINTAGE-R005`: the bellwether-mcp console script (bellwether_mcp/mcp_server.py::mcp_server) builds the server via bellwether_mcp/mcp/server.py::build_server, which calls bellwether_mcp/mcp/tools_macro_series.py::register_macro_series_tools and serves the fred_series_observations, fred_series_observations_asof and fred_series_vintage_dates tools, which call bellwether_mcp/api/fred.py.
6. `CONN-BELLWETHER-MCP-FRED-VINTAGE-R006`: the declared FRED source is read by the scion_sdk MCP source adapter over the served fred_series_observations tool registered through bellwether_mcp/__init__.py::connector, down to bellwether_mcp/api/fred.py::get_observations.

## Cross-repo seams

none. The cited owner rows are library capabilities the connector calls in process; spec.md names them.
