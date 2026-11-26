---
name: market-data-mcp-development
skill_type: skill
domain: development
description: >-
  Develop, test, gate, and release the market-data-mcp connector. Use this
  skill when changing the connector's API mappings, MCP tools, packaging,
  documentation, or repository gates.
license: MIT
tags: [market-data-mcp, development, connector, test, gates]
tier: repository
metadata:
  version: '0.1.0'
---

# market-data-mcp development

This repository owns the CoinMarketCap discovery/caps, FRED/ALFRED macro
series, and FOMC decision calendar source adapters, MCP tools, and agent
entry points. Shared connector contracts and transports belong to
`scion-sdk`; admission, serving, and durable graph state belong to
their owning repositories. Read `AGENTS.md` before changing code and keep
provider credentials and endpoints out of source, logs, and skill content.

## Rapid delivery: the 5-minute contract

Specs are already designed. Deliver small, reviewable slices and cite the
owning spec row in the commit trailer.

- Find the owning row first with `git grep -n "<term>" -- specs` and extend
  that spec before adding new requirement text.
- Reuse existing SDK clients, transport policies, and tool factories. Do not
  create a second implementation of a connector capability.
- Keep changes scoped to this connector. A change owned by the SDK, Arbora,
  or the knowledge graph belongs in that repository instead.
- Every delivered requirement needs a bound test. Generated `status.json`
  files are produced by `pipelines-hook spec-status`; never hand-edit them.
- One logical change per commit, with `Spec: <ID>` and the assisting agent
  trailer adjacent in the final paragraph.

## Steps
1. Find the owning requirement with `git grep -n "<term>" -- specs`. Verify a spec row id is returned.
2. Edit only the connector files that slice touches. Verify with `git diff --stat` that no unrelated file changed.
3. Run the focused mocked test with `uv run --all-extras pytest tests/test_api_coinmarketcap.py -q`. Verify it passes.
4. Run the gate with `uvx pre-commit run --all-files`. Verify every hook reports Passed.
5. Stage reviewed paths with `git add -- <path>` and commit with a `Spec:` trailer. Verify `git diff --cached --name-status` lists only intended files.

## Failure recovery
| Failure | Cause | Recovery |
|---------|-------|----------|
| No spec row found | The change has no owning requirement | Extend the nearest row under `specs/` before editing code |
| A pre-commit hook fails | A shared gate rule was violated | Read the hook output, fix the named file at its source, and commit again with hooks active |
| A test needs live credentials | A provider call was not mocked | Mock the CoinMarketCap or FRED call and rerun `uv run --all-extras pytest` on that file |

## Setup and gates

Use the pinned environment from `uv sync --locked`. Run the repository
gate from the checkout root:

```bash
uvx pre-commit run --all-files
```

For focused feedback, run the relevant tests with the repository's pinned
environment, for example:

```bash
uv run --all-extras pytest tests/test_connector_tool_parity.py -q
uv run --all-extras pytest tests/test_api_coinmarketcap.py -q
```

The canonical `.pre-commit-config.yaml` delegates connector-standard,
secrets, spec, and tests-fast checks to `Knuckles-Team/pipelines` at
`rev: main`. Do not replace those shared hooks with local copies or bypass
a failing check.

## Connector-specific checks

- Keep the MCP and agent surfaces aligned with `scion-sdk`.
- Validate environment and TLS settings before making provider calls.
- Mock external CoinMarketCap and FRED calls in tests; never use live
  credentials in a local gate.
- Keep `bellwether_mcp/skills/` package data intact when adding skills.
- Documentation lives under `docs/` and is published by the shared Pages
  workflow; source status records live under `specs/`.

## Delivery discipline

Work in a real Git worktree based on `origin/main`. Inspect the complete diff,
stage only reviewed paths, and verify `git status --short` after every gate.
Do not use `git stash`, `git add -A`, or `git add .`; do not claim Pages
publication until a successful exact-source workflow run and the public page
are both observed.
