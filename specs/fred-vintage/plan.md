# CONN-BELLWETHER-MCP-FRED-VINTAGE — Design and implementation plan

Governing spec: [spec.md](spec.md).

The FRED API defaults omitted real-time bounds to today. The as-of client
therefore validates its required date before it constructs a request. Explicit
bounds also require canonical calendar dates and an ordered window. The latest
observation call may still omit both bounds.

The MCP as-of tool calls this same client. Tests enter the served tool with an
invalid date and observe a refusal with zero vendor requests.

Source: [FRED real-time periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html).

The observation client refuses non-finite numeric values before the MCP tool returns a page. The explicit missing-value marker still maps to null.

A page must carry an observations list of objects. The client accepts an empty list but does not treat a missing list as an empty result.
