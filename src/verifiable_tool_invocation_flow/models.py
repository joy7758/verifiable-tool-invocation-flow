"""Typed models for the Task 1 demo evidence inputs."""

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
