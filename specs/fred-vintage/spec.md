# CONN-BELLWETHER-MCP-FRED-VINTAGE — FRED point-in-time requests

Owner: bellwether-mcp. Cross-repo IDs: `SDK-FINANCE-SOURCES-R001`.

## Purpose and user stories

A caller needs FRED observations as known on a specified date. An invalid date
must not silently request the latest revision.

## Requirements and acceptance

See [requirements.md](requirements.md).

## Why a new spec

The `http` spec owns pacing and redirect boundaries. The `connector-content`
spec owns packaged content. Neither owns FRED vintage semantics.
