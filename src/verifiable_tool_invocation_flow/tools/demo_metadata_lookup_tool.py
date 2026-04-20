"""Deterministic demo metadata lookup tool."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_DEMO_RESOURCE_ID = "fdo:demo-dataset-001"
_DEMO_METADATA = {
    "title": "Demo Dataset 001",
    "creator": "Verifiable Tool Invocation Flow",
    "license": "CC-BY-4.0",
}


def demo_metadata_lookup_tool(tool_input: Mapping[str, Any]) -> dict[str, Any]:
    """Return deterministic metadata for the single supported demo resource."""
    resource_id = tool_input.get("resource_id")
    if resource_id != _DEMO_RESOURCE_ID:
        raise ValueError(f"unsupported resource_id: {resource_id!r}")

    requested_fields = tool_input.get("metadata_fields")
    metadata = _filter_metadata(requested_fields)

    return {
        "resource_id": _DEMO_RESOURCE_ID,
        "metadata": metadata,
        "access_type": "metadata_only",
    }


def _filter_metadata(requested_fields: Any) -> dict[str, str]:
    if requested_fields is None:
        return dict(_DEMO_METADATA)
    if not isinstance(requested_fields, list) or not all(isinstance(field, str) for field in requested_fields):
        raise ValueError("metadata_fields must be a list of strings")
    return {field: _DEMO_METADATA[field] for field in requested_fields if field in _DEMO_METADATA}
