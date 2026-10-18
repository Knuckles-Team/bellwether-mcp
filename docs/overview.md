# bellwether-mcp — Concept Overview

> **Category**: Finance | **Ecosystem Role**: MCP Server + `agent-connector-sdk` source adapters
> Built directly on [`agent-connector-sdk`](https://github.com/Knuckles-Team/agent-connector-sdk) — **not**
> `agent-utilities` (see "Why agent-connector-sdk" below).

## Description

Crypto discovery/caps (CoinMarketCap), Fed macro series with point-in-time vintages
(FRED/ALFRED), and the FOMC decision calendar as an MCP server and
`agent-connector-sdk` source adapters.

## Why `agent-connector-sdk`, not `agent-utilities`

Most fleet packages depend on `agent-utilities` directly and ship an
`agent_server.py` A2A agent alongside their MCP server. `bellwether-mcp` is
modeled on `agents/world-reference-mcp` — the first package built on this
newer, lighter architecture per RF-ADR-009 §2.2.1 ("a new API source is a
preset, not code"):

- **Ports, not ad hoc code.** Every one of this connector's ten streams is one
  `agent_connector_sdk.manifest.presets.ToolPreset` entry in
  `connectors/mcp_source_presets.json`, extracted by the SDK's generic
  `agent_connector_sdk.adapters.mcp_tool.McpToolSourceAdapter`.
- **No direct epistemic-graph dependency, and no `agent-utilities`.** This
  package never builds its own knowledge-graph client and ships no
  `kg_ingest.py`-style direct-to-graph tool. Delivery to a live graph is
  entirely `agent_connector_sdk.runner`/`sinks`' job, wired at deployment time
  from `connectors.adapters.build_source_adapters()`. There is consequently no
  `agent_server.py` here either — see `AGENTS.md` for the full rationale.

## Architecture

This project follows the fleet's connector pattern, minus the agent layer:

```
bellwether-mcp/
├── bellwether_mcp/          # Source code
│   ├── api/                      # Thin async vendor clients (CMC, FRED, FOMC)
│   ├── mcp/                      # The eight-tool FastMCP surface + composition root
│   ├── connectors/                # Declarative mcp_tool presets + the SourceAdapter factory
│   ├── ontology/                  # This connector's own admin-lifecycle ontology
│   ├── config.py                  # Base URLs, rate limits, FRED series aliases
│   ├── credentials.py             # Server-side credential resolution (env:// / openbao://)
│   └── mcp_server.py              # Entry point (build_server)
├── tests/                     # Test suite
├── docs/                      # Documentation
├── pyproject.toml             # Package metadata
├── mcp_config.json             # MCP server configuration
└── docker/Dockerfile           # Container deployment (single MCP-only target)
```

## MCP Configuration

### stdio Mode
```json
{
  "mcpServers": {
    "bellwether-mcp": {
      "command": "uv",
      "args": ["run", "--with", "bellwether-mcp", "bellwether-mcp"],
      "env": {}
    }
  }
}
```

### Streamable HTTP Mode
```bash
bellwether-mcp --transport streamable-http --port 8000
```
