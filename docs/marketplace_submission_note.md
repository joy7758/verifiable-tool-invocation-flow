# Marketplace Submission Note

## Project name

Secure & Verifiable Tool Invocation Flow

## Repository name

verifiable-tool-invocation-flow

## Repository URL placeholder

https://github.com/joy7758/verifiable-tool-invocation-flow

## Short description

A reusable CrewAI Flow template for wrapping sensitive agent tool calls with signed execution receipts and independent validation reports.

## Long description

This template demonstrates how a CrewAI Flow can wrap a sensitive agent tool invocation with verifiable execution evidence. It captures a pre-execution commitment, policy snapshot hash, tool manifest hash, tool-call evidence, result hash, nonce, audience, expiration time, and Ed25519 signature. The template also includes an independent validator that checks schema validity, hashes, policy alignment, signature validity, replay indicators, audience binding, and request binding.

## Categories

- Security
- Governance
- Compliance
- Tooling
- Data Operations

## Submission checklist

- Public GitHub repository or private access granted to `crewAIEngineering`.
- README complete.
- Tests pass.
- Flow runnable.
- No private keys committed.
- No `.env` committed.
- No `outputs/` artifacts committed except `outputs/.gitkeep`.
- Python requirement documented as `>=3.10,<3.14`.
- The default demo requires no LLM API key.
