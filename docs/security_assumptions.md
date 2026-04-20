# Security Assumptions

## Assumptions

- The validator has access to the execution receipt and the matching evidence bundle.
- The public key used by the validator is authentic.
- The signing key has not been compromised.
- Canonical JSON rules remain stable and deterministic across signer and validator runs.
- The policy snapshot used for validation is the same policy snapshot that was committed before execution.
- The validator can run outside the agent runtime.
- Evidence artifacts are transported without silent substitution between producer and validator.

## What this enables

Under those assumptions, the validator can detect:

- receipt tampering
- evidence tampering
- request binding mismatches
- audience mismatches
- signature mismatches
- time-window failures
- optional replay reuse when a replay cache is enabled

## Out of scope

- Runtime sandboxing.
- Tool-side truth verification.
- Compromised signing key detection.
- Malicious policy author detection.
- Raw chain-of-thought capture.
- Full FDO or data-space connector implementation.
- Complete supply-chain security.

## Practical reading

This template is designed to prove that a specific tool invocation was recorded consistently and can be rechecked later. It is not designed to prove that every surrounding trust assumption was sound.
