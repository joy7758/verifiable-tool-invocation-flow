# verifiable-tool-invocation-flow

Minimal, testable building blocks for a CrewAI Flow that emits verifiable execution evidence for sensitive tool calls.

## Current Scope

This repository currently implements:

- deterministic canonical JSON serialization
- SHA-256 hashing helpers
- typed Pydantic models for the demo request, policy, manifest, and tool output
- in-memory Ed25519 signing and verification for canonical JSON payloads
- example JSON inputs
- tests for canonicalization, hashing, and signatures

Not implemented yet:

- policy enforcement
- receipt building
- validation CLI
- CrewAI Flow runtime

## Signing Note

`ReceiptSigner` signs canonical JSON payloads with Ed25519 and verifies signatures independently of any Flow runtime.

For mapping payloads, the signer excludes only the top-level `signature` field from the signed body.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[test]"
pytest
```

## Current Guarantee Boundary

The current code guarantees deterministic canonical serialization, stable SHA-256 hashing for equivalent JSON content, and verifiable Ed25519 signatures over canonical payloads.

It does not yet guarantee receipt construction, policy correctness, replay protection, or independent validation.
