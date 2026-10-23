# CONN-BELLWETHER-MCP-HTTP — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Existing system and reuse

The package carried a copy of the minimum-interval limiter in `bellwether_mcp/http_clients.py`. The SDK now ships the same class as `agent_connector_sdk.httpsupport.RateLimiter` (SDK 0.3.13). The copy is deleted.

## Architecture

Each `_Endpoint` in `bellwether_mcp/mcp/clients.py` holds one governed client and one SDK limiter. The process shares one `Clients` instance, so the limiter paces all traffic to a host.

## Interfaces and data model

No interface change. `RateLimiter(min_interval_seconds)` and `await limiter.wait()` keep their signatures.

## Live integration path

A tool calls `_Endpoint.paced_client()`. It awaits the SDK limiter and returns the governed client.

## Quality and release gates

Run `uv run pytest` and the repository pre-commit hooks.

## Risks, alternatives, and decisions

Decision: keep `build_async_client` local. It builds options from this connector's user agent and endpoint type.
