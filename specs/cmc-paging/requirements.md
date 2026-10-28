# CONN-BELLWETHER-MCP-CMC-PAGING — Requirements

Governing spec: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-BELLWETHER-MCP-CMC-PAGING-R001` | **Start listings at the first record.** The served CMC listings tool defaults to zero-based offset zero and translates explicit offsets to the provider's one-based start. | `tests/test_api_coinmarketcap.py` exercises default and explicit offsets through the served MCP tool. |
| `CONN-BELLWETHER-MCP-CMC-PAGING-R002` | **SDK source paging.** The declared CMC listings source pages through the SDK MCP adapter without skipping records. | `tests/test_api_coinmarketcap.py` extracts two served pages with the SDK transport and source adapter. |
| `CONN-BELLWETHER-MCP-CMC-PAGING-R003` | **Valid page bounds.** Listing offsets are nonnegative integers and limits are positive integers. Invalid bounds refuse before the provider request. | `tests/test_api_coinmarketcap.py` covers served refusal and direct client validation. |
