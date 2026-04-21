# Secure & Verifiable Tool Invocation Flow

[![PyPI version](https://img.shields.io/pypi/v/verifiable-tool-invocation-flow)](https://pypi.org/project/verifiable-tool-invocation-flow/0.1.1/)
[![GitHub release](https://img.shields.io/github/v/release/joy7758/verifiable-tool-invocation-flow?sort=semver)](https://github.com/joy7758/verifiable-tool-invocation-flow/releases/tag/v0.1.1)
[![GitHub Marketplace Action](https://img.shields.io/badge/GitHub%20Marketplace-Verify%20Agent%20Execution%20Receipt-blue?logo=github)](https://github.com/marketplace/actions/verify-agent-execution-receipt)

This CrewAI Flow template wraps a sensitive agent tool call with policy checking, evidence capture, signed execution receipts, and independent validation reports.

The default demo requires no LLM API key and no network access.

## Project overview

A one-page overview of the public assets, quickstart paths, and research scope is available here:

- [Agent Receipt Validator Ecosystem](docs/public_landing_note.md)

## Live demo

A Hugging Face Spaces demo is available for validating signed execution receipts against evidence bundles:

- [Agent Receipt Validator Space](https://huggingface.co/spaces/joy7759/agent-receipt-validator)

The demo is for inspection and experimentation only. Do not upload private keys, production receipts, confidential evidence bundles, API tokens, or sensitive data.

## Related public assets

This project is also available through related integration surfaces:

- Core PyPI package: https://pypi.org/project/verifiable-tool-invocation-flow/0.1.1/
- GitHub Marketplace Action: https://github.com/marketplace/actions/verify-agent-execution-receipt
- Hugging Face validator demo: https://huggingface.co/spaces/joy7759/agent-receipt-validator
- MCP server package: https://pypi.org/project/agent-receipt-validator-mcp/0.1.1/
- MCP server repository: https://github.com/joy7758/agent-receipt-validator-mcp

The MCP server exposes local stdio tools for validating signed agent execution receipts from MCP-compatible clients.

The MCP server validates signed execution evidence. It does not prove semantic correctness of tool outputs, certify legal compliance, or replace sandboxing, IAM, access control, monitoring, or human approval.

## What this template does

- Checks whether a tool invocation is allowed by an exact-match policy snapshot and tool manifest.
- Captures deterministic evidence for one specific tool invocation.
- Signs the resulting execution receipt with Ed25519.
- Validates the receipt independently against the request, policy snapshot, tool manifest, tool input, and tool output.
- Produces a CrewAI Flow wrapper that orchestrates the existing reusable modules without reimplementing them.

## When to use it

- Sensitive dataset metadata access.
- Controlled API or tool calls that need audit evidence.
- Compliance-oriented agent workflows.
- Accountable data operations.
- Data-space-like environments that need portable execution evidence.
- Audit-oriented agent tool execution where runtime and verification should be separable.

## What it guarantees

- It generates deterministic evidence for a specific tool invocation.
- It signs the execution receipt with Ed25519.
- It validates that the receipt matches the request, policy snapshot, tool manifest, tool input, and tool output.
- It detects tampering of receipt or evidence artifacts.
- It validates audience binding, request binding, policy alignment, time window, and signature.
- It optionally detects replay when replay cache is enabled.

## What it does NOT guarantee

This template provides verifiable execution evidence for a tool invocation.
It does not prove semantic correctness of the tool output.
It does not prove that the policy itself is correct.
It does not protect against a compromised signer.
It does not replace sandboxing, IAM, access control, monitoring, or human approval.
It does not require or expose raw chain-of-thought.
It is not a full FDO, Gaia-X, IDS, or EDC implementation.

## Architecture

```text
ExecutionRequest
  -> PolicySnapshot / ToolManifest
  -> guarded_tool_call()
  -> demo_metadata_lookup_tool()
  -> evidence_bundle.json
  -> execution_receipt.json
  -> independent validator
  -> verification_report.json
```

The CrewAI Flow is only orchestration. The reusable core is `guarded_tool_call()`. The validator can run outside the agent runtime.

## Repository layout

- `src/verifiable_tool_invocation_flow/`: reusable modules, demo tool, validator, and Flow wrapper.
- `schemas/`: JSON Schema for receipts and verification reports.
- `examples/`: deterministic demo request, policy, manifest, tool input, and tool output fixtures.
- `tests/`: unit and integration tests for hashing, signing, policy, receipts, validation, guarded calls, and Flow orchestration.
- `docs/`: architecture, assumptions, threat model, integration guidance, and marketplace submission material.
- `outputs/`: generated demo artifacts. Git tracks only `outputs/.gitkeep`.

## Requirements

- Python `>=3.10,<3.14`
- CrewAI
- `cryptography`
- `pydantic`
- `jsonschema`
- `pytest` for tests

CrewAI currently does not support Python 3.14 for this project. Use Python 3.10, 3.11, 3.12, or 3.13.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
python -m verifiable_tool_invocation_flow.main
```

```bash
uv sync
uv run python -m verifiable_tool_invocation_flow.main
```

If the CrewAI CLI is available in a supported Python environment:

```bash
crewai run
```

## Expected outputs

- `outputs/evidence_bundle.json`
- `outputs/execution_receipt.json`
- `outputs/verification_report.json`
- `outputs/demo_public_key.pem`

`demo_public_key.pem` is public and safe to write. No private key is written. `outputs/` is ignored by Git except `outputs/.gitkeep`.

## Run the independent validator

```bash
python -m verifiable_tool_invocation_flow.validator \
  --receipt outputs/execution_receipt.json \
  --evidence outputs/evidence_bundle.json \
  --public-key outputs/demo_public_key.pem \
  --audience demo-validator \
  --out outputs/verification_report.cli.json
```

## Use in your own Flow

```python
from verifiable_tool_invocation_flow.guarded_tool_call import guarded_tool_call
from verifiable_tool_invocation_flow.signer import ReceiptSigner

result = guarded_tool_call(
    request=request,
    policy=policy_snapshot,
    tool_manifest=tool_manifest,
    tool_input=tool_input,
    tool_fn=my_sensitive_tool,
    signer=ReceiptSigner.generate_demo(),
)

if result.verification_report["verdict"] != "valid":
    raise RuntimeError("Tool invocation could not be verified")
```

## Validator rules

- `schema_valid`
- `input_hash_match`
- `policy_hash_match`
- `tool_manifest_hash_match`
- `tool_input_hash_match`
- `tool_output_hash_match`
- `result_hash_match`
- `pre_execution_commitment_match`
- `policy_decision_valid`
- `signature_valid`
- `time_window_valid`
- `replay_check_performed`
- `replay_detected`
- `audience_match`
- `request_binding_match`

## Replay protection

Replay protection is disabled unless `replay_cache_path` is provided. The built-in replay cache is file-based and demo-level only. Production systems should use a shared durable replay store.

## Security assumptions

The validator assumes authentic public-key distribution, stable canonical JSON rules, and access to the receipt plus evidence bundle. See [docs/security_assumptions.md](docs/security_assumptions.md).

## Threat model

The threat model covers tampering, policy mismatch, replay, wrong audience, wrong public key, compromised signer, and guarantee-boundary misunderstandings. See [docs/threat_model.md](docs/threat_model.md).

## FDO / Data Space mapping

This template provides an FDO/Data-Space-like mapping for demonstration only. It is not a full implementation of FDO, Gaia-X, IDS, or EDC. See [docs/fdo_dataspace_mapping.md](docs/fdo_dataspace_mapping.md).

## Marketplace submission note

Marketplace-ready project naming, descriptions, categories, and submission checklist are in [docs/marketplace_submission_note.md](docs/marketplace_submission_note.md).

## Support and commercial integration

This project is open-source infrastructure for verifiable agent execution evidence.

For public technical questions, use GitHub Issues. For private integration, validator adaptation, CI/CD receipt verification, CrewAI workflow integration, or FDO/Data-Space-like evidence mapping, see:

- [SUPPORT.md](SUPPORT.md)
- [COMMERCIAL_SUPPORT.md](COMMERCIAL_SUPPORT.md)

GitHub Sponsors is not currently enabled for this account. Funding links may be added later once a sponsorship channel is active.
