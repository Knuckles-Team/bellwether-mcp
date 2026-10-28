# CONN-BELLWETHER-MCP-FRED-VINTAGE — Requirements

Governing spec: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-BELLWETHER-MCP-FRED-VINTAGE-R001` | **Validate point-in-time windows.** The FRED client requires a canonical calendar date for each explicit real-time bound. The as-of operation requires a date and pins both bounds. Invalid or reversed bounds refuse before any vendor request. | `tests/test_api_fred.py` checks the API and served MCP path, valid dates and zero vendor calls on refusal. |
