# CONN-BELLWETHER-MCP-CONNECTOR-CONTENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Architecture

`pyproject.toml` declares `bellwether-mcp` as the connector identity. `create_mcp_server` resolves the packaged content of `bellwether_mcp` from it.
