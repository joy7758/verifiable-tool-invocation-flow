# Announcement Pack: Agent Receipt Validator Ecosystem v0.1

## One-line description

A small open-source toolkit for generating, signing, and independently validating execution receipts for sensitive AI agent tool calls.

## Three-sentence description

AI agents increasingly perform tool calls, API calls, and data access operations that need post-execution evidence.
This project provides a minimal receipt and validator pattern: evidence bundle, signed execution receipt, and independent verification report.
It is available as a CrewAI Flow template, Python package, GitHub Action, Hugging Face demo, and MCP server.

## What is included

| Component | Link | Use |
|---|---|---|
| CrewAI Flow template | https://github.com/joy7758/verifiable-tool-invocation-flow | runnable template |
| Core PyPI package | https://pypi.org/project/verifiable-tool-invocation-flow/0.1.1/ | Python toolkit |
| GitHub Action | https://github.com/marketplace/actions/verify-agent-execution-receipt | CI verification |
| Hugging Face Space | https://huggingface.co/spaces/joy7759/agent-receipt-validator | visual demo |
| MCP server repo | https://github.com/joy7758/agent-receipt-validator-mcp | MCP source |
| MCP server PyPI package | https://pypi.org/project/agent-receipt-validator-mcp/0.1.1/ | MCP install |

## What it verifies

- receipt schema
- request hash
- policy snapshot hash
- tool manifest hash
- tool input hash
- tool output hash
- result hash
- pre-execution commitment
- policy decision
- Ed25519 signature
- time window
- audience binding
- request binding
- optional replay indicator

## What it does not claim

This project provides verifiable execution evidence for tool invocations.
It does not prove semantic correctness of the tool output.
It does not prove that the policy itself is correct.
It does not protect against a compromised signer.
It does not replace sandboxing, IAM, access control, monitoring, human approval, or legal compliance review.
It does not require or expose raw chain-of-thought.
It is not a full FDO, Gaia-X, IDS, or EDC implementation.

## CrewAI forum version

I have been working on a small open-source pattern for verifiable AI agent tool execution: signed execution receipts plus independent validation.

The CrewAI version is a runnable Flow template that wraps a sensitive tool call with:

- an exact-match policy snapshot
- a tool manifest
- a guarded tool call
- an evidence bundle
- an Ed25519-signed execution receipt
- an independent verification report

The core reusable piece is `guarded_tool_call()`, so the Flow is mostly orchestration around receipt generation and validation rather than a closed workflow.

Links:

- CrewAI Flow template: https://github.com/joy7758/verifiable-tool-invocation-flow
- Core PyPI package: https://pypi.org/project/verifiable-tool-invocation-flow/0.1.1/
- Visual demo: https://huggingface.co/spaces/joy7759/agent-receipt-validator
- GitHub Action: https://github.com/marketplace/actions/verify-agent-execution-receipt
- MCP server package: https://pypi.org/project/agent-receipt-validator-mcp/0.1.1/

I would appreciate feedback on the receipt profile and validator rules:

- Are the receipt fields minimal enough?
- Which checks should be required by default?
- Should replay detection be mandatory or profile-specific?
- What evidence should be present for third-party audit?

Scope boundary: this validates signed execution evidence. It does not prove semantic correctness of a tool output, replace sandboxing or access control, or certify legal compliance.

## LangChain forum version

I have published a small open-source receipt and validator toolkit for tool-calling agents.

The problem is framework-neutral: after an agent calls a tool, API, or data system, a team may need a portable record of what request was made, which policy snapshot applied, which tool was used, what input and output were recorded, and whether an independent verifier can detect later changes.

The project produces:

- an evidence bundle
- a signed execution receipt
- an independent verification report

The core Python package is not tied to CrewAI. The repository includes a CrewAI Flow template as a runnable example, plus a GitHub Action for CI verification and an MCP server for local MCP-compatible clients.

Links:

