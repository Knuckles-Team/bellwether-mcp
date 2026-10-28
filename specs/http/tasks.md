# CONN-BELLWETHER-MCP-HTTP — Implementation tasks

Governing spec: [spec.md](spec.md). Design: [plan.md](plan.md). Rows: [requirements.md](requirements.md).

- [x] Replace the local limiter with the SDK `RateLimiter` and delete the copy (CONN-BELLWETHER-MCP-HTTP-R001).
- [x] Refuse redirects on keyed CoinMarketCap calls (CONN-BELLWETHER-MCP-HTTP-R002).
