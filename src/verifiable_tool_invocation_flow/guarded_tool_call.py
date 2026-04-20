"""Reusable guarded tool execution wrapper."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .canonical import normalize_json_value
from .models import ExecutionRequest, PolicySnapshot, ToolManifest
from .policy_checker import PolicyDecision, assert_policy_allows
from .receipt_builder import build_evidence_bundle, build_signed_receipt
from .signer import ReceiptSigner
from .validator import validate_receipt


@dataclass(frozen=True)
class GuardedToolCallResult:
    """Structured result for a successful guarded tool invocation."""

    tool_output: dict[str, Any]
    evidence_bundle: dict[str, Any]
    receipt: dict[str, Any]
    verification_report: dict[str, Any]
    policy_decision: PolicyDecision


class GuardedToolCallVerificationError(ValueError):
    """Raised when post-call independent validation does not produce a valid verdict."""

    def __init__(self, verification_report: Mapping[str, Any]) -> None:
        self.verification_report = dict(verification_report)
        super().__init__("guarded tool call verification failed")


def guarded_tool_call(
    request: ExecutionRequest,
    policy: PolicySnapshot,
    tool_manifest: ToolManifest,
    tool_input: Mapping[str, Any],
    tool_fn: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    signer: ReceiptSigner,
    *,
    public_key_pem: bytes | None = None,
    audience: str = "demo-validator",
    issuer: str = "agent-receipt-demo-signer",
    checked_at: datetime | None = None,
    replay_cache_path: Path | None = None,
    update_replay_cache: bool = False,
    receipt_kwargs: Mapping[str, Any] | None = None,
) -> GuardedToolCallResult:
    """Execute a tool only after deterministic policy approval, then build and verify its receipt."""
    policy_decision = assert_policy_allows(request, policy, tool_manifest)

    normalized_tool_input = _ensure_json_object(tool_input, label="tool_input")
    raw_tool_output = tool_fn(normalized_tool_input)
    normalized_tool_output = _ensure_json_object(raw_tool_output, label="tool_output")

    evidence_bundle = build_evidence_bundle(
        request,
        policy,
        tool_manifest,
        normalized_tool_input,
        normalized_tool_output,
    )

    receipt_options = dict(receipt_kwargs or {})
    receipt_options.setdefault("audience", audience)
    receipt_options.setdefault("issuer", issuer)

    receipt = build_signed_receipt(
        request,
        policy,
        tool_manifest,
        normalized_tool_input,
        normalized_tool_output,
        policy_decision,
        signer,
        **receipt_options,
    )

    effective_public_key_pem = public_key_pem or signer.public_key_pem()
    verification_report = validate_receipt(
        receipt,
        evidence_bundle,
        effective_public_key_pem,
        audience=audience,
        checked_at=checked_at,
        replay_cache_path=replay_cache_path,
        update_replay_cache=update_replay_cache,
    )

    if verification_report["verdict"] != "valid":
        raise GuardedToolCallVerificationError(verification_report)

    return GuardedToolCallResult(
        tool_output=normalized_tool_output,
        evidence_bundle=evidence_bundle,
        receipt=receipt,
        verification_report=verification_report,
        policy_decision=policy_decision,
    )


def _ensure_json_object(value: Any, *, label: str) -> dict[str, Any]:
    normalized = normalize_json_value(dict(value) if isinstance(value, Mapping) else value)
    if not isinstance(normalized, dict):
        raise TypeError(f"{label} must be a JSON-serializable mapping")
    return normalized
