"""Every declared preset validates, and the adapter factory wires it correctly.

Regression coverage for the schema-mapping collision this factory must avoid:
all seven ``macro_series_*`` streams share ``doc_type="macro_series_observation"``
(they differ only by which FRED series they pull) — keying by ``doc_type``
would silently collapse them onto whichever preset happened to be read first.
"""

from __future__ import annotations

import json
from pathlib import Path

from bellwether_mcp.connectors.adapters import (
    build_schema_mappings,
    build_source_adapters,
)

_PRESETS_PATH = (
    Path(__file__).resolve().parent.parent
    / "bellwether_mcp/connectors/mcp_source_presets.json"
)

#: stream name -> the exact (provisional) finance-v1 class this lane's design assigns it.
_EXPECTED_CLASSES = {
    "crypto_listings_cmc": "Instrument",
    "crypto_global_metrics_cmc": "MacroEvent",
    "macro_series_fed_balance_sheet": "EconomicIndicator",
    "macro_series_treasury_general_account": "EconomicIndicator",
    "macro_series_m2_money_stock": "EconomicIndicator",
    "macro_series_reverse_repo_overnight": "EconomicIndicator",
    "macro_series_bank_reserve_balances": "EconomicIndicator",
    "macro_series_treasury_10y_yield": "EconomicIndicator",
    "macro_series_dollar_index_broad": "EconomicIndicator",
    "fomc_calendar": "MacroEvent",
}


def test_every_declared_preset_has_an_expected_class() -> None:
    presets = json.loads(_PRESETS_PATH.read_text())
    names = {name for name in presets if not name.startswith("_")}
    assert names == set(_EXPECTED_CLASSES)


def test_schema_mappings_do_not_collide_across_shared_doc_types() -> None:
    mappings = build_schema_mappings()
    for stream, expected_class in _EXPECTED_CLASSES.items():
        assert mappings[stream].ontology_class == expected_class

    # Every macro_series_* preset shares one doc_type but must stay 7
    # independently addressable streams, not collapse into one.
    macro_streams = [s for s in mappings if s.startswith("macro_series_")]
    assert len(macro_streams) == 7


def test_each_macro_series_preset_targets_a_distinct_fred_alias() -> None:
    presets = json.loads(_PRESETS_PATH.read_text())
    aliases = {
        name: raw["arguments"]["alias"]
        for name, raw in presets.items()
        if name.startswith("macro_series_")
    }
    assert len(aliases) == len(set(aliases.values())), (
        "aliases must be distinct per preset"
    )


def test_build_source_adapters_constructs_one_per_preset() -> None:
    adapters = build_source_adapters()
    assert len(adapters) == len(_EXPECTED_CLASSES)
    streams = {adapter.stream for adapter in adapters}
    assert streams == set(_EXPECTED_CLASSES)
    for adapter in adapters:
        descriptor = adapter.describe()
        assert descriptor.kind == "mcp_tool"
        assert descriptor.certified_for_ingestion is True