- Core repo and template: https://github.com/joy7758/verifiable-tool-invocation-flow
- Core PyPI package: https://pypi.org/project/verifiable-tool-invocation-flow/0.1.1/
- GitHub Action: https://github.com/marketplace/actions/verify-agent-execution-receipt
- Hugging Face demo: https://huggingface.co/spaces/joy7759/agent-receipt-validator
- MCP server repo: https://github.com/joy7758/agent-receipt-validator-mcp
- MCP server PyPI package: https://pypi.org/project/agent-receipt-validator-mcp/0.1.1/

Feedback I am looking for:

- What receipt fields should be mandatory for tool-calling agents?
- Which validator rules belong in a common baseline profile?
- Should the MCP surface expose validation only, or receipt building too?
- What should remain outside the scope of a receipt validator?

Boundary: this provides verifiable execution evidence. It does not prove semantic correctness, replace runtime controls, or guarantee compliance.

## GitHub release announcement

Agent Receipt Validator Ecosystem v0.1 is now available.

This is a small open-source toolkit for signed execution receipts and independent validation of sensitive AI agent tool calls.

Components:

- CrewAI Flow template: https://github.com/joy7758/verifiable-tool-invocation-flow
- Core PyPI package: https://pypi.org/project/verifiable-tool-invocation-flow/0.1.1/
- GitHub Marketplace Action: https://github.com/marketplace/actions/verify-agent-execution-receipt
- Hugging Face Space demo: https://huggingface.co/spaces/joy7759/agent-receipt-validator
- MCP server repository: https://github.com/joy7758/agent-receipt-validator-mcp
- MCP server PyPI package: https://pypi.org/project/agent-receipt-validator-mcp/0.1.1/
- Landing note: docs/public_landing_note.md

What it does:

- records evidence for one sensitive tool invocation
- signs an execution receipt with Ed25519
- independently validates receipt schema, hashes, policy alignment, signature, audience binding, request binding, time window, and optional replay indicators
- provides CI and MCP surfaces for reuse

Scope boundaries:

- does not prove semantic correctness of tool output
- does not prove the policy itself is correct
- does not protect against a compromised signer
- does not replace sandboxing, IAM, monitoring, human approval, or legal compliance review
- does not require or expose raw chain-of-thought
- is not a full FDO, Gaia-X, IDS, or EDC implementation

## Hugging Face Space description

This Space demonstrates independent validation of signed AI agent execution receipts against evidence bundles.

Start with the built-in demo first. If you upload your own files, upload only receipt JSON, evidence bundle JSON, and a public key PEM that are safe to share with this Space.

Do not upload private keys, API tokens, production receipts, confidential evidence bundles, or sensitive data.

Related links:

- Core repo: https://github.com/joy7758/verifiable-tool-invocation-flow
- Core PyPI package: https://pypi.org/project/verifiable-tool-invocation-flow/0.1.1/
- GitHub Action: https://github.com/marketplace/actions/verify-agent-execution-receipt
- MCP server package: https://pypi.org/project/agent-receipt-validator-mcp/0.1.1/
- MCP server repo: https://github.com/joy7758/agent-receipt-validator-mcp

## LinkedIn / X short post

### Short version under 700 characters

I published Agent Receipt Validator Ecosystem v0.1: a small open-source toolkit for signed execution receipts and independent validation of sensitive AI agent tool calls.

It includes a CrewAI Flow template, Python package, GitHub Action, Hugging Face demo, and MCP server.

GitHub: https://github.com/joy7758/verifiable-tool-invocation-flow
Demo: https://huggingface.co/spaces/joy7759/agent-receipt-validator

### Longer version under 1,500 characters

I published Agent Receipt Validator Ecosystem v0.1.

It is a small open-source toolkit for generating, signing, and independently validating execution receipts for sensitive AI agent tool calls.

The idea is simple: one tool invocation becomes an evidence bundle, a signed execution receipt, and a verification report that can be checked outside the original agent runtime.

Public assets include:

