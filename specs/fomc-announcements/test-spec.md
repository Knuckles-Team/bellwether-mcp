# CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS — Tests

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R001` | `tests/test_api_fomc_calendar.py` | Every returned timestamp is UTC and matches its decision date; representative standard and daylight releases and the January 2026 source match the original statements. |

- `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R002`: `tests/test_api_fomc_calendar.py` extracts a curated announcement through the SDK transport and adapter.
