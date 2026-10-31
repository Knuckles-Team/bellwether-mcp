"""Credential references for the two keyed sources (CoinMarketCap, FRED).

Every value is resolved through ``scion_sdk.credentials`` at call
time — never read directly from ``os.environ``, never logged, never cached to
disk, never embedded in a fixture, and never accepted as an MCP tool argument.
"""

from __future__ import annotations

from scion_sdk.credentials.references import parse_secret_reference
from scion_sdk.credentials.resolver import (
    CompositeCredentialResolver,
    CredentialResolver,
    CredentialUnavailableError,
    EnvironmentCredentialResolver,
)

from bellwether_mcp.config import ENV_PREFIX, env_name

__all__ = [
    "CredentialUnavailableError",
    "CMC_API_KEY_REFERENCE",
    "FRED_API_KEY_REFERENCE",
    "COINGLASS_API_KEY_REFERENCE",
    "default_resolver",
    "resolve_cmc_api_key",
    "resolve_fred_api_key",
    "resolve_coinglass_api_key",
]

#: ``env://`` is the default; a deployment may repoint either to
#: ``openbao://apps/bellwether-mcp#<field>`` via the same-named environment
#: variable holding an ``openbao://`` reference instead.
CMC_API_KEY_REFERENCE = "env://BELLWETHER_CMC_API_KEY"
FRED_API_KEY_REFERENCE = "env://BELLWETHER_FRED_API_KEY"
COINGLASS_API_KEY_REFERENCE = "env://BELLWETHER_COINGLASS_API_KEY"


def _with_deprecated_prefix(reference: str) -> str:
    """Read ``BELLWETHER_<KEY>`` (deprecated) when only the old variable is set."""
    prefix = "env://" + ENV_PREFIX
    if not reference.startswith(prefix):
        return reference
    return "env://" + env_name(reference[len(prefix) :])


def default_resolver() -> CredentialResolver:
    """The environment resolver; OpenBao is added by the deployment composition root."""
    return CompositeCredentialResolver({"env": EnvironmentCredentialResolver()})


def _resolve(reference: str, resolver: CredentialResolver | None) -> str:
    return (resolver or default_resolver()).resolve(
        parse_secret_reference(_with_deprecated_prefix(reference))
    )


def resolve_cmc_api_key(resolver: CredentialResolver | None = None) -> str:
    """Return the CoinMarketCap Pro API key.

    Raises:
        CredentialUnavailableError: the reference is not resolvable.
    """
    return _resolve(CMC_API_KEY_REFERENCE, resolver)


def resolve_fred_api_key(resolver: CredentialResolver | None = None) -> str:
    """Return the FRED/ALFRED API key.

    Raises:
        CredentialUnavailableError: the reference is not resolvable.
    """
    return _resolve(FRED_API_KEY_REFERENCE, resolver)


def resolve_coinglass_api_key(resolver: CredentialResolver | None = None) -> str:
    """Return the configured CoinGlass API key."""
    return _resolve(COINGLASS_API_KEY_REFERENCE, resolver)
