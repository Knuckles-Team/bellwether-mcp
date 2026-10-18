"""Package-specific validation errors raised by the MCP tool surface."""

from __future__ import annotations

__all__ = ["UnknownFredSeriesAliasError", "UnknownFomcOutcomeFilterError"]


class UnknownFredSeriesAliasError(ValueError):
    """A caller asked for a named macro-series alias this package does not ship."""


class UnknownFomcOutcomeFilterError(ValueError):
    """A caller filtered the FOMC calendar by an outcome this dataset does not use."""
