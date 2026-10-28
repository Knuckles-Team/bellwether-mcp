"""Shared validation for zero-based offset pages."""


def validate_offset_page(offset: int, limit: int) -> None:
    """Refuse invalid page bounds before calling a provider."""
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError("page offset must be a nonnegative integer")
    if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
        raise ValueError("page limit must be a positive integer")
