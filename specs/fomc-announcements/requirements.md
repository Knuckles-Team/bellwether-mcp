# CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS — Requirements

Governing spec: [spec.md](spec.md).

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS-R001` | **Historical release time.** The curated FOMC calendar returns each existing decision's sourced UTC announcement time. | `tests/test_api_fomc_calendar.py` checks UTC timestamps, representative standard and daylight time releases, the corrected January 2026 source, and the returned record. |
