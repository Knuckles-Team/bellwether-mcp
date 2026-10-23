# bellwether-mcp specifications

These specs follow the ecosystem [spec standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/spec-standard.md): one owning spec per capability, extend an existing spec before creating one, audits and reviews land in the owning spec, one ID and title form, one file set. The `spec-standard` gate enforces it.

## Owner

This repository owns the specs with the ID prefix `CONN-BELLWETHER-MCP`. The connector contract, certification, and transport rules belong to [agent-connector-sdk](https://github.com/Knuckles-Team/agent-connector-sdk/tree/main/specs). The spec-delivery page rules belong to [pipelines](https://github.com/Knuckles-Team/pipelines/tree/main/specs).

## Prefix alias

The prefix `CONN-MARKET-DATA-MCP-` is the retired name of `CONN-BELLWETHER-MCP-`. `.config/spec-aliases.toml` maps it, so an older commit trailer counts for the new prefix.

## Add a spec

Read the existing specs first. Extend the spec that owns the behavior. Create a spec only for a capability that no spec owns. Copy [`_template/`](_template/) to `specs/<area>/`, set the ID to `CONN-BELLWETHER-MCP` or `CONN-BELLWETHER-MCP-<AREA>`, and add one index line below.

## Local specifications

- [`http`](http/spec.md): Outbound HTTP pacing
- [`CONN-BELLWETHER-MCP-CONNECTOR-CONTENT`](connector-content/spec.md) — The connector serves its packaged content.
