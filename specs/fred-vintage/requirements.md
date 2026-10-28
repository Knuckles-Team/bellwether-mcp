# CONN-BELLWETHER-MCP-FRED-VINTAGE — Requirements

Governing spec: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-BELLWETHER-MCP-FRED-VINTAGE-R001` | **Validate point-in-time windows.** The FRED client requires a canonical calendar date for each explicit real-time bound. The as-of operation requires a date and pins both bounds. Invalid or reversed bounds refuse before any vendor request. | `tests/test_api_fred.py` checks the API and served MCP path, valid dates and zero vendor calls on refusal. |
| `CONN-BELLWETHER-MCP-FRED-VINTAGE-R002` | **Finite observations.** FRED observations refuse non-finite values. The missing-value marker remains a null value. | `tests/test_api_fred.py` checks refusal through the served tool and existing missing-value behavior. |
| `CONN-BELLWETHER-MCP-FRED-VINTAGE-R003` | **Observation page shape.** A FRED page has an observations list of objects. A missing or malformed list refuses; an empty list is valid. | `tests/test_api_fred.py` exercises refusal through the served tool and a valid empty page. |
