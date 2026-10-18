"""``bellwether-mcp`` console-script entry point."""

from __future__ import annotations

import sys

from bellwether_mcp._version import __version__
from bellwether_mcp.mcp.server import build_server

__all__ = ["mcp_server"]


def mcp_server() -> None:
    """Build and run the server on the transport ``--transport`` selects."""
    mcp, args, _middlewares, _clients = build_server()
    print(f"bellwether-mcp v{__version__}", file=sys.stderr)
    if args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    mcp_server()
