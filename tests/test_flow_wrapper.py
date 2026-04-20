from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("crewai.flow.flow", reason="CrewAI Flow runtime is required for Task 7 tests")

from verifiable_tool_invocation_flow.flows.secure_tool_invocation_flow import SecureToolInvocationFlow
from verifiable_tool_invocation_flow.main import kickoff


def test_secure_tool_invocation_flow_kickoff_returns_valid_summary(tmp_path: Path) -> None:
    flow = SecureToolInvocationFlow(output_dir=tmp_path)

    result = flow.kickoff()

    assert result["verdict"] == "valid"
    assert flow.state.evidence_bundle is not None
    assert flow.state.receipt is not None
    assert flow.state.verification_report is not None
    assert flow.state.verification_report["verdict"] == "valid"


def test_secure_tool_invocation_flow_writes_outputs(tmp_path: Path) -> None:
    flow = SecureToolInvocationFlow(output_dir=tmp_path)

    result = flow.kickoff()

    evidence_path = Path(result["evidence_bundle_path"])
    receipt_path = Path(result["receipt_path"])
    report_path = Path(result["verification_report_path"])
    public_key_path = Path(result["public_key_path"])

    assert evidence_path.exists()
    assert receipt_path.exists()
    assert report_path.exists()
    assert public_key_path.exists()
    assert "BEGIN PUBLIC KEY" in public_key_path.read_text(encoding="utf-8")
    assert not (tmp_path / "demo_private_key.pem").exists()

    verification_report = json.loads(report_path.read_text(encoding="utf-8"))
    assert verification_report["verdict"] == "valid"


def test_main_kickoff_function(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("VTIF_OUTPUT_DIR", str(tmp_path))

    result = kickoff()

    assert result["verdict"] == "valid"
