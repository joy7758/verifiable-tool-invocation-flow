from __future__ import annotations

import json
from pathlib import Path

from verifiable_tool_invocation_flow.hashing import sha256_digest, sha256_hex
from verifiable_tool_invocation_flow.models import ExecutionRequest, PolicySnapshot, ToolManifest, ToolOutput

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def test_sha256_hex_matches_known_canonical_payload() -> None:
    assert sha256_hex({"b": 2, "a": 1}) == "43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777"
    assert sha256_digest({"b": 2, "a": 1}) == (
        "sha256:43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777"
    )


def test_hash_is_stable_for_equivalent_json_content() -> None:
    first = {"payload": {"x": 1, "y": [2, 3]}, "order": ["a", "b"]}
    second = {"order": ["a", "b"], "payload": {"y": [2, 3], "x": 1}}

    assert sha256_digest(first) == sha256_digest(second)


def test_example_files_validate_against_models_and_hash() -> None:
    request = ExecutionRequest.model_validate(
        json.loads((EXAMPLES_DIR / "input_request.json").read_text(encoding="utf-8"))
    )
    policy = PolicySnapshot.model_validate(
        json.loads((EXAMPLES_DIR / "policy_snapshot.json").read_text(encoding="utf-8"))
    )
    manifest = ToolManifest.model_validate(
        json.loads((EXAMPLES_DIR / "tool_manifest.json").read_text(encoding="utf-8"))
    )
    tool_output = ToolOutput.model_validate(
        json.loads((EXAMPLES_DIR / "tool_output.json").read_text(encoding="utf-8"))
    )

    assert request.to_sha256_digest().startswith("sha256:")
    assert policy.to_sha256_digest().startswith("sha256:")
    assert manifest.to_sha256_digest().startswith("sha256:")
    assert tool_output.to_sha256_digest().startswith("sha256:")
