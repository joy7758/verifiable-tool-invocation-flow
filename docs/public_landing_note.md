# Agent Receipt Validator Ecosystem

## One-line summary

A small open-source toolkit for generating, signing, and independently validating execution receipts for sensitive AI agent tool calls.

## What problem it addresses

AI agents increasingly call tools, APIs, and data systems. After an agent acts, teams often need evidence of:

- what request was made
- which policy snapshot applied
- which tool was used
- what result was produced
- whether the evidence was later changed
- whether an independent verifier can check the record

This project provides a minimal receipt and validator pattern for that problem.

## Core idea

The system turns one sensitive tool invocation into:

- an evidence bundle
- a signed execution receipt
- a verification report

```text
Execution request
  -> policy snapshot
  -> tool manifest
  -> guarded tool call
  -> evidence bundle
  -> signed execution receipt
  -> independent validator
  -> verification report
```

## Public assets

| Asset | Link | Purpose |
|---|---|---|
| CrewAI Flow template | https://github.com/joy7758/verifiable-tool-invocation-flow | runnable workflow template |
| Core PyPI package | https://pypi.org/project/verifiable-tool-invocation-flow/0.1.1/ | Python receipt and validator toolkit |
| GitHub Marketplace Action | https://github.com/marketplace/actions/verify-agent-execution-receipt | CI receipt verification |
| Hugging Face Space | https://huggingface.co/spaces/joy7759/agent-receipt-validator | visual demo |
| MCP server repo | https://github.com/joy7758/agent-receipt-validator-mcp | local MCP server source |
| MCP server PyPI package | https://pypi.org/project/agent-receipt-validator-mcp/0.1.1/ | MCP-compatible receipt validation tools |

## Quick ways to try it

### 1. Visual demo

Use:

https://huggingface.co/spaces/joy7759/agent-receipt-validator

Use the built-in demo first. Do not upload private keys, production receipts, confidential evidence bundles, API tokens, or sensitive data.

### 2. Python package

```bash
pip install verifiable-tool-invocation-flow==0.1.1
python -m verifiable_tool_invocation_flow.main
```

### 3. GitHub Action

```yaml
- uses: joy7758/verify-agent-receipt-action@v0.1.0
  with:
    receipt: outputs/execution_receipt.json
    evidence: outputs/evidence_bundle.json
    public-key: outputs/demo_public_key.pem
    audience: demo-validator
```

### 4. MCP server

```bash
pip install agent-receipt-validator-mcp==0.1.1
```

```json
{
  "mcpServers": {
    "agent-receipt-validator": {
      "command": "agent-receipt-validator-mcp",
      "args": []
    }
  }
}
```

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

## What it does not verify

This project provides verifiable execution evidence for tool invocations.
It does not prove semantic correctness of the tool output.
It does not prove that the policy itself is correct.
It does not protect against a compromised signer.
It does not replace sandboxing, IAM, access control, monitoring, human approval, or legal compliance review.
It does not require or expose raw chain-of-thought.
It is not a full FDO, Gaia-X, IDS, or EDC implementation.

## FDO / Data Space relevance

This project uses FDO/Data-Space-like concepts as a research mapping:

- `resource_id` as a PID-like object identifier
- `policy_id` and `policy_version` as usage policy snapshot references
- `agent_id` as accountable execution subject
- `tool_id` as controlled operation capability
- `execution_receipt` as portable operation evidence
- `verification_report` as audit verification result

This is a demonstration mapping, not a full implementation of FDO, Gaia-X, IDS, or EDC.

## Who may find it useful

- agent workflow developers
- AI governance researchers
- data space / FDO researchers
- teams building audit trails for tool-calling agents
- teams testing CI gates for agent-generated evidence
- researchers preparing reproducible agent-execution artifacts

## Support and collaboration

- [SUPPORT.md](../SUPPORT.md)
- [COMMERCIAL_SUPPORT.md](../COMMERCIAL_SUPPORT.md)

Commercial and research collaboration may include:

- private validator integration
- receipt profile adaptation
- CI/CD receipt verification
- CrewAI workflow integration
- MCP tool integration
- FDO/Data-Space-like evidence mapping
- research artifact preparation

## Suggested citation / reference text

Agent Receipt Validator Ecosystem. An open-source toolkit for signed execution receipts and independent validation of sensitive AI agent tool calls. Available at: [https://github.com/joy7758/verifiable-tool-invocation-flow](https://github.com/joy7758/verifiable-tool-invocation-flow)
