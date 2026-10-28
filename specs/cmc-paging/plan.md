# CONN-BELLWETHER-MCP-CMC-PAGING — Design and implementation plan

Governing spec: [spec.md](spec.md).

The CMC client already translates zero-based offsets to one-based provider starts. The served tool defaults its offset to zero so its first request includes the first listing. Explicit offsets use the same translation.
