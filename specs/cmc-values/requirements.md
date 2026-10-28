# CONN-BELLWETHER-MCP-CMC-VALUES — Requirements

Governing spec: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-BELLWETHER-MCP-CMC-VALUES-R001` | **Finite market values.** Listing, quote and global-metric numeric fields refuse non-finite or non-numeric values. Null fields remain null. | `tests/test_api_coinmarketcap.py` checks served refusal and null preservation. |
| `CONN-BELLWETHER-MCP-CMC-VALUES-R002` | **Response data shape.** Listing and quote pages require their data collections. Global metrics require a USD quote. Missing or malformed data refuses instead of producing an empty result. | `tests/test_api_coinmarketcap.py` exercises served refusal and valid empty collections. |
| `CONN-BELLWETHER-MCP-CMC-VALUES-R003` | **Provider identity.** Listings and quotes require a positive integer CMC asset ID. Invalid or missing IDs refuse instead of producing a fabricated string identity. | `tests/test_api_coinmarketcap.py` covers served refusal for listings and quotes. |
