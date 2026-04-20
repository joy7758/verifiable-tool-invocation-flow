"""Deterministic canonical JSON helpers."""

from __future__ import annotations

import dataclasses
import json
import math
from datetime import date, datetime, time
from enum import Enum
from typing import Any, TypeAlias

from pydantic import BaseModel

JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]


def normalize_json_value(value: Any) -> JSONValue:
    """Convert supported Python values into a deterministic JSON-safe form."""
    if isinstance(value, BaseModel):
        return normalize_json_value(value.model_dump(mode="json"))

    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return normalize_json_value(dataclasses.asdict(value))

    if isinstance(value, dict):
        normalized: dict[str, JSONValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"JSON object keys must be strings, got {type(key).__name__}")
            normalized[key] = normalize_json_value(item)
        return normalized

    if isinstance(value, (list, tuple)):
        return [normalize_json_value(item) for item in value]

    if value is None or isinstance(value, (str, bool)):
        return value

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Canonical JSON rejects NaN and infinite floats")
        return value

    if isinstance(value, Enum):
        return normalize_json_value(value.value)

    if isinstance(value, (datetime, date, time)):
        return value.isoformat()

    raise TypeError(f"Unsupported value for canonical JSON: {type(value).__name__}")


def canonical_json(value: Any) -> str:
    """Serialize a value using a stable JSON representation."""
    return json.dumps(
        normalize_json_value(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def canonical_bytes(value: Any) -> bytes:
    """Return canonical JSON encoded as UTF-8 bytes."""
    return canonical_json(value).encode("utf-8")
