from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from verifiable_tool_invocation_flow.models import ExecutionRequest, PolicySnapshot, ToolManifest, ToolOutput
from verifiable_tool_invocation_flow.policy_checker import evaluate_policy
from verifiable_tool_invocation_flow.receipt_builder import build_evidence_bundle, build_signed_receipt
from verifiable_tool_invocation_flow.signer import ReceiptSigner
from verifiable_tool_invocation_flow.validator import validate_receipt

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"
FIXED_ISSUED_AT = datetime(2026, 4, 21, 10, 0, 0, tzinfo=timezone.utc)
FIXED_EXPIRES_AT = FIXED_ISSUED_AT + timedelta(minutes=10)
FIXED_STARTED_AT = FIXED_ISSUED_AT
FIXED_ENDED_AT = FIXED_ISSUED_AT + timedelta(seconds=2)
FIXED_CHECKED_AT = FIXED_ISSUED_AT + timedelta(minutes=5)


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


def _load_tool_output() -> dict[str, object]:
    tool_output = ToolOutput.model_validate(
        json.loads((EXAMPLES_DIR / "tool_output.json").read_text(encoding="utf-8"))
    )
    return tool_output.output


def test_validate_receipt_valid_case() -> None:
    request = _load_request()
    policy = _load_policy()
    manifest = _load_manifest()
    tool_output = _load_tool_output()
    decision = evaluate_policy(request, policy, manifest)
    signer = ReceiptSigner.generate_demo()
    receipt = build_signed_receipt(
        request,
        policy,
        manifest,
        request.tool_input,
        tool_output,
        decision,
        signer,
        receipt_id="receipt-001",
        execution_id="exec-001",
        tool_call_id="call-001",
        nonce="nonce-001",
        issued_at=FIXED_ISSUED_AT,
        expires_at=FIXED_EXPIRES_AT,
        tool_started_at=FIXED_STARTED_AT,
        tool_ended_at=FIXED_ENDED_AT,
        status="success",
    )
    evidence_bundle = build_evidence_bundle(request, policy, manifest, request.tool_input, tool_output)

    report = validate_receipt(
        receipt,
        evidence_bundle,
        signer.public_key_pem(),
        audience="demo-validator",
        checked_at=FIXED_CHECKED_AT,
        replay_cache_path=None,
    )

    assert report["verdict"] == "valid"
    assert report["schema_valid"] is True
    assert report["input_hash_match"] is True
    assert report["policy_hash_match"] is True
    assert report["tool_manifest_hash_match"] is True
    assert report["tool_input_hash_match"] is True
    assert report["tool_output_hash_match"] is True
    assert report["result_hash_match"] is True
    assert report["pre_execution_commitment_match"] is True
    assert report["policy_decision_valid"] is True
    assert report["signature_valid"] is True
    assert report["time_window_valid"] is True
    assert report["replay_check_performed"] is False
    assert report["replay_detected"] is False
    assert report["audience_match"] is True
    assert report["request_binding_match"] is True