- CrewAI Flow template
- Core Python package on PyPI
- GitHub Action for CI receipt verification
- Hugging Face visual demo
- MCP server package for local MCP-compatible clients

Main repo: https://github.com/joy7758/verifiable-tool-invocation-flow
Demo: https://huggingface.co/spaces/joy7759/agent-receipt-validator
MCP server: https://pypi.org/project/agent-receipt-validator-mcp/0.1.1/

Scope boundary: this validates signed execution evidence. It does not prove semantic correctness of tool output, replace sandboxing or access control, or certify legal compliance.

## Email intro to potential collaborators

Subject: Open-source toolkit for signed AI agent execution receipts

Hi [Name],

I wanted to share a small open-source project that may be relevant to your work on AI governance, data spaces, agent frameworks, or security engineering.

Agent Receipt Validator Ecosystem v0.1 provides a minimal pattern for generating, signing, and independently validating execution receipts for sensitive AI agent tool calls. One tool invocation becomes an evidence bundle, a signed execution receipt, and a verification report that can be checked outside the original agent runtime.

Public links:

- Core repo and CrewAI Flow template: https://github.com/joy7758/verifiable-tool-invocation-flow
- Core PyPI package: https://pypi.org/project/verifiable-tool-invocation-flow/0.1.1/
- GitHub Action: https://github.com/marketplace/actions/verify-agent-execution-receipt
- Hugging Face demo: https://huggingface.co/spaces/joy7759/agent-receipt-validator
- MCP server repo: https://github.com/joy7758/agent-receipt-validator-mcp
- MCP server package: https://pypi.org/project/agent-receipt-validator-mcp/0.1.1/
- Landing note: https://github.com/joy7758/verifiable-tool-invocation-flow/blob/main/docs/public_landing_note.md

The project is intentionally narrow. It validates signed execution evidence; it does not prove semantic correctness, replace sandboxing or access control, or certify legal compliance.

I would appreciate feedback on the receipt profile, validator rules, and what should remain out of scope.

Best,
[Your Name]

## Research artifact description

Artifact name: Agent Receipt Validator Ecosystem v0.1

This artifact provides an open-source implementation of a minimal receipt and validator pattern for sensitive AI agent tool calls. It includes a reusable Python package, a CrewAI Flow template, a GitHub Action for CI-based receipt verification, a Hugging Face Space for visual validation, and an MCP server package for local MCP-compatible clients.

Reproducibility notes:

- The default demo requires no LLM API key.
- The core repository includes deterministic examples and tests.
- The validator can run independently against an execution receipt, evidence bundle, public key PEM, and expected audience.
- The GitHub Action can be used to verify receipt artifacts in CI.
- The MCP server exposes local stdio validation tools for MCP-compatible clients.

Boundary conditions:

- The artifact validates signed execution evidence for tool invocations.
- It does not prove semantic correctness of tool outputs.
- It does not prove that the policy itself is correct.
- It does not protect against a compromised signer.
- It does not replace sandboxing, IAM, access control, monitoring, human approval, or legal compliance review.
- It is not a full FDO, Gaia-X, IDS, or EDC implementation.

Landing note: https://github.com/joy7758/verifiable-tool-invocation-flow/blob/main/docs/public_landing_note.md

## Suggested title options

- Technical: Signed Execution Receipts and Independent Validation for AI Agent Tool Calls
- Research-oriented: Portable Evidence Records for Auditable AI Agent Tool Execution
- Marketplace-oriented: Verify Agent Execution Receipts in CI and Local MCP Clients
- Short: Agent Receipt Validator
- FDO/data-space oriented: FDO-Inspired Execution Evidence for Agentic Data Operations

## Suggested next feedback questions

- Are the receipt fields minimal enough?
- Should policy snapshot references include issuer?
- Should replay detection be mandatory?
- Which validator rules should be profile-level requirements?
- How should FDO/Data-Space identifiers be represented?
- Should the MCP server expose receipt building or validation only?
- What should remain out of scope?
- What evidence is needed for third-party audit?
