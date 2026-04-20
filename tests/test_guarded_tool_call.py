from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from verifiable_tool_invocation_flow.guarded_tool_call import (
    GuardedToolCallVerificationError,
    guarded_tool_call,
)
from verifiable_tool_invocation_flow.models import ExecutionRequest, PolicySnapshot, ToolManifest
from verifiable_tool_invocation_flow.policy_checker import PolicyDeniedError
from verifiable_tool_invocation_flow.signer import ReceiptSigner
from verifiable_tool_invocation_flow.tools import demo_metadata_lookup_tool

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"
FIXED_ISSUED_AT = datetime(2026, 4, 21, 10, 0, 0, tzinfo=timezone.utc)
FIXED_EXPIRES_AT = FIXED_ISSUED_AT + timedelta(minutes=10)
FIXED_STARTED_AT = FIXED_ISSUED_AT
FIXED_ENDED_AT = FIXED_ISSUED_AT + timedelta(seconds=2)
FIXED_CHECKED_AT = FIXED_ISSUED_AT + timedelta(minutes=5)


def _load_tool_input() -> dict[str, object]:
    return json.loads((EXAMPLES_DIR / "tool_input.json").read_text(encoding="utf-8"))


def _make_request(*, action: str = "metadata.lookup") -> ExecutionRequest:
    return ExecutionRequest(
        request_id="req-guarded-001",
        execution_id="exec-guarded-001",
        nonce="nonce-guarded-001",
        audience="demo-validator",
        agent_id="agent-demo",
        resource_id="fdo:demo-dataset-001",
        action=action,
        tool_id="demo_metadata_lookup",
        tool_input=_load_tool_input(),
        requested_at="2026-04-21T10:00:00Z",
    )


def _make_policy() -> PolicySnapshot:
    return PolicySnapshot(
        policy_id="policy-guarded-001",
        policy_version="2026-04-21.1",
        description="Allow metadata lookup on the demo FDO dataset.",
        allowed_actions=["metadata.lookup"],
        allowed_resources=["fdo:demo-dataset-001"],
        allowed_tools=["demo_metadata_lookup"],
        issued_at="2026-04-21T09:55:00Z",
    )


def _make_manifest() -> ToolManifest:
    return ToolManifest(
        tool_id="demo_metadata_lookup",
        tool_name="Demo Metadata Lookup Tool",
        tool_version="0.1.0",
        description="Returns deterministic metadata for the demo FDO dataset.",
        allowed_operations=["metadata.lookup"],
        input_schema={
            "type": "object",
            "required": ["resource_id", "metadata_fields"],
        },
        output_schema={
            "type": "object",
            "required": ["resource_id", "metadata", "access_type"],
        },
    )


def _receipt_kwargs() -> dict[str, object]:
    return {
        "receipt_id": "receipt-guarded-001",
        "execution_id": "exec-guarded-001",
        "tool_call_id": "call-guarded-001",
        "nonce": "nonce-guarded-001",
        "issued_at": FIXED_ISSUED_AT,
        "expires_at": FIXED_EXPIRES_AT,
        "tool_started_at": FIXED_STARTED_AT,
        "tool_ended_at": FIXED_ENDED_AT,
        "status": "success",
    }


def test_guarded_tool_call_success() -> None:
    request = _make_request()
    policy = _make_policy()
    manifest = _make_manifest()
    tool_input = _load_tool_input()
    signer = ReceiptSigner.generate_demo()

    result = guarded_tool_call(
        request,
        policy,
        manifest,
        tool_input,
        demo_metadata_lookup_tool,
        signer,
        checked_at=FIXED_CHECKED_AT,
        receipt_kwargs=_receipt_kwargs(),
    )

    assert result.tool_output["metadata"]["title"] == "Demo Dataset 001"
    assert result.receipt["signature"].startswith("base64:")
    assert result.verification_report["verdict"] == "valid"
    assert result.policy_decision.allowed is True
    assert {"request", "policy", "tool_manifest", "tool_input", "tool_output"} == set(result.evidence_bundle)


def test_guarded_tool_call_denied_policy_does_not_execute_tool() -> None:
    request = _make_request(action="read_raw_data")
    policy = _make_policy()
    manifest = _make_manifest()
    tool_input = _load_tool_input()
    signer = ReceiptSigner.generate_demo()
    calls = {"count": 0}

    def forbidden_tool(_: object) -> dict[str, object]:
        calls["count"] += 1
        return {"should_not": "run"}

    with pytest.raises(PolicyDeniedError):
        guarded_tool_call(
            request,
            policy,
            manifest,
            tool_input,
            forbidden_tool,
            signer,
            checked_at=FIXED_CHECKED_AT,
            receipt_kwargs=_receipt_kwargs(),
        )

    assert calls["count"] == 0


def test_guarded_tool_call_invalid_verification_raises() -> None:
    request = _make_request()
    policy = _make_policy()
    manifest = _make_manifest()
    tool_input = _load_tool_input()
    signer_a = ReceiptSigner.generate_demo(public_key_id="key-a")
    signer_b = ReceiptSigner.generate_demo(public_key_id="key-b")

    with pytest.raises(GuardedToolCallVerificationError) as exc_info:
        guarded_tool_call(
            request,
            policy,
            manifest,
            tool_input,
            demo_metadata_lookup_tool,
            signer_a,
            public_key_pem=signer_b.public_key_pem(),
            checked_at=FIXED_CHECKED_AT,
            receipt_kwargs=_receipt_kwargs(),
        )

    report = exc_info.value.verification_report
    assert report["signature_valid"] is False
    assert report["verdict"] == "invalid"


def test_demo_metadata_tool_filters_fields() -> None:
    tool_output = demo_metadata_lookup_tool(
        {
            "resource_id": "fdo:demo-dataset-001",
            "metadata_fields": ["title"],
        }
    )

    assert tool_output["metadata"] == {"title": "Demo Dataset 001"}


def test_demo_metadata_tool_rejects_unknown_resource() -> None:
    with pytest.raises(ValueError):
        demo_metadata_lookup_tool(
            {
                "resource_id": "fdo:unknown-dataset",
                "metadata_fields": ["title"],
            }
        )


def test_guarded_tool_call_replay_cache_optional() -> None:
    request = _make_request()
    policy = _make_policy()
    manifest = _make_manifest()
    tool_input = _load_tool_input()
    signer = ReceiptSigner.generate_demo()

    first = guarded_tool_call(
        request,
        policy,
        manifest,
        tool_input,
        demo_metadata_lookup_tool,
        signer,
        checked_at=FIXED_CHECKED_AT,
        replay_cache_path=None,
        receipt_kwargs=_receipt_kwargs(),
    )
    second = guarded_tool_call(
        request,
        policy,
        manifest,
        tool_input,
        demo_metadata_lookup_tool,
        signer,
        checked_at=FIXED_CHECKED_AT,
        replay_cache_path=None,
        receipt_kwargs=_receipt_kwargs(),
    )

    assert first.verification_report["verdict"] == "valid"
    assert second.verification_report["verdict"] == "valid"
    assert first.verification_report["replay_check_performed"] is False
    assert second.verification_report["replay_check_performed"] is False
