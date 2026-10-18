# Configuration, trust, and privacy

This page is the operator contract for `bellwether-mcp`. Package-specific
endpoint, authentication, tool-toggle, and rate-limit settings remain
documented in the repository README, `AGENTS.md`, and the installed command's
`--help` output. Runtime values must be injected by the launcher; they do not
belong in source, packaged skill content, traces, or generated reports.

## Capability configuration

The current capability surface is defined by:

- the eight MCP tools described in the README and `docs/usage.md`;
- the ten declarative `agent_connector_sdk.manifest.presets.ToolPreset` entries
  in `connectors/mcp_source_presets.json`;
- `connector_manifest.yml` and its ontology, mappings, shapes, fixtures,
  migrations, tool-schema fingerprints, and certification metadata.

Treat those artifacts as a unit during release and deployment. Do not enable a
preset whose tool-schema fingerprint does not match the installed package's
live `tools/list` schema (regenerate with `scripts/compute_tool_fingerprints.py`
after any tool signature/docstring change).

## Runtime values and secrets

- Supply the two vendor API keys through environment variables or a mounted
  secret provider — never as a tool argument.
- Use non-personal agent aliases and opaque tenant/correlation identifiers.
- Keep developer directories, workstation names, and deployment hostnames out
  of checked-in configuration.
- Bind network transports to an explicitly chosen interface and require the
  deployment's MCP authentication policy before accepting remote traffic.

The checked-in examples use `localhost` for loopback-only development and
placeholder key values for replaceable credentials. Neither is a production
default.

## TLS trust

Certificate verification is required for every outbound HTTP call — both
vendor clients go through `agent_connector_sdk.http.client`'s governed
transport, which checks TLS by default. Do not disable verification to work
around an incomplete server chain.

## Privacy and data governance

The default observability posture is metadata-only. Do not persist API
credentials, raw HTTP request/response bodies, local paths, hostnames, or
personal identity in logs or reports. `bellwether_mcp.config.USER_AGENT`
advertises only a contact email (`BELLWETHER_CONTACT_EMAIL`), never a
hostname or personal identifier.

When the declarative source adapters are wired to a live sink (deployment
layer, outside this package — see `AGENTS.md`), each change must carry
tenant, ACL, classification, retention, provenance, and checkpoint/delta
metadata per `agent_connector_sdk`'s `SourceIngestionRequest` contract. Reject
or quarantine records that cannot satisfy that contract; never silently widen
a tenant scope.

## Deployment verification

1. Validate `connector_manifest.yml` and the tool-schema fingerprints against
   the installed package's live `tools/list` schema.
2. Confirm `BELLWETHER_CMC_API_KEY` / `BELLWETHER_FRED_API_KEY` are present
   without printing their values.
3. Check the complete TLS chain with certificate verification enabled.
4. Exercise the `/health` endpoint (HTTP transports) and one keyless read
   (`fomc_calendar_list`) plus one keyed read per vendor.
5. Record only sanitized pass/fail evidence and version identifiers.
