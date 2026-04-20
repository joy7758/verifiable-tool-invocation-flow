# verifiable-tool-invocation-flow

Minimal, testable building blocks for a CrewAI Flow that emits verifiable execution evidence for sensitive tool calls.

## Current Scope

This repository currently implements:

- deterministic canonical JSON serialization
- SHA-256 hashing helpers
- typed Pydantic models for the demo request, policy, manifest, and tool output
- in-memory Ed25519 signing and verification for canonical JSON payloads
- exact-match policy evaluation for action, resource, tool, and tool-manifest checks
- signed execution receipt building for one tool invocation
- independent receipt validation against an evidence bundle
- a reusable guarded tool-call wrapper that combines policy checking, receipt building, and independent validation
- example JSON inputs
- JSON Schema for the execution receipt
- JSON Schema for the verification report
- tests for canonicalization, hashing, signatures, policy checks, receipt building, validation, and guarded tool execution

Not implemented yet:

- replay protection

## Signing Note

`ReceiptSigner` signs canonical JSON payloads with Ed25519 and verifies signatures independently of any Flow runtime.

For mapping payloads, the signer excludes only the top-level `signature` field from the signed body.

## Receipt Note

`receipt_builder.py` constructs a signed receipt that binds one request, policy snapshot, tool manifest, tool input, tool output, and policy decision together.

It does not prove semantic correctness of the tool result.

## Validator Note

`validator.py` verifies a signed receipt independently from any Flow runtime and can be used either as a Python module or from the command line with `python -m verifiable_tool_invocation_flow.validator`.

The validator checks schema validity, hashes, request bindings, pre-execution commitment, policy consistency, signature validity, audience, time window, and optional file-based replay detection.

## Guarded Tool Note

`guarded_tool_call.py` is the reusable integration layer for application code and future Flow orchestration. It evaluates policy, executes the tool only if allowed, builds evidence and a signed receipt, validates that receipt independently, and returns the complete result bundle.

It does not implement Flow orchestration or failure receipt variants in this phase.

## Flow Note

`SecureToolInvocationFlow` is the demo orchestration layer. It loads the demo inputs, calls `guarded_tool_call()`, and writes the evidence bundle, receipt, verification report, and public key to `outputs/`.

CrewAI requires Python `>=3.10,<3.14`. Python `3.14` is not currently supported for running `crewai run`.

This project uses the real CrewAI Flow API and is marked as `type = "flow"` for `crewai run` in supported Python environments. If CrewAI is unavailable locally, the Flow tests are skipped explicitly rather than replaced with a compatibility shim.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[test]"
pytest
```

## Current Guarantee Boundary

The current code guarantees deterministic canonical serialization, stable SHA-256 hashing for equivalent JSON content, verifiable Ed25519 signatures over canonical payloads, exact-match policy decisions, signed receipt construction for a single tool invocation, independent receipt verification against evidence bundles, and a reusable guarded wrapper that prevents execution when policy is denied.

It does not yet guarantee policy correctness or semantic correctness of tool outputs.
