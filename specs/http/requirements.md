# CONN-BELLWETHER-MCP-HTTP — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A child row `.n` is one five-minute unit of work. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-BELLWETHER-MCP-HTTP-R001` | **SDK request pacing.** Each vendor endpoint in `bellwether_mcp/mcp/clients.py` paces its calls with the SDK `RateLimiter` at its `min_interval_seconds`. The package ships no limiter of its own. Caller chain: every vendor tool served by bellwether_mcp/mcp/server.py::build_server obtains its endpoint from bellwether_mcp/mcp/clients.py::Clients, whose _Endpoint.paced_client (line 41) awaits the SDK RateLimiter via limiter.wait before returning the client. Shape: _Endpoint in bellwether_mcp/mcp/clients.py constructs scion_sdk.httpsupport.RateLimiter(self.config.min_interval_seconds); the package defines no limiter class. | `tests/test_sdk_rate_limiter.py::test_endpoint_limiter_is_the_sdk_limiter` and `tests/test_sdk_rate_limiter.py::test_package_ships_no_rate_limiter` pass. |
| `CONN-BELLWETHER-MCP-HTTP-R002` | **CoinMarketCap keys never follow redirects.** Each keyed CoinMarketCap call disables redirect following even when its injected client enables it. A redirect refuses without forwarding the key to a second destination. Caller chain: the cmc_listings, cmc_quotes and cmc_global_metrics tools in bellwether_mcp/mcp/tools_crypto_reference.py call list_listings (line 93), get_quotes (line 122) and get_global_metrics (line 145) in bellwether_mcp/api/coinmarketcap.py. Shape: each of those three functions passes follow_redirects=False on its keyed request (lines 111, 129, 156) so an injected client cannot follow a redirect. | `tests/test_api_coinmarketcap.py::test_api_key_is_not_forwarded_on_redirect` exercises listings, quotes and global metrics. |
