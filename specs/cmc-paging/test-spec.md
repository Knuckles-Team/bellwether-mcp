# CONN-BELLWETHER-MCP-CMC-PAGING — Test specification

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

- `CONN-BELLWETHER-MCP-CMC-PAGING-R001`: `tests/test_api_coinmarketcap.py` observes provider starts for the served tool's default and an explicit offset.

- `CONN-BELLWETHER-MCP-CMC-PAGING-R002`: `tests/test_api_coinmarketcap.py` extracts two pages through the real SDK transport and adapter using the declared source.
