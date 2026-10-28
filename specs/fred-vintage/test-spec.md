# CONN-BELLWETHER-MCP-FRED-VINTAGE — Test specification

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

- `CONN-BELLWETHER-MCP-FRED-VINTAGE-R001`: `tests/test_api_fred.py` checks valid vintage binding and refusal before a vendor request, including through the served MCP tool.

- `CONN-BELLWETHER-MCP-FRED-VINTAGE-R002`: `tests/test_api_fred.py` exercises non-finite refusal through the served tool.

- `CONN-BELLWETHER-MCP-FRED-VINTAGE-R003`: `tests/test_api_fred.py` covers malformed pages at the served tool and an empty valid page.

- `CONN-BELLWETHER-MCP-FRED-VINTAGE-R004`: `tests/test_api_fred.py` checks served refusal of missing or invalid observation identity fields.

- `CONN-BELLWETHER-MCP-FRED-VINTAGE-R005`: `tests/test_api_fred.py` covers malformed vintage-date pages through the served tool and an empty valid page.

- `CONN-BELLWETHER-MCP-FRED-VINTAGE-R006`: `tests/test_api_fred.py` extracts two FRED pages through the SDK transport and declared source adapter.
