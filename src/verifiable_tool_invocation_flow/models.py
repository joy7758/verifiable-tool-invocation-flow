"""Typed models for the core demo evidence inputs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .canonical import canonical_json
from .hashing import sha256_digest


class StrictModel(BaseModel):
    """Shared base model with strict input handling."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    def to_canonical_json(self) -> str:
        """Serialize the model into canonical JSON."""
        return canonical_json(self)

    def to_sha256_digest(self) -> str:
        """Compute the canonical SHA-256 digest for the model."""
        return sha256_digest(self)


class ExecutionRequest(StrictModel):
    """Represents a requested tool invocation before execution."""

    request_id: str
    execution_id: str
    nonce: str
    audience: str
    agent_id: str
    resource_id: str
    action: str
    tool_id: str
    tool_input: dict[str, Any] = Field(default_factory=dict)
    requested_at: str


class PolicySnapshot(StrictModel):
    """Represents the policy state consulted for a guarded invocation."""

    policy_id: str
    policy_version: str
    description: str | None = None
    allowed_actions: list[str]
    allowed_resources: list[str]
    allowed_tools: list[str]
    issued_at: str


class ToolManifest(StrictModel):
    """Describes the expected interface of the guarded tool."""

    tool_id: str
    tool_name: str
    tool_version: str
    description: str | None = None
    allowed_operations: list[str] = Field(default_factory=list)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)


class ToolOutput(StrictModel):
    """Captures the demo tool result payload."""

    execution_id: str
    tool_id: str
    status: Literal["succeeded", "failed"]
    output: dict[str, Any] = Field(default_factory=dict)
    produced_at: str


class ReceiptToolCall(StrictModel):
    """Captures the hashed tool call details embedded in a receipt."""

    tool_call_id: str
    started_at: str
    ended_at: str
    status: str
    tool_input_hash: str
    tool_output_hash: str


class ExecutionReceipt(StrictModel):
    """Represents a signed execution receipt for one tool invocation."""

    profile_version: str
    receipt_id: str
    execution_id: str
    request_id: str
    nonce: str
    audience: str
    issued_at: str
    expires_at: str
    agent_id: str
    resource_id: str
    action: str
    tool_id: str
    policy_id: str
    policy_version: str
    input_hash: str
    policy_hash: str
    tool_manifest_hash: str
    tool_input_hash: str
    tool_output_hash: str
    result_hash: str
    pre_execution_commitment: str
    policy_decision: dict[str, Any]
    issuer: str
    public_key_id: str
    signature_alg: str
    signature: str
    tool_call: ReceiptToolCall


class VerificationReport(StrictModel):
    """Represents the outcome of independent receipt verification."""

    receipt_id: str
    execution_id: str
    profile_version: str
    checked_at: str
    schema_valid: bool
    input_hash_match: bool
    policy_hash_match: bool
    tool_manifest_hash_match: bool
    tool_input_hash_match: bool
    tool_output_hash_match: bool
    result_hash_match: bool
    pre_execution_commitment_match: bool
    policy_decision_valid: bool
    signature_valid: bool
    time_window_valid: bool
    replay_check_performed: bool
    replay_detected: bool
    audience_match: bool
    request_binding_match: bool
    verdict: Literal["valid", "invalid"]
    errors: list[str]
    warnings: list[str]
