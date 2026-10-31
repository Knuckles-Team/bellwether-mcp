# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.8] - 2026-10-30

### Changed
- Migrate to the `scion_sdk` import package and require `scion-sdk[mcp]>=0.6.4,<0.7.0`.

## [1.3.7] - 2026-10-28

### Added
- Validate served FRED, ETF, sentiment and on-chain sources against a real graph.

### Changed
- Preserve FRED capture times and pair ETF flows with sourced assets under management.
- Keep connector specification receipts and packaged skill metadata current.

## [1.3.4] - 2026-10-23

### Changed
- Requires `agent-connector-sdk>=0.4.1`; data sources are declared in code (`connector_sources`).

## [Unreleased]

## [1.3.0] - 2026-10-18

### Changed
- Renamed from market-data-mcp to bellwether-mcp (PyPI distribution, import package
  `bellwether_mcp`, CLI `bellwether-mcp`, Docker image `knucklessg1/bellwether-mcp`,
  GitHub repository). Settings move from `MARKET_DATA_*` to `BELLWETHER_*`; the old
  prefix is still read, with a DeprecationWarning, for this release. Tool names and
  spec IDs (`CONN-MARKET-DATA-MCP`) are unchanged. agent-connector-sdk 0.3.6 floor.


### Added
-

### Changed
-

### Fixed
-

## [0.1.0] - 2026-09-24

### Added
- Initial release: CoinMarketCap crypto discovery/caps, FRED/ALFRED macro series
  with point-in-time vintages, and a curated FOMC decision calendar, as an MCP
  server plus `agent-connector-sdk` declarative source-adapter presets.
