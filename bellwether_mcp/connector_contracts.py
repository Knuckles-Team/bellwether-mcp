"""Surface contracts: tool use, links, data locations and business roles."""

from scion_sdk.surface_contracts import (
    BusinessRole,
    DataLocation,
    Refusal,
    SurfaceLink,
    ToolStep,
    ToolUseContract,
)

CONTRACTS = (
    ToolUseContract(
        "rank-crypto-assets",
        (
            ToolStep(
                "cmc_listings",
                params=("start", "limit", "mode", "source_checkpoint"),
                result=("id", "symbol", "name", "cmc_rank", "market_cap"),
                refusals=(
                    Refusal(
                        "CREDENTIAL_MISSING",
                        "the server-side credential reference resolves to nothing",
                    ),
                    Refusal(
                        "RATE_LIMITED",
                        "the vendor API throttles the request after the process's paced interval",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "quote-crypto-symbols",
        (
            ToolStep(
                "cmc_listings",
                params=("start", "limit"),
                result=("symbol", "cmc_rank"),
                refusals=(
                    Refusal(
                        "CREDENTIAL_MISSING",
                        "the server-side credential reference resolves to nothing",
                    ),
                    Refusal(
                        "RATE_LIMITED",
                        "the vendor API throttles the request after the process's paced interval",
                    ),
                ),
            ),
            ToolStep(
                "cmc_quotes",
                params=("symbols",),
                result=("symbol", "price", "volume_24h", "percent_change_24h"),
                refusals=(
                    Refusal(
                        "CREDENTIAL_MISSING",
                        "the server-side credential reference resolves to nothing",
                    ),
                    Refusal("UNKNOWN_SYMBOL", "the symbol is not listed"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "read-crypto-market-metrics",
        (
            ToolStep(
                "cmc_global_metrics",
                params=("mode", "source_checkpoint"),
                result=(
                    "total_market_cap",
                    "btc_dominance",
                    "eth_dominance",
                    "total_volume_24h",
                ),
                refusals=(
                    Refusal(
                        "CREDENTIAL_MISSING",
                        "the server-side credential reference resolves to nothing",
                    ),
                    Refusal(
                        "RATE_LIMITED",
                        "the vendor API throttles the request after the process's paced interval",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "read-a-macro-series",
        (
            ToolStep(
                "fred_macro_series_aliases",
                result=("aliases",),
            ),
            ToolStep(
                "fred_series_observations",
                params=(
                    "series_id",
                    "alias",
                    "offset",
                    "limit",
                    "realtime_start",
                    "realtime_end",
                    "mode",
                    "source_checkpoint",
                ),
                result=(
                    "observation_date",
                    "value",
                    "series_id",
                    "realtime_start",
                    "realtime_end",
                ),
                refusals=(
                    Refusal(
                        "CREDENTIAL_MISSING",
                        "the server-side credential reference resolves to nothing",
                    ),
                    Refusal("UNKNOWN_ALIAS", "the alias is not one the package ships"),
                    Refusal(
                        "RATE_LIMITED",
                        "the vendor API throttles the request after the process's paced interval",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "reconstruct-a-series-as-of",
        (
            ToolStep(
                "fred_series_vintage_dates",
                params=("series_id", "alias", "offset", "limit"),
                result=("vintage_date",),
                refusals=(
                    Refusal(
                        "CREDENTIAL_MISSING",
                        "the server-side credential reference resolves to nothing",
                    ),
                    Refusal(
                        "RATE_LIMITED",
                        "the vendor API throttles the request after the process's paced interval",
                    ),
                ),
            ),
            ToolStep(
                "fred_series_observations_asof",
                params=("vintage_date", "series_id", "alias", "offset", "limit"),
                result=("observation_date", "value", "vintage_date"),
                refusals=(
                    Refusal(
                        "CREDENTIAL_MISSING",
                        "the server-side credential reference resolves to nothing",
                    ),
                    Refusal(
                        "INVALID_VINTAGE",
                        "the vintage date is not a published revision date",
                    ),
                    Refusal(
                        "RATE_LIMITED",
                        "the vendor API throttles the request after the process's paced interval",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "list-fomc-decisions",
        (
            ToolStep(
                "fomc_calendar_list",
                params=(
                    "since",
                    "until",
                    "outcome",
                    "offset",
                    "limit",
                    "mode",
                    "source_checkpoint",
                ),
                result=("decision_date", "outcome", "target_range", "source_url"),
                refusals=(
                    Refusal("INVALID_OUTCOME", "the outcome is not hike, cut or hold"),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "read-onchain-and-etf-panel",
        (
            ToolStep(
                "coinglass_macro_snapshot",
                params=(
                    "dataset",
                    "license_tag",
                    "mode",
                    "ticker",
                    "source_checkpoint",
                ),
                result=("items", "dataset", "license_tag"),
                refusals=(
                    Refusal(
                        "CREDENTIAL_MISSING",
                        "the server-side credential reference resolves to nothing",
                    ),
                    Refusal(
                        "INVALID_DATASET",
                        "ticker is required for etf_fund_flows and invalid for other datasets",
                    ),
                    Refusal("READ_FAILED", "the provider read failed"),
                ),
            ),
        ),
    ),
)

LINKS = (
    SurfaceLink(
        "rank-crypto-assets",
        tools=("cmc_listings",),
        prompts=("bellwether-operator", "bellwether-crypto-analyst"),
        skills=("bellwether-crypto-reference",),
    ),
    SurfaceLink(
        "quote-crypto-symbols",
        tools=("cmc_listings", "cmc_quotes"),
        prompts=("bellwether-operator", "bellwether-crypto-analyst"),
        skills=("bellwether-crypto-reference",),
    ),
    SurfaceLink(
        "read-crypto-market-metrics",
        tools=("cmc_global_metrics",),
        prompts=("bellwether-operator", "bellwether-crypto-analyst"),
        skills=("bellwether-crypto-reference",),
    ),
    SurfaceLink(
        "read-a-macro-series",
        tools=("fred_macro_series_aliases", "fred_series_observations"),
        prompts=("bellwether-operator", "bellwether-macro-analyst"),
        skills=("bellwether-macro-series",),
    ),
    SurfaceLink(
        "reconstruct-a-series-as-of",
        tools=("fred_series_vintage_dates", "fred_series_observations_asof"),
        prompts=("bellwether-operator", "bellwether-macro-analyst"),
        skills=("bellwether-macro-series",),
    ),
    SurfaceLink(
        "list-fomc-decisions",
        tools=("fomc_calendar_list",),
        prompts=("bellwether-operator", "bellwether-macro-analyst"),
        skills=("bellwether-fomc-calendar",),
    ),
    SurfaceLink(
        "read-onchain-and-etf-panel",
        tools=("coinglass_macro_snapshot",),
        prompts=(
            "bellwether-operator",
            "bellwether-crypto-analyst",
            "bellwether-macro-analyst",
        ),
        skills=("bellwether-macro-panel",),
    ),
)

LOCATIONS = (
    DataLocation(
        "crypto-market-reference",
        ("Instrument", "Listing"),
        "BELLWETHER_CMC_BASE_URL",
        "cmc_listings",
        federation_key="symbol",
    ),
    DataLocation(
        "fred-macro-series",
        ("MacroSeries", "MacroObservation"),
        "BELLWETHER_FRED_BASE_URL",
        "fred_series_observations",
        route_param="series_id",
        federation_key="series_id",
    ),
    DataLocation(
        "fomc-decision-calendar",
        ("MacroEvent",),
        "bellwether_mcp/connectors/fomc_meetings.json",
        "fomc_calendar_list",
        federation_key="decision_date",
    ),
    DataLocation(
        "coinglass-macro-panel",
        ("MacroObservation",),
        "BELLWETHER_COINGLASS_API_KEY",
        "coinglass_macro_snapshot",
        route_param="dataset",
    ),
)

ROLES = (
    BusinessRole(
        "macro-analyst",
        tasks=(
            "read-a-macro-series",
            "reconstruct-a-series-as-of",
            "list-fomc-decisions",
            "read-onchain-and-etf-panel",
        ),
    ),
    BusinessRole(
        "crypto-analyst",
        tasks=(
            "rank-crypto-assets",
            "quote-crypto-symbols",
            "read-crypto-market-metrics",
            "read-onchain-and-etf-panel",
        ),
    ),
)
