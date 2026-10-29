"""The released-wheel image refresh uses the shared public payload guard."""

import tomllib
from pathlib import Path

import yaml


def test_release_generator_uses_existing_ontology():
    root = Path(__file__).resolve().parents[1]
    config = tomllib.loads((root / "pyproject.toml").read_text())
    stem = config["tool"]["pipelines"]["ontology"]["ttl"]
    assert stem == "market_data"
    assert (root / "bellwether_mcp" / "ontology" / f"{stem}.ttl").is_file()


def test_public_wheel_preflight_precedes_container_publication():
    root = Path(__file__).resolve().parents[1]
    workflow = yaml.safe_load(
        (root / ".github/workflows/container-release.yml").read_text()
    )
    jobs = workflow["jobs"]
    steps = jobs["verify-public-wheel"]["steps"]
    guard = next(
        step
        for step in steps
        if step.get("uses", "").endswith("/verify-release-version")
    )
    assert guard["with"] == {
        "mode": "published-wheel",
        "distribution": "bellwether-mcp",
        "module": "bellwether_mcp",
    }
    assert jobs["publish-docker"]["needs"] == "verify-public-wheel"
    assert (
        jobs["publish-docker"]["uses"]
        == "Knuckles-Team/pipelines/.github/workflows/container_pipeline.yml@main"
    )
