# CONN-BELLWETHER-MCP-FOMC-ANNOUNCEMENTS — Plan

Governing spec: [spec.md](spec.md).

The existing MCP tool calls the local calendar reader, which projects the packaged curated dataset. Add the Federal Reserve release time to that data and projection; retain the existing date, ID and pagination contracts. Each timestamp is checked against its linked original statement. No live scrape or future schedule is implied. Run the focused tests, full test suite, and repository pre-commit and pre-push gates.
