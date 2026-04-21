# Feedback Tracking: Agent Receipt Validator Ecosystem v0.1

## Purpose

This document tracks planned public posts, feedback received, and follow-up decisions for the Agent Receipt Validator ecosystem. The goal is to collect external feedback before expanding the project into new platforms, standards, or profile versions.

## Current project state

The current v0.1 ecosystem includes:

- CrewAI Flow template
- Core Python package
- GitHub Marketplace Action
- Hugging Face Space demo
- MCP server package
- Support / commercial integration pages
- Landing note
- Announcement pack

No new engineering platform should be added until feedback has been reviewed.

## Primary feedback objective

The main objective is to evaluate whether the current execution receipt profile and validator rule set are minimal, understandable, and useful for accountable AI agent tool invocation.

## Key feedback questions

1. Are the receipt fields minimal enough?
2. Are any fields missing for third-party verification?
3. Should policy snapshot references include issuer, timestamp, or trust anchor metadata?
4. Should replay detection be mandatory or optional?
5. Which validator rules should be profile-level requirements?
6. Should tool manifests be treated as evidence, policy, or both?
7. How should FDO/Data-Space identifiers be represented?
8. Should the MCP server expose receipt building, validation only, or both?
9. What should remain explicitly out of scope?
10. What evidence is needed for practical third-party audit?
11. Does the GitHub Action fit CI/CD use cases?
12. Is the Hugging Face demo clear enough for first-time users?

## Posting channels

| Channel | Priority | Purpose | Draft source | Status | Planned date | Posted link |
|---|---:|---|---|---|---|---|
| CrewAI Forum | 1 | Flow template and agent workflow feedback | docs/announcement_pack.md - CrewAI forum version | planned | TBD | TBD |
| LangChain Forum | 2 | Tool-calling agent evidence feedback | docs/announcement_pack.md - LangChain forum version | planned | TBD | TBD |
| GitHub repo announcement | 3 | Developer-facing project announcement | docs/announcement_pack.md - GitHub release announcement | planned | TBD | TBD |
| Hugging Face Space community/update | 4 | Demo-facing introduction | docs/announcement_pack.md - Hugging Face Space description | planned | TBD | TBD |
| LinkedIn / X | 5 | Short public summary | docs/announcement_pack.md - LinkedIn / X short post | optional | TBD | TBD |
| Direct email to researchers | 6 | Targeted research feedback | docs/announcement_pack.md - Email intro | optional | TBD | TBD |

## Recommended posting order

1. CrewAI Forum
2. LangChain / tool-calling agent community
3. GitHub announcement
4. Hugging Face Space update
5. Direct emails to selected researchers or maintainers
6. LinkedIn / X only after the technical posts are live

The first posts should target technical feedback rather than promotion.

## Draft: CrewAI Forum post

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

## Draft: LangChain / tool-calling agent post

I have published a small open-source receipt and validator toolkit for tool-calling agents.

The problem is framework-neutral: after an agent calls a tool, API, or data system, a team may need a portable record of what request was made, which policy snapshot applied, which tool was used, what input and output were recorded, and whether an independent verifier can detect later changes.

The project produces:

- an evidence bundle
- a signed execution receipt
- an independent verification report

The core Python package is framework-independent. The repository includes a CrewAI Flow template as a runnable example, plus a GitHub Action for CI verification and an MCP server for local MCP-compatible clients.

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
- What evidence is needed for practical third-party audit?
- Should the MCP surface expose validation only, or receipt building too?
- What should remain outside the scope of a receipt validator?

Boundary: this provides verifiable execution evidence. It does not prove semantic correctness, replace runtime controls, or guarantee compliance.

## Draft: GitHub announcement

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

## Draft: Direct email

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

## Feedback log

| Date | Channel | Link | Feedback summary | Theme | Severity | Follow-up needed | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | new |

Theme options:

- receipt fields
- validator rules
- policy snapshot
- signature/key management
- replay protection
- FDO/Data-Space mapping
- CI/CD use case
- MCP use case
- documentation clarity
- security boundary
- commercial/support inquiry
- other

Severity options:

- high
- medium
- low
- note

Status options:

- new
- triaged
- accepted
- deferred
- rejected
- implemented

## Profile v0.2 candidate changes

| Candidate change | Source feedback | Rationale | Risk | Decision | Status |
|---|---|---|---|---|---|
| Add policy issuer metadata | TBD | Could make policy snapshot provenance clearer for third-party verification. | Adds schema complexity before demand is validated. | TBD | new |
| Add key issuer / public key discovery metadata | TBD | Could help verifiers understand key origin and discovery path. | May imply infrastructure assumptions that v0.1 intentionally avoids. | TBD | new |
| Clarify replay detection requirements | TBD | Current replay indicator is optional and should be easier to profile. | Making it mandatory may add storage requirements. | TBD | new |
| Separate evidence bundle schema from receipt schema | TBD | Could clarify which data is signed receipt metadata and which data is supporting evidence. | More schemas may make first adoption harder. | TBD | new |
| Add tool manifest issuer / version metadata | TBD | Could improve tool provenance and controlled operation tracking. | Adds fields that may not be available in simple agent workflows. | TBD | new |
| Define minimal FDO/Data-Space field mapping | TBD | Could help researchers compare the artifact to PID, policy, and audit concepts. | Must avoid implying full FDO/Data-Space implementation. | TBD | new |
| Define validator rule severity levels | TBD | Could distinguish hard failures from warnings or profile-specific checks. | Adds interpretation complexity to verification reports. | TBD | new |

## Out-of-scope guardrails

Do not expand the project into a general AI security framework.
Do not claim compliance certification.
Do not claim semantic correctness of tool outputs.
Do not claim tamper resistant execution.
Do not implement KMS/HSM integration before profile requirements are clearer.
Do not implement remote hosted validator before demand is validated.
Do not publish to additional marketplaces before initial feedback is reviewed.

## Decision log

| Date | Decision | Reason | Evidence / feedback source | Impact |
|---|---|---|---|---|
| TBD | Do not expand to new platforms until first feedback cycle is complete | ecosystem already has sufficient public entry points | internal project review | focus on feedback and profile v0.2 |

## Success criteria for feedback round 1

- At least one technical comment on receipt fields
- At least one comment on validator rules
- At least one comment on CI/CD or MCP usability
- At least one comment on FDO/Data-Space mapping or audit evidence
- Clear decision on whether profile v0.2 should change schema, validator rules, or documentation only

## Next action after feedback

After feedback round 1, create a short profile v0.2 planning note before writing new code.
