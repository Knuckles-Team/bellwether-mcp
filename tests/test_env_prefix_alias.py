"""BELLWETHER_ settings, with the pre-rename MARKET_DATA_ prefix as a deprecated alias."""

from __future__ import annotations

import pytest

from bellwether_mcp import credentials
from bellwether_mcp.config import env_name


def test_new_prefix_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BELLWETHER_FRED_BASE_URL", "https://new")
    monkeypatch.setenv("MARKET_DATA_FRED_BASE_URL", "https://old")
    assert env_name("FRED_BASE_URL") == "BELLWETHER_FRED_BASE_URL"


def test_old_prefix_is_read_with_a_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BELLWETHER_FRED_BASE_URL", raising=False)
    monkeypatch.setenv("MARKET_DATA_FRED_BASE_URL", "https://old")
    with pytest.warns(DeprecationWarning, match="MARKET_DATA_FRED_BASE_URL"):
        assert env_name("FRED_BASE_URL") == "MARKET_DATA_FRED_BASE_URL"


def test_credential_falls_back_to_the_old_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("BELLWETHER_FRED_API_KEY", raising=False)
    monkeypatch.setenv("MARKET_DATA_FRED_API_KEY", "legacy-test-key")
    with pytest.warns(DeprecationWarning):
        assert credentials.resolve_fred_api_key() == "legacy-test-key"
