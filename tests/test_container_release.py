"""The released-wheel image refresh uses the shared public payload guard."""

import tomllib
from pathlib import Path


def test_release_generator_uses_existing_ontology():
    root = Path(__file__).resolve().parents[1]
    config = tomllib.loads((root / "pyproject.toml").read_text())
    stem = config["tool"]["pipelines"]["ontology"]["ttl"]
    assert stem == "market_data"
    assert (root / "bellwether_mcp" / "ontology" / f"{stem}.ttl").is_file()
