from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jsonschema import validate

from verifiable_tool_invocation_flow.hashing import sha256_digest
from verifiable_tool_invocation_flow.models import ExecutionRequest, PolicySnapshot, ToolManifest, ToolOutput
from verifiable_tool_invocation_flow.policy_checker import evaluate_policy
from verifiable_tool_invocation_flow.receipt_builder import build_signed_receipt
from verifiable_tool_invocation_flow.signer import ReceiptSigner

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"
SCHEMAS_DIR = Path(__file__).resolve().parents[1] / "schemas"
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


def _build_receipt(*, tool_output: dict[str, object] | None = None) -> tuple[ReceiptSigner, dict[str, object]]:
    request = _load_request()
    policy = _load_policy()
    manifest = _load_manifest()
    actual_tool_output = tool_output or _load_tool_output()
    decision = evaluate_policy(request, policy, manifest)
    signer = ReceiptSigner.generate_demo()
    receipt = build_signed_receipt(
        request,
        policy,
        manifest,
        request.tool_input,
        actual_tool_output,
        decision,
        signer,
        receipt_id="receipt-001",
        execution_id="exec-001",
        tool_call_id="call-001",
        nonce="nonce-001",
        audience="demo-validator",
        issuer="agent-receipt-demo-signer",
        issued_at=FIXED_ISSUED_AT,
        expires_at=FIXED_EXPIRES_AT,
        tool_started_at=FIXED_STARTED_AT,
        tool_ended_at=FIXED_ENDED_AT,
        status="success",
    )
    return signer, receipt


def test_build_signed_receipt_has_required_fields() -> None:
    _, receipt = _build_receipt()

    required_fields = {
        "profile_version",
        "receipt_id",
        "execution_id",
        "request_id",
        "nonce",
        "audience",
        "issued_at",
        "expires_at",
        "agent_id",
        "resource_id",
        "action",
        "tool_id",
        "policy_id",
        "policy_version",
        "input_hash",
        "policy_hash",
        "tool_manifest_hash",
        "tool_input_hash",
        "tool_output_hash",
        "result_hash",
        "pre_execution_commitment",
        "policy_decision",
        "issuer",
        "public_key_id",
        "signature_alg",
        "signature",
        "tool_call",
    }

    assert required_fields.issubset(receipt)
    assert receipt["signature"].startswith("base64:")
    assert receipt["signature_alg"] == "Ed25519"
    assert {"tool_call_id", "started_at", "ended_at", "status", "tool_input_hash", "tool_output_hash"}.issubset(
        receipt["tool_call"]
    )


def test_receipt_hashes_match_source_artifacts() -> None:
    _, receipt = _build_receipt()
    request = _load_request()
    policy = _load_policy()
    manifest = _load_manifest()
    tool_input = request.tool_input
    tool_output = _load_tool_output()

    assert receipt["input_hash"] == sha256_digest(request)
    assert receipt["policy_hash"] == sha256_digest(policy)
    assert receipt["tool_manifest_hash"] == sha256_digest(manifest)
    assert receipt["tool_input_hash"] == sha256_digest(tool_input)
    assert receipt["tool_output_hash"] == sha256_digest(tool_output)
    assert receipt["result_hash"] == receipt["tool_output_hash"]


def test_pre_execution_commitment_excludes_tool_output() -> None:
    first_output = _load_tool_output()
    second_output = {
        **first_output,
        "metadata": {
            **first_output["metadata"],
            "owner": "other-owner",
        },
    }

    _, first_receipt = _build_receipt(tool_output=first_output)
    _, second_receipt = _build_receipt(tool_output=second_output)

    assert first_receipt["pre_execution_commitment"] == second_receipt["pre_execution_commitment"]
    assert first_receipt["tool_output_hash"] != second_receipt["tool_output_hash"]
    assert first_receipt["result_hash"] != second_receipt["result_hash"]


def test_signature_verifies_for_signed_receipt() -> None:
    signer, receipt = _build_receipt()

    assert signer.verify_mapping(receipt, receipt["signature"])
    assert signer.verify_mapping(receipt, receipt["signature"], public_key_pem=signer.public_key_pem())


def test_signed_receipt_tampering_fails_signature() -> None:
    signer, receipt = _build_receipt()
    tampered = {**receipt, "action": "tampered_action"}

    assert not signer.verify_mapping(tampered, receipt["signature"])


def test_execution_receipt_schema_accepts_built_receipt() -> None:
    _, receipt = _build_receipt()
    schema = json.loads((SCHEMAS_DIR / "execution_receipt.schema.json").read_text(encoding="utf-8"))

    validate(instance=receipt, schema=schema)
