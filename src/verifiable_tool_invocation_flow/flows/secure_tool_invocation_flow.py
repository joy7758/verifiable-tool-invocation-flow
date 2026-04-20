"""CrewAI flow wrapper for the secure tool invocation demo."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from crewai.flow.flow import Flow, FlowState, listen, start

from ..guarded_tool_call import guarded_tool_call
from ..models import ExecutionRequest, PolicySnapshot, ToolManifest
from ..resources import load_example_json
from ..signer import ReceiptSigner
from ..tools.demo_metadata_lookup_tool import demo_metadata_lookup_tool


class SecureToolInvocationState(FlowState):
    """State shared across the secure tool invocation flow."""

    request: dict[str, Any] | None = None
    policy: dict[str, Any] | None = None
    tool_manifest: dict[str, Any] | None = None
    tool_input: dict[str, Any] | None = None
    tool_output: dict[str, Any] | None = None
    evidence_bundle: dict[str, Any] | None = None
    receipt: dict[str, Any] | None = None
    verification_report: dict[str, Any] | None = None
    policy_decision: dict[str, Any] | None = None
    public_key_pem: str | None = None
    output_dir: str = "outputs"


class SecureToolInvocationFlow(Flow[SecureToolInvocationState]):
    """Demo Flow wrapper that orchestrates the guarded tool invocation path."""

    def __init__(self, output_dir: str | Path | None = None) -> None:
        super().__init__()
        if output_dir is not None:
            self.state.output_dir = str(output_dir)

    @start()
    def load_demo_inputs(self):
        """Load the example request, policy, manifest, and tool input into state."""
        request = ExecutionRequest.model_validate(load_example_json("input_request.json"))
        policy = PolicySnapshot.model_validate(load_example_json("policy_snapshot.json"))
        tool_manifest = ToolManifest.model_validate(load_example_json("tool_manifest.json"))
        tool_input = load_example_json("tool_input.json")

        self.state.request = request.model_dump(mode="json")
        self.state.policy = policy.model_dump(mode="json")
        self.state.tool_manifest = tool_manifest.model_dump(mode="json")
        self.state.tool_input = tool_input
        return {"loaded": True, "input_dir": "package:verifiable_tool_invocation_flow/examples"}

    @listen(load_demo_inputs)
    def run_guarded_tool_call(self, _loaded_inputs: dict[str, Any]):
        """Execute the deterministic guarded tool call using the existing reusable module."""
        request = ExecutionRequest.model_validate(dict(self.state.request or {}))
        policy = PolicySnapshot.model_validate(dict(self.state.policy or {}))
        tool_manifest = ToolManifest.model_validate(dict(self.state.tool_manifest or {}))
        tool_input = dict(self.state.tool_input or {})

        signer = ReceiptSigner.generate_demo()
        issued_at = datetime.now(timezone.utc).replace(microsecond=0)
        checked_at = issued_at + timedelta(seconds=5)
        result = guarded_tool_call(
            request,
            policy,
            tool_manifest,
            tool_input,
            demo_metadata_lookup_tool,
            signer,
            audience="demo-validator",
            checked_at=checked_at,
            replay_cache_path=None,
            update_replay_cache=False,
            receipt_kwargs={
                "receipt_id": "receipt-flow-001",
                "execution_id": request.execution_id,
                "tool_call_id": "call-flow-001",
                "nonce": request.nonce,
                "issued_at": issued_at,
                "expires_at": issued_at + timedelta(minutes=10),
                "tool_started_at": issued_at,
                "tool_ended_at": issued_at + timedelta(seconds=2),
                "status": "success",
            },
        )

        self.state.tool_output = result.tool_output
        self.state.evidence_bundle = result.evidence_bundle
        self.state.receipt = result.receipt
        self.state.verification_report = result.verification_report
        self.state.policy_decision = result.policy_decision.model_dump(mode="json")
        self.state.public_key_pem = signer.public_key_pem().decode("utf-8")
        return {"guarded_call_completed": True, "verdict": result.verification_report["verdict"]}

    @listen(run_guarded_tool_call)
    def write_outputs(self, _guarded_result: dict[str, Any]):
        """Write the demo evidence artifacts and public key to the configured output directory."""
        output_dir = Path(self.state.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        evidence_path = output_dir / "evidence_bundle.json"
        receipt_path = output_dir / "execution_receipt.json"
        report_path = output_dir / "verification_report.json"
        public_key_path = output_dir / "demo_public_key.pem"

        _write_json(evidence_path, _to_plain_json(self.state.evidence_bundle))
        _write_json(receipt_path, _to_plain_json(self.state.receipt))
        _write_json(report_path, _to_plain_json(self.state.verification_report))
        public_key_path.write_text(self.state.public_key_pem or "", encoding="utf-8")

        summary = {
            "receipt_path": str(receipt_path),
            "evidence_bundle_path": str(evidence_path),
            "verification_report_path": str(report_path),
            "public_key_path": str(public_key_path),
            "verdict": (self.state.verification_report or {}).get("verdict", "invalid"),
        }
        return summary
def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _to_plain_json(value: Any) -> Any:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return {str(key): _to_plain_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_plain_json(item) for item in value]
    return value
