# CONN-BELLWETHER-MCP-CMC-VALUES — Requirements

Governing spec: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-BELLWETHER-MCP-CMC-VALUES-R001` | **Finite market values.** Listing, quote and global-metric numeric fields refuse non-finite or non-numeric values. Null fields remain null. | `tests/test_api_coinmarketcap.py` checks served refusal and null preservation. |
