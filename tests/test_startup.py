"""Import-time smoke test and a bare server-build smoke test."""

from __future__ import annotations


def test_startup() -> None:
    import bellwether_mcp.api.coinmarketcap  # noqa: F401
    import bellwether_mcp.api.fomc_calendar  # noqa: F401
    import bellwether_mcp.api.fred  # noqa: F401
    import bellwether_mcp.connectors.adapters  # noqa: F401
    import bellwether_mcp.credentials  # noqa: F401
    import bellwether_mcp.mcp.server  # noqa: F401
    import bellwether_mcp.mcp_server  # noqa: F401


def test_build_server_with_no_auth_configured() -> None:
    from bellwether_mcp.mcp.server import build_server

    mcp, args, middlewares, clients = build_server(command_args=[])
    assert mcp.name == "bellwether-mcp"
    assert args.transport == "stdio"
    assert isinstance(middlewares, list)
    assert clients.coinmarketcap.config.base_url.endswith("coinmarketcap.com")
    assert clients.fred.config.base_url.endswith("/fred")
