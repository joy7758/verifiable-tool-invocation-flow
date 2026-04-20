# Architecture

## Purpose

This project separates agent-side tool execution from independent verification. The runtime path produces evidence and a signed receipt. The audit path recomputes hashes, checks bindings, verifies the signature, and returns a verification report without depending on the original Flow execution context.

## Execution and validation split

The execution side is responsible for:

- loading the request, policy snapshot, and tool manifest
- checking whether the tool invocation is allowed
- running the tool only after policy approval
- capturing deterministic evidence
- building and signing the execution receipt

The validation side is responsible for:

- validating receipt schema
- recomputing hashes from the evidence bundle
- checking request, audience, and policy bindings
- recomputing the pre-execution commitment
- verifying the Ed25519 signature
- checking the receipt time window
- optionally checking replay indicators

This split is deliberate. For audit use cases, the validator should be able to run outside the original agent runtime.

## Flow role

`SecureToolInvocationFlow` is orchestration only. It loads demo inputs, calls `guarded_tool_call()`, and writes:

- `evidence_bundle.json`
- `execution_receipt.json`
- `verification_report.json`
- `demo_public_key.pem`

It does not reimplement signing, policy logic, receipt building, or validation rules.

## Reusable modules

- `guarded_tool_call`: reusable wrapper that coordinates policy evaluation, tool execution, receipt building, and post-call validation.
- `receipt_builder`: builds deterministic evidence bundles, pre-execution commitments, unsigned receipts, and signed receipts.
- `signer`: Ed25519 signing and verification over canonical JSON payloads.
- `validator`: independent receipt verification as a Python module and CLI.
- `policy_checker`: exact-match policy checks with structured allow and deny reasons.
- `demo_metadata_lookup_tool`: deterministic demo tool used by the example Flow.

## Evidence artifacts

`evidence_bundle.json` contains the request, policy snapshot, tool manifest, tool input, and tool output.

`execution_receipt.json` binds those artifacts together using deterministic hashes, policy decision metadata, execution identifiers, and an Ed25519 signature.

`verification_report.json` records whether the validator could independently confirm schema validity, hash consistency, bindings, signature validity, time window validity, and optional replay status.

## Why external validation matters

If the same runtime that executes the tool also performs the only verification, audit evidence is much weaker. This template is built so that the validator can be run later, elsewhere, with only:

- the signed receipt
- the evidence bundle
- the public key

That is the core architectural boundary the template is trying to demonstrate.
