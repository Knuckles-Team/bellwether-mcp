# CONN-BELLWETHER-MCP-FRED-VINTAGE — Implementation tasks

Governing spec: [spec.md](spec.md). Design: [plan.md](plan.md). Rows: [requirements.md](requirements.md).

- [x] Validate explicit real-time dates and the as-of window (CONN-BELLWETHER-MCP-FRED-VINTAGE-R001).

- [x] Refuse non-finite FRED observation values (CONN-BELLWETHER-MCP-FRED-VINTAGE-R002).

- [x] Refuse malformed FRED observation pages (CONN-BELLWETHER-MCP-FRED-VINTAGE-R003).

- [x] Refuse observations without complete period and vintage identity (CONN-BELLWETHER-MCP-FRED-VINTAGE-R004).

- [x] Refuse malformed FRED vintage-date pages (CONN-BELLWETHER-MCP-FRED-VINTAGE-R005).

- [x] Exercise the declared FRED source through the SDK MCP adapter (CONN-BELLWETHER-MCP-FRED-VINTAGE-R006).
