"""Helpers for building signed execution receipts."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from secrets import token_hex
from typing import Any
from uuid import uuid4

from .canonical import normalize_json_value
from .hashing import sha256_digest
from .models import ExecutionReceipt, ExecutionRequest, PolicySnapshot, ReceiptToolCall, ToolManifest
from .policy_checker import PolicyDecision
from .signer import ReceiptSigner

PROFILE_VERSION = "agent-execution-receipt-profile/0.1"
DEFAULT_AUDIENCE = "demo-validator"
DEFAULT_ISSUER = "agent-receipt-demo-signer"
DEFAULT_SIGNATURE_ALG = "Ed25519"


def isoformat_z(dt: datetime) -> str:
    """Format a timezone-aware datetime as a UTC ISO-8601 string ending in Z."""
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("Expected a timezone-aware datetime")
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def build_evidence_bundle(
    request: ExecutionRequest,
    policy: PolicySnapshot,
    tool_manifest: ToolManifest,
    tool_input: Mapping[str, Any],
    tool_output: Mapping[str, Any],
) -> dict[str, Any]:
    """Collect the source artifacts needed to understand a single invocation."""
    return {
        "request": _to_json_object(request),
        "policy": _to_json_object(policy),
        "tool_manifest": _to_json_object(tool_manifest),
        "tool_input": _to_json_object(tool_input),
        "tool_output": _to_json_object(tool_output),
    }


def build_unsigned_receipt(
    request: ExecutionRequest,
    policy: PolicySnapshot,
    tool_manifest: ToolManifest,
    tool_input: Mapping[str, Any],
    tool_output: Mapping[str, Any],
    policy_decision: PolicyDecision,
    *,
    execution_id: str | None = None,
    receipt_id: str | None = None,
    tool_call_id: str | None = None,
    nonce: str | None = None,
    audience: str = DEFAULT_AUDIENCE,
    issuer: str = DEFAULT_ISSUER,
    issued_at: datetime | None = None,
    expires_at: datetime | None = None,
    tool_started_at: datetime | None = None,
    tool_ended_at: datetime | None = None,
    status: str = "success",
    public_key_id: str = "demo-ed25519-key-001",
) -> dict[str, Any]:
    """Build an unsigned execution receipt as a JSON-serializable mapping."""
    tool_input_payload = _to_json_object(tool_input)
    tool_output_payload = _to_json_object(tool_output)

    issued_at_value = issued_at or _utc_now()
    expires_at_value = expires_at or (issued_at_value + timedelta(minutes=10))
    tool_started_at_value = tool_started_at or issued_at_value
    tool_ended_at_value = tool_ended_at or issued_at_value

    execution_id_value = execution_id or request.execution_id or _prefixed_id("exec-")
    receipt_id_value = receipt_id or _prefixed_id("receipt-")
    tool_call_id_value = tool_call_id or _prefixed_id("call-")
    nonce_value = nonce or request.nonce or _generate_nonce()

    input_hash = sha256_digest(request)
    policy_hash = sha256_digest(policy)
    tool_manifest_hash = sha256_digest(tool_manifest)
    tool_input_hash = sha256_digest(tool_input_payload)
    tool_output_hash = sha256_digest(tool_output_payload)
    result_hash = tool_output_hash

    pre_execution_commitment = sha256_digest(
        {
            "request_id": request.request_id,
            "execution_id": execution_id_value,
            "nonce": nonce_value,
            "audience": audience,
            "input_hash": input_hash,
            "policy_hash": policy_hash,
            "tool_manifest_hash": tool_manifest_hash,
            "tool_input_hash": tool_input_hash,
        }
    )

    tool_call = ReceiptToolCall(
        tool_call_id=tool_call_id_value,
        started_at=isoformat_z(tool_started_at_value),
        ended_at=isoformat_z(tool_ended_at_value),
        status=status,
        tool_input_hash=tool_input_hash,
        tool_output_hash=tool_output_hash,
    )

    receipt = ExecutionReceipt(
        profile_version=PROFILE_VERSION,
        receipt_id=receipt_id_value,
        execution_id=execution_id_value,
        request_id=request.request_id,
        nonce=nonce_value,
        audience=audience,
        issued_at=isoformat_z(issued_at_value),
        expires_at=isoformat_z(expires_at_value),
        agent_id=request.agent_id,
        resource_id=request.resource_id,
        action=request.action,
        tool_id=request.tool_id,
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
        input_hash=input_hash,
        policy_hash=policy_hash,
        tool_manifest_hash=tool_manifest_hash,
        tool_input_hash=tool_input_hash,
        tool_output_hash=tool_output_hash,
        result_hash=result_hash,
        pre_execution_commitment=pre_execution_commitment,
        policy_decision=_to_json_object(policy_decision),
        issuer=issuer,
        public_key_id=public_key_id,
        signature_alg=DEFAULT_SIGNATURE_ALG,
        signature="",
        tool_call=tool_call,
    )
    return receipt.model_dump(mode="json")


def build_signed_receipt(
    request: ExecutionRequest,
    policy: PolicySnapshot,
    tool_manifest: ToolManifest,
    tool_input: Mapping[str, Any],
    tool_output: Mapping[str, Any],
    policy_decision: PolicyDecision,
    signer: ReceiptSigner,
    **kwargs: Any,
) -> dict[str, Any]:
    """Build and sign an execution receipt."""
    if "public_key_id" not in kwargs:
        kwargs["public_key_id"] = signer.public_key_id()

    receipt = build_unsigned_receipt(
        request,
        policy,
        tool_manifest,
        tool_input,
        tool_output,
        policy_decision,
        **kwargs,
    )
    receipt["signature"] = signer.sign_mapping(receipt)
    return receipt


def _to_json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        normalized = normalize_json_value(dict(value))
    else:
        normalized = normalize_json_value(value)
    if not isinstance(normalized, dict):
        raise TypeError("Expected a JSON object")
    return normalized


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _prefixed_id(prefix: str) -> str:
    return f"{prefix}{uuid4()}"


def _generate_nonce() -> str:
    return token_hex(16)
