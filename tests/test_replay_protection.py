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


def _build_valid_case() -> tuple[ReceiptSigner, dict[str, object], dict[str, object]]:
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
    return signer, receipt, evidence_bundle


def test_replay_cache_detects_second_use(tmp_path: Path) -> None:
    signer, receipt, evidence_bundle = _build_valid_case()
    replay_cache = tmp_path / "replay_cache.json"

    first_report = validate_receipt(
        receipt,
        evidence_bundle,
        signer.public_key_pem(),
        checked_at=FIXED_ISSUED_AT,
        replay_cache_path=replay_cache,
    )
    second_report = validate_receipt(
        receipt,
        evidence_bundle,
        signer.public_key_pem(),
        checked_at=FIXED_ISSUED_AT + timedelta(seconds=1),
        replay_cache_path=replay_cache,
    )

    assert first_report["verdict"] == "valid"
    assert first_report["replay_check_performed"] is True
    assert first_report["replay_detected"] is False

    assert second_report["verdict"] == "invalid"
    assert second_report["replay_check_performed"] is True
    assert second_report["replay_detected"] is True


def test_replay_check_disabled_without_cache() -> None:
    signer, receipt, evidence_bundle = _build_valid_case()

    first_report = validate_receipt(receipt, evidence_bundle, signer.public_key_pem(), checked_at=FIXED_ISSUED_AT)
    second_report = validate_receipt(
        receipt,
        evidence_bundle,
        signer.public_key_pem(),
        checked_at=FIXED_ISSUED_AT + timedelta(seconds=1),
    )

    assert first_report["verdict"] == "valid"
    assert second_report["verdict"] == "valid"
    assert first_report["replay_check_performed"] is False
    assert second_report["replay_check_performed"] is False
    assert first_report["replay_detected"] is False
    assert second_report["replay_detected"] is False
