# FDO / Data Space Mapping

This template provides an FDO/Data-Space-like mapping for demonstration only. It is not a full implementation of FDO, Gaia-X, IDS, or EDC.

## Field mapping

| Template field | Demonstration mapping |
| --- | --- |
| `resource_id` | FDO PID-like object identifier |
| `policy_id` / `policy_version` | Usage policy snapshot |
| `agent_id` | Accountable execution subject |
| `tool_id` | Controlled operation capability |
| `execution_id` | Specific operation instance |
| `execution_receipt` | Portable operation evidence |
| `verification_report` | Audit verification result |

## Why this mapping exists

The demo resource identifier and policy metadata are structured so they can be explained in data-space terms:

- a resource is identified
- an operation is requested
- a policy snapshot constrains the operation
- evidence is captured for one execution instance
- a validator checks the evidence later

## What this repository does not claim

It does not claim:

- full FDO registry behavior
- Gaia-X compliance
- IDS protocol compatibility
- EDC connector integration
- interoperable trust-fabric deployment

The mapping is descriptive only. It is intended to help reviewers understand how a signed execution receipt could fit into broader accountable data-operation workflows.
