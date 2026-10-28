# CONN-BELLWETHER-MCP-CMC-PAGING — Requirements

Governing spec: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-BELLWETHER-MCP-CMC-PAGING-R001` | **Start listings at the first record.** The served CMC listings tool defaults to zero-based offset zero and translates explicit offsets to the provider's one-based start. | `tests/test_api_coinmarketcap.py` exercises default and explicit offsets through the served MCP tool. |
