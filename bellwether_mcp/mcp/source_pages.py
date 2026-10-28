"""Delta checkpoint envelope for bounded source reads."""

from typing import Any
from uuid import uuid4


def _page_parts(result: dict[str, Any]) -> tuple[list[dict[str, Any]], int, int]:
    items = result.get("items")
    offset, limit = result.get("offset"), result.get("limit")
    if (
        not isinstance(items, list)
        or any(not isinstance(item, dict) for item in items)
        or type(offset) is not int
        or type(limit) is not int
    ):
        raise ValueError("invalid source page")
    return items, offset, limit


def _records(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            key: value
            for key, value in item.items()
            if value is not None and not (key == "realtime_end" and value == "")
        }
        for item in items
    ]


def source_page(result: dict[str, Any], mode: str) -> dict[str, Any]:
    """Preserve legacy responses; identify each delta extraction separately."""
    if mode == "":
        return result
    if mode != "delta":
        raise ValueError("source pages require delta mode")
    items, offset, limit = _page_parts(result)
    next_offset = offset + len(items) if len(items) >= limit and limit > 0 else 0
    return {
        **result,
        "items": _records(items),
        "checkpoint": {"offset": next_offset, "generation": uuid4().hex},
    }
