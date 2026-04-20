# verifiable-tool-invocation-flow

Minimal, testable building blocks for a CrewAI Flow that emits verifiable execution evidence for sensitive tool calls.

## Task 1 Scope

This repository currently implements only the Task 1 baseline:

- deterministic canonical JSON serialization
- SHA-256 hashing helpers
- typed Pydantic models for the demo request, policy, manifest, and tool output
- example JSON inputs
- tests for canonicalization and hash stability

Not implemented yet:

- signatures
- policy enforcement
- receipt building
- validation CLI
- CrewAI Flow runtime

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[test]"
pytest
```

## Current Guarantee Boundary

The current code guarantees only deterministic canonical serialization and stable SHA-256 hashing for equivalent JSON content.

It does not yet guarantee signed receipts, policy correctness, replay protection, or independent validation.
