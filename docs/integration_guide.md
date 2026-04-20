# Integration Guide

## Import the reusable wrapper

```python
from verifiable_tool_invocation_flow import (
    GuardedToolCallVerificationError,
    ReceiptSigner,
    guarded_tool_call,
)
```

## Use a custom tool function

Your tool function should accept a JSON-serializable mapping and return a JSON-serializable mapping.

```python
def my_sensitive_tool(tool_input: dict[str, object]) -> dict[str, object]:
    return {
        "resource_id": tool_input["resource_id"],
        "status": "ok",
    }
```

## Pass a custom policy snapshot

Construct `ExecutionRequest`, `PolicySnapshot`, and `ToolManifest` for your own operation, then call `guarded_tool_call()`:

```python
result = guarded_tool_call(
    request=request,
    policy=policy_snapshot,
    tool_manifest=tool_manifest,
    tool_input=tool_input,
    tool_fn=my_sensitive_tool,
    signer=ReceiptSigner.generate_demo(),
)
```

## Run the validator separately

You can validate the resulting artifacts later and outside the original runtime:

```bash
python -m verifiable_tool_invocation_flow.validator \
  --receipt outputs/execution_receipt.json \
  --evidence outputs/evidence_bundle.json \
  --public-key outputs/demo_public_key.pem \
  --audience demo-validator
```

## Handle verification failures explicitly

`guarded_tool_call()` raises `GuardedToolCallVerificationError` if post-call validation does not return a valid verdict.

```python
try:
    result = guarded_tool_call(
        request=request,
        policy=policy_snapshot,
        tool_manifest=tool_manifest,
        tool_input=tool_input,
        tool_fn=my_sensitive_tool,
        signer=signer,
    )
except GuardedToolCallVerificationError as exc:
    report = exc.verification_report
    raise RuntimeError(f"verification failed: {report['errors']}") from exc
```

## Keep private keys out of the repository

- Do not commit private keys.
- Do not store demo private keys on disk for the default template.
- Load production signing material from your deployment environment and hand it to `ReceiptSigner.from_private_key_pem(...)`.

## Replace the demo signer later

This template intentionally avoids implementing KMS or HSM integration. A practical next step is to replace:

```python
ReceiptSigner.generate_demo()
```

with a signer created from deployment-managed PEM material:

```python
signer = ReceiptSigner.from_private_key_pem(private_key_pem_bytes, public_key_id="prod-key-001")
```

That keeps the core interface stable without pretending this repository already implements production key management.
