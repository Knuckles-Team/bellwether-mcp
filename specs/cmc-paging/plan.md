# CONN-BELLWETHER-MCP-CMC-PAGING — Design and implementation plan

Governing spec: [spec.md](spec.md).

The CMC client already translates zero-based offsets to one-based provider starts. The served tool defaults its offset to zero so its first request includes the first listing. Explicit offsets use the same translation.

The cross-package test builds the SDK contract from the connector declaration and drives the served tool through the SDK MCP transport. Two synthetic provider pages exercise the actual offset handoff.

The listings client validates zero-based offsets and positive page limits before constructing a provider request.
