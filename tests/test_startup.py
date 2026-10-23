"""Import-time smoke test and a bare server-build smoke test."""

from __future__ import annotations


def test_build_server_with_no_auth_configured() -> None:
    from bellwether_mcp.mcp.server import build_server

    mcp, args, middlewares, clients = build_server(command_args=[])
    assert mcp.name == "bellwether-mcp"
    assert args.transport == "stdio"
    assert isinstance(middlewares, list)
    assert clients.coinmarketcap.config.base_url.endswith("coinmarketcap.com")
    assert clients.fred.config.base_url.endswith("/fred")
