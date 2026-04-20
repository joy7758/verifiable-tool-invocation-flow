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


def _build_valid_case(*, signer: ReceiptSigner | None = None, audience: str = "demo-validator") -> tuple[ReceiptSigner, dict[str, object], dict[str, object]]:
    request = _load_request()
    policy = _load_policy()
    manifest = _load_manifest()
    tool_output = _load_tool_output()
    decision = evaluate_policy(request, policy, manifest)
    actual_signer = signer or ReceiptSigner.generate_demo()
    receipt = build_signed_receipt(
        request,
        policy,
        manifest,
        request.tool_input,
        tool_output,
        decision,
        actual_signer,
        receipt_id="receipt-001",
        execution_id="exec-001",
        tool_call_id="call-001",
        nonce="nonce-001",
        audience=audience,
        issued_at=FIXED_ISSUED_AT,
        expires_at=FIXED_EXPIRES_AT,
        tool_started_at=FIXED_STARTED_AT,
        tool_ended_at=FIXED_ENDED_AT,
        status="success",
    )
    evidence_bundle = build_evidence_bundle(request, policy, manifest, request.tool_input, tool_output)
    return actual_signer, receipt, evidence_bundle


def test_validator_detects_tampered_tool_output() -> None:
    signer, receipt, evidence_bundle = _build_valid_case()
    evidence_bundle["tool_output"] = {
        **evidence_bundle["tool_output"],
        "metadata": {
            **evidence_bundle["tool_output"]["metadata"],
            "owner": "tampered-owner",
        },
    }

    report = validate_receipt(receipt, evidence_bundle, signer.public_key_pem(), checked_at=FIXED_ISSUED_AT)

    assert report["verdict"] == "invalid"
    assert report["tool_output_hash_match"] is False
    assert report["result_hash_match"] is False


def test_validator_detects_tampered_receipt_field() -> None:
    signer, receipt, evidence_bundle = _build_valid_case()
    tampered_receipt = {**receipt, "action": "tampered_action"}

    report = validate_receipt(tampered_receipt, evidence_bundle, signer.public_key_pem(), checked_at=FIXED_ISSUED_AT)

    assert report["verdict"] == "invalid"
    assert report["signature_valid"] is False
    assert report["request_binding_match"] is False


def test_validator_detects_wrong_audience() -> None:
    signer, receipt, evidence_bundle = _build_valid_case(audience="demo-validator")

    report = validate_receipt(receipt, evidence_bundle, signer.public_key_pem(), audience="other-validator", checked_at=FIXED_ISSUED_AT)

    assert report["verdict"] == "invalid"
    assert report["audience_match"] is False


def test_validator_detects_expired_receipt() -> None:
    signer = ReceiptSigner.generate_demo()
    request = _load_request()
    policy = _load_policy()
    manifest = _load_manifest()
    tool_output = _load_tool_output()
    decision = evaluate_policy(request, policy, manifest)
    expired_receipt = build_signed_receipt(
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
        expires_at=FIXED_ISSUED_AT + timedelta(minutes=1),
        tool_started_at=FIXED_STARTED_AT,
        tool_ended_at=FIXED_ENDED_AT,
        status="success",
    )
    evidence_bundle = build_evidence_bundle(request, policy, manifest, request.tool_input, tool_output)

    report = validate_receipt(
        expired_receipt,
        evidence_bundle,
        signer.public_key_pem(),
        checked_at=FIXED_ISSUED_AT + timedelta(minutes=2),
    )

    assert report["verdict"] == "invalid"
    assert report["time_window_valid"] is False


def test_validator_detects_wrong_public_key() -> None:
    signer_a, receipt, evidence_bundle = _build_valid_case()
    signer_b = ReceiptSigner.generate_demo()

    report = validate_receipt(receipt, evidence_bundle, signer_b.public_key_pem(), checked_at=FIXED_ISSUED_AT)

    assert report["verdict"] == "invalid"
    assert report["signature_valid"] is False


def test_validator_returns_invalid_report_for_schema_failure() -> None:
    signer, receipt, evidence_bundle = _build_valid_case()
    invalid_receipt = dict(receipt)
    invalid_receipt.pop("nonce")

    report = validate_receipt(invalid_receipt, evidence_bundle, signer.public_key_pem(), checked_at=FIXED_ISSUED_AT)

    assert report["verdict"] == "invalid"
    assert report["schema_valid"] is False
