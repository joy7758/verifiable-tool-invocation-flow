from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from verifiable_tool_invocation_flow.canonical import canonical_json
from verifiable_tool_invocation_flow.models import ExecutionRequest

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_canonical_json_is_deterministic_for_reordered_keys() -> None:
    left = {
        "tool_input": {"fields": ["owner", "region"], "dataset": "customer-metadata"},
        "tool_id": "demo_metadata_lookup",
        "action": "metadata.lookup",
    }
    right = {
        "action": "metadata.lookup",
        "tool_id": "demo_metadata_lookup",
        "tool_input": {"dataset": "customer-metadata", "fields": ["owner", "region"]},
    }

    assert canonical_json(left) == canonical_json(right)
    assert canonical_json(left) == (
        '{"action":"metadata.lookup","tool_id":"demo_metadata_lookup",'
        '"tool_input":{"dataset":"customer-metadata","fields":["owner","region"]}}'
    )


def test_canonical_json_accepts_pydantic_models() -> None:
    payload = json.loads((EXAMPLES_DIR / "input_request.json").read_text(encoding="utf-8"))
    request = ExecutionRequest.model_validate(payload)

    assert canonical_json(request) == canonical_json(payload)


def test_canonical_json_rejects_nan() -> None:
    with pytest.raises(ValueError):
        canonical_json({"not_allowed": math.nan})
