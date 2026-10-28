# CONN-BELLWETHER-MCP-CMC-VALUES — Test specification

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

- `CONN-BELLWETHER-MCP-CMC-VALUES-R001`: `tests/test_api_coinmarketcap.py` checks invalid values through the served tools and preserves null supply fields.

- `CONN-BELLWETHER-MCP-CMC-VALUES-R002`: `tests/test_api_coinmarketcap.py` covers malformed responses through the served tools and accepts empty collections.

- `CONN-BELLWETHER-MCP-CMC-VALUES-R003`: `tests/test_api_coinmarketcap.py` covers invalid and missing asset IDs through the served tools.

- `CONN-BELLWETHER-MCP-CMC-VALUES-R004`: `tests/test_api_coinmarketcap.py` covers repeated asset IDs with equal and different values through served tools.
