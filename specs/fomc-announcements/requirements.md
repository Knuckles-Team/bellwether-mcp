# CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS — Requirements

Governing spec: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R001` | **Historical release time.** The curated FOMC calendar returns each existing decision's sourced UTC announcement time. | `tests/test_api_fomc_calendar.py` checks UTC timestamps, representative standard and daylight time releases, the corrected January 2026 source, and the returned record. |
| `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R002` | **Declared SDK source.** The declared FOMC source retains the curated announcement time and source URL through the SDK MCP adapter. | `tests/test_api_fomc_calendar.py` extracts the served source through the SDK transport. |
