"""Deterministic exact-match policy evaluation helpers."""

from __future__ import annotations

from .models import ExecutionRequest, StrictModel, PolicySnapshot, ToolManifest


class PolicyDecision(StrictModel):
    """Captures the outcome of a deterministic policy evaluation."""

    allowed: bool
    request_id: str
    policy_id: str
    policy_version: str
    action: str
    resource_id: str
    tool_id: str
    reasons: list[str]
    denied_reasons: list[str]


class PolicyDeniedError(Exception):
    """Raised when a request is denied by the local policy snapshot."""

    def __init__(self, decision: PolicyDecision) -> None:
        self.decision = decision
        message = ", ".join(decision.denied_reasons) or "policy_denied"
        super().__init__(message)


def evaluate_policy(
    request: ExecutionRequest,
    policy: PolicySnapshot,
    tool_manifest: ToolManifest | None = None,
) -> PolicyDecision:
    """Evaluate a request against exact-match policy and optional tool manifest constraints."""
    reasons: list[str] = []
    denied_reasons: list[str] = []

    if request.action in policy.allowed_actions:
        reasons.append("action_allowed")
    else:
        denied_reasons.append("action_not_allowed")

    if request.resource_id in policy.allowed_resources:
        reasons.append("resource_allowed")
    else:
        denied_reasons.append("resource_not_allowed")

    if request.tool_id in policy.allowed_tools:
        reasons.append("tool_allowed")
    else:
        denied_reasons.append("tool_not_allowed")

    if tool_manifest is not None:
        if request.tool_id == tool_manifest.tool_id:
            reasons.append("tool_manifest_id_matches")
        else:
            denied_reasons.append("tool_manifest_id_mismatch")

        if request.action in tool_manifest.allowed_operations:
            reasons.append("tool_manifest_allows_action")
        else:
            denied_reasons.append("tool_manifest_action_not_allowed")

    return PolicyDecision(
        allowed=not denied_reasons,
        request_id=request.request_id,
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
        action=request.action,
        resource_id=request.resource_id,
        tool_id=request.tool_id,
        reasons=reasons,
        denied_reasons=denied_reasons,
    )


def assert_policy_allows(
    request: ExecutionRequest,
    policy: PolicySnapshot,
    tool_manifest: ToolManifest | None = None,
) -> PolicyDecision:
    """Return the decision when allowed or raise a typed denial exception."""
    decision = evaluate_policy(request, policy, tool_manifest)
    if not decision.allowed:
        raise PolicyDeniedError(decision)
    return decision
