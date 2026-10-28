# CONN-BELLWETHER-MCP-HTTP — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A child row `.n` is one five-minute unit of work. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-BELLWETHER-MCP-HTTP-R001` | **SDK request pacing.** Each vendor endpoint in `bellwether_mcp/mcp/clients.py` paces its calls with the SDK `RateLimiter` at its `min_interval_seconds`. The package ships no limiter of its own. | `tests/test_sdk_rate_limiter.py::test_endpoint_limiter_is_the_sdk_limiter` and `tests/test_sdk_rate_limiter.py::test_package_ships_no_rate_limiter` pass. |
| `CONN-BELLWETHER-MCP-HTTP-R002` | **CoinMarketCap keys never follow redirects.** Each keyed CoinMarketCap call disables redirect following even when its injected client enables it. A redirect refuses without forwarding the key to a second destination. | `tests/test_api_coinmarketcap.py::test_api_key_is_not_forwarded_on_redirect` exercises listings, quotes and global metrics. |
