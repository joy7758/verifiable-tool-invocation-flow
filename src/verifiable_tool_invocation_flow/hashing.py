"""Hashing helpers built on top of canonical JSON serialization."""

from __future__ import annotations

import hashlib
from typing import Any

from .canonical import canonical_bytes


def sha256_hex(value: Any) -> str:
    """Return the hexadecimal SHA-256 digest for a JSON-compatible payload."""
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_digest(value: Any) -> str:
    """Return the prefixed SHA-256 digest for a JSON-compatible payload."""
    return f"sha256:{sha256_hex(value)}"
