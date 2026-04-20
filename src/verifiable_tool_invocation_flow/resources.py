"""Helpers for reading packaged JSON resources from the installed distribution."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


def load_example_json(filename: str) -> dict[str, Any]:
    """Load an example JSON document bundled with the package."""
    return _load_json_resource("examples", filename)


def load_schema_json(filename: str) -> dict[str, Any]:
    """Load a JSON schema document bundled with the package."""
    return _load_json_resource("schemas", filename)


def _load_json_resource(directory: str, filename: str) -> dict[str, Any]:
    resource = files("verifiable_tool_invocation_flow").joinpath(directory, filename)
    payload = json.loads(resource.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in packaged resource {directory}/{filename}")
    return payload
