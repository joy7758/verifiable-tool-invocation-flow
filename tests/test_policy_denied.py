from __future__ import annotations

import json
from pathlib import Path

import pytest

from verifiable_tool_invocation_flow.models import ExecutionRequest, PolicySnapshot, ToolManifest
from verifiable_tool_invocation_flow.policy_checker import (
    PolicyDeniedError,
    assert_policy_allows,
    evaluate_policy,
)

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def _load_request() -> ExecutionRequest:
    return ExecutionRequest.model_validate(
        json.loads((EXAMPLES_DIR / "input_request.json").read_text(encoding="utf-8"))
    )


def _load_policy() -> PolicySnapshot:
    return PolicySnapshot.model_validate(
        json.loads((EXAMPLES_DIR / "policy_snapshot.json").read_text(encoding="utf-8"))
    )


def _load_manifest() -> ToolManifest:
    return ToolManifest.model_validate(
        json.loads((EXAMPLES_DIR / "tool_manifest.json").read_text(encoding="utf-8"))
    )


def test_policy_allows_valid_request() -> None:
    request = _load_request()
    policy = _load_policy()
    manifest = _load_manifest()

    decision = evaluate_policy(request, policy, manifest)

    assert decision.allowed is True
    assert decision.denied_reasons == []
    assert "action_allowed" in decision.reasons
    assert "resource_allowed" in decision.reasons
    assert "tool_allowed" in decision.reasons
    assert "tool_manifest_allows_action" in decision.reasons
    assert assert_policy_allows(request, policy, manifest) == decision


def test_policy_denies_unlisted_action() -> None:
    request = _load_request().model_copy(update={"action": "read_raw_data"})
    policy = _load_policy()
    manifest = _load_manifest().model_copy(update={"allowed_operations": ["metadata.lookup"]})

    decision = evaluate_policy(request, policy, manifest)

    assert decision.allowed is False
    assert "action_not_allowed" in decision.denied_reasons
    assert "tool_manifest_action_not_allowed" in decision.denied_reasons
    with pytest.raises(PolicyDeniedError) as exc_info:
        assert_policy_allows(request, policy, manifest)
    assert exc_info.value.decision == decision


def test_policy_denies_unlisted_resource() -> None:
    request = _load_request().model_copy(update={"resource_id": "dataset/unknown"})
    policy = _load_policy()
    manifest = _load_manifest()

    decision = evaluate_policy(request, policy, manifest)

    assert decision.allowed is False
    assert "resource_not_allowed" in decision.denied_reasons


def test_policy_denies_unlisted_tool() -> None:
    request = _load_request().model_copy(update={"tool_id": "unknown_tool"})
    policy = _load_policy()
    manifest = _load_manifest().model_copy(update={"tool_id": "unknown_tool"})

    decision = evaluate_policy(request, policy, manifest)

    assert decision.allowed is False
    assert "tool_not_allowed" in decision.denied_reasons


def test_policy_denies_tool_manifest_action_mismatch() -> None:
    request = _load_request()
    policy = _load_policy()
    manifest = _load_manifest().model_copy(update={"allowed_operations": ["metadata.write"]})

    decision = evaluate_policy(request, policy, manifest)

    assert decision.allowed is False
    assert "tool_manifest_action_not_allowed" in decision.denied_reasons


def test_policy_denies_tool_manifest_id_mismatch() -> None:
    request = _load_request()
    policy = _load_policy()
    manifest = _load_manifest().model_copy(update={"tool_id": "other_tool"})

    decision = evaluate_policy(request, policy, manifest)

    assert decision.allowed is False
    assert "tool_manifest_id_mismatch" in decision.denied_reasons
