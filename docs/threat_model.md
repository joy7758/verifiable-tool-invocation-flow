# Threat Model

| Attack | Impact | Current mitigation | Residual risk | Severity |
| --- | --- | --- | --- | --- |
| Post-hoc log tampering | Audit logs can be rewritten after execution | Receipt and evidence hashes can be revalidated independently | Attackers may still tamper with systems outside this template | High |
| Receipt tampering | Receipt fields can be modified to misstate what happened | Ed25519 signature verification and hash recomputation | A compromised signer could still sign false data | High |
| Evidence artifact tampering | Request, policy, input, or output artifacts can be swapped | Validator recomputes `input_hash`, `policy_hash`, `tool_manifest_hash`, `tool_input_hash`, and `tool_output_hash` | If validator receives substituted artifacts plus a matching malicious receipt from a compromised signer, the template cannot detect it | High |
| Policy mismatch | Receipt may claim approval under a different policy snapshot | Validator recomputes policy hash and reevaluates policy from evidence | Incorrect policy content is still possible | Medium |
| Tool manifest mismatch | Receipt may claim a different tool capability boundary | Validator recomputes tool manifest hash and reevaluates allowed operations | Manifest quality still depends on authoring discipline | Medium |
| Replay attack | A valid receipt may be reused to misrepresent multiple executions | Optional replay cache keyed by `execution_id:nonce` | File-based replay cache is demo-level and not shared across systems | Medium |
| Wrong validator audience | Receipt may be replayed to a validator with a different intended audience | Explicit `audience_match` check | Audience strings are only as strong as deployment discipline | Medium |
| Expired receipt | Old receipts may be presented as current | `issued_at` and `expires_at` are checked against `checked_at` | Clock skew and policy choice still matter | Medium |
| Wrong public key | Validator may use the wrong verification key | Signature verification fails | Public-key distribution is outside scope | Medium |
| Compromised signer | An attacker with signing-key access can produce valid-looking receipts | Explicitly documented as out of scope | A compromised signer defeats receipt authenticity | Critical |
| Runtime and validator co-location | Same compromised runtime may control both execution and validation | Validator is designed to run independently from Flow runtime | Operators may still deploy them together | Medium |
| Supply-chain misuse | Dependency or packaging issues may alter behavior | Typed tests, supported Python range, and explicit dependency declaration | This is not a full supply-chain security solution | Medium |
| User misunderstanding of guarantees | Users may over-trust the template as a complete security framework | README and docs state guarantee boundaries and non-goals | Misuse remains possible if boundaries are ignored | Low |
