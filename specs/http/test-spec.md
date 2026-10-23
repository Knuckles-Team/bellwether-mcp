# CONN-BELLWETHER-MCP-HTTP — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Level | Setup and input | Expected observation | Evidence |
|---|---|---|---|---|---|
| T-001 | FR-001 | Unit | A `Clients()` instance. | Each endpoint limiter is an SDK `RateLimiter` with the endpoint's interval. |  |
| T-002 | SC-001 | Unit | The `bellwether_mcp.http_clients` module. | The module has no `RateLimiter` attribute. |  |

## Negative and boundary cases

The SDK tests cover zero and negative intervals and concurrent callers.

## Quality and release proof

Run `uv run pytest tests/test_sdk_rate_limiter.py`.
